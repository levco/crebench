"""Run an auditable, small API pilot on the disclosed synthetic case only.

No repair, retry, answer-key access by the model, or model fallback. Credentials
are sent only to the fixed HTTPS endpoint and never written into run artifacts.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.request

from .grade import grade, read_json, safe_child, sha256, verify_case

ENDPOINT = "https://ai-gateway.vercel.sh/v1/chat/completions"
INPUTS = {"t12.csv", "rent-roll.csv", "source-summary.json", "sizing-inputs.json",
          "prompt.md", "output-contract.json"}
MODELS = ["openai/gpt-5.6-sol", "anthropic/claude-sonnet-5", "google/gemini-3.8-flash"]


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write(path, data):
    with Path(path).open("x") as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write("\n")


def packet(case):
    manifest = verify_case(case)
    if manifest["case_id"] != "harbor-court-001" or set(manifest["system_inputs"]) != INPUTS:
        raise ValueError("Pilot is restricted to the original public synthetic case")
    parts = []
    for name in manifest["system_inputs"]:
        if name not in manifest["sha256"]:
            raise ValueError("Every model input must have an integrity hash")
        parts.append(f"<file name=\"{name}\">\n{safe_child(Path(case), name).read_text()}\n</file>")
    return "\n\n".join(parts)


def credential(env_file):
    token = os.environ.get("AI_GATEWAY_API_KEY") or os.environ.get("VERCEL_OIDC_TOKEN")
    if token:
        return token
    if env_file:
        for line in Path(env_file).read_text().splitlines():
            if line.startswith("VERCEL_OIDC_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise ValueError("Missing AI_GATEWAY_API_KEY or VERCEL_OIDC_TOKEN")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError("Authenticated request redirect refused")


def prepare(case, directory, catalog_path):
    content = packet(case)
    catalog = read_json(catalog_path)
    selected = [next(m for m in catalog["data"] if m["id"] == model) for model in MODELS]
    # Deliberately loose text-only cost reservation: byte count as token ceiling,
    # largest standard tier price, then 2x headroom. No paid tools are enabled.
    input_ceiling = len(content.encode()) + 1024
    estimates = {}
    for model in selected:
        prices = model["pricing"]
        rates = {side: max([float(prices[side])] + [float(t["cost"]) for t in prices.get(side+"_tiers", [])])
                 for side in ("input", "output")}
        estimates[model["id"]] = 2 * (input_ceiling * rates["input"] + 8192 * rates["output"])
    reserve = 3 * sum(estimates.values())
    if reserve > 5:
        raise ValueError("Conservative catalog cost reservation exceeds $5 pilot cap")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    write(directory / "catalog.json", {"retrieved_at": now(), "source": "https://ai-gateway.vercel.sh/v1/models", "data": selected})
    plan = {"experiment": directory.name, "created_at": now(), "case_id": "harbor-court-001",
            "track": "public_synthetic_text_api_pilot", "model_evaluation": True,
            "leaderboard_eligible": False, "case_manifest_sha256": sha256(Path(case)/"manifest.json"),
            "grader_sha256": sha256(Path(__file__).with_name("grade.py")),
            "runner_sha256": sha256(__file__), "packet_sha256": hashlib.sha256(content.encode()).hexdigest(),
            "endpoint": ENDPOINT, "models": MODELS, "repetitions": 3, "max_tokens": 8192,
            "temperature": "provider_default", "reasoning": "provider_default",
            "tools": [], "retries": 0, "timeout_seconds": 180,
            "model_fallbacks": [], "provider_routing": "gateway_default_record_response",
            "cost_reservation_usd": reserve, "cost_limit_usd": 5,
            "reservation_by_model_usd": estimates,
            "limitations": ["One public case; answer key already published", "No independent case reviewer",
                            "CSV and JSON supplied as text; no PDF ingestion", "Source references supplied in contract",
                            "Provider defaults and routing may differ; not equal compute", "Aliases may change over time",
                            "No workbook, OM, or Lev product assessment", "Cost reservation is not a provider billing cap"]}
    write(directory/"plan.json", plan)
    for repetition in range(1, 4):
        for index, model in enumerate(MODELS, 1):
            run = directory / f"r{repetition}-{index}"
            run.mkdir()
            write(run/"request.json", {"model": model, "messages": [{"role": "user", "content": content}],
                                       "max_tokens": 8192, "stream": False})
    return plan


def execute(case, directory, env_file):
    directory = Path(directory)
    plan = read_json(directory/"plan.json")
    if sha256(__file__) != plan["runner_sha256"] or sha256(Path(__file__).with_name("grade.py")) != plan["grader_sha256"]:
        raise ValueError("Runner or grader changed after plan freeze")
    if sha256(Path(case)/"manifest.json") != plan["case_manifest_sha256"]:
        raise ValueError("Case manifest changed after plan freeze")
    content = packet(case)
    if hashlib.sha256(content.encode()).hexdigest() != plan["packet_sha256"]:
        raise ValueError("Packet changed after plan freeze")
    token = credential(env_file)
    opener = urllib.request.build_opener(NoRedirect())
    # A request is reserved before network I/O. Interrupted attempts are never retried.
    for repetition in range(1, plan["repetitions"]+1):
        for index, model in enumerate(plan["models"], 1):
            run = directory / f"r{repetition}-{index}"
            if (run/"started.json").exists():
                continue
            request = read_json(run/"request.json")
            expected = {"model": model, "messages": [{"role": "user", "content": content}],
                        "max_tokens": plan["max_tokens"], "stream": False}
            if request != expected:
                raise ValueError("Request differs from frozen protocol")
            write(run/"started.json", {"at": now(), "request_sha256": sha256(run/"request.json"),
                                       "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()})
            started = time.monotonic()
            record = {"model_evaluation": True, "leaderboard_eligible": False, "requested_model": model,
                      "repetition": repetition, "status": "infrastructure_error", "grade": None}
            try:
                req = urllib.request.Request(ENDPOINT, data=json.dumps(request).encode(),
                                             headers={"Content-Type": "application/json", "Authorization": "Bearer "+token})
                with opener.open(req, timeout=plan["timeout_seconds"]) as response:
                    raw = response.read()
                    record["http_status"] = response.status
                # Redact exact credential defensively before retaining any server text.
                text = raw.decode().replace(token, "[REDACTED]")
                (run/"response.json").write_text(text)
                result = read_json(run/"response.json")
                record["returned_model"] = result.get("model")
                record["usage"] = result.get("usage")
                choices = result.get("choices", [])
                choice = choices[0] if choices else {}
                record["finish_reason"] = choice.get("finish_reason")
                answer = choice.get("message", {}).get("content")
                if isinstance(answer, str):
                    (run/"answer.txt").write_text(answer)
                    try:
                        parsed = read_json(run/"answer.txt")
                        record["grade"] = grade(case, parsed)
                        record["grade"]["model_evaluation"] = True
                        record["grade"]["result_type"] = "public_synthetic_model_pilot"
                        record["status"] = "scored"
                    except (ValueError, TypeError):
                        record["status"] = "invalid_json"
                else:
                    record["status"] = "no_answer"
                if choice.get("finish_reason") == "length":
                    record["status"] = "output_limit"
            except urllib.error.HTTPError as exc:
                record["http_status"] = exc.code
                record["error"] = exc.read().decode(errors="replace").replace(token, "[REDACTED]")
            except (urllib.error.URLError, TimeoutError, ValueError) as exc:
                record["error"] = str(exc).replace(token, "[REDACTED]")
            record["elapsed_seconds"] = round(time.monotonic()-started, 3)
            record["completed_at"] = now()
            record["sha256"] = {p.name: sha256(p) for p in run.iterdir() if p.is_file()}
            write(run/"result.json", record)
            print(json.dumps({"run": run.name, "model": model, "status": record["status"],
                              "passed": record["grade"]["passed"] if record["grade"] else None,
                              "seconds": record["elapsed_seconds"], "http_status": record.get("http_status")}), flush=True)
            if record.get("http_status") in (401, 402, 403):
                print("Stopped on authentication/billing/access gate; no remaining requests sent.", flush=True)
                return


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "execute"])
    parser.add_argument("directory")
    parser.add_argument("--case", default="cases/public/harbor-court-001")
    parser.add_argument("--catalog", default="work/gateway-models.json")
    parser.add_argument("--env-file")
    args = parser.parse_args()
    if args.action == "prepare":
        plan = prepare(args.case, args.directory, args.catalog)
        print(json.dumps({"prepared": args.directory, "calls": 9, "reserved_usd": plan["cost_reservation_usd"]}))
    else:
        execute(args.case, args.directory, args.env_file)


if __name__ == "__main__":
    main()
