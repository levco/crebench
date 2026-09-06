import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

from . import __version__
from .grade import grade, read_json, sha256, verify_case


def main():
    parser = argparse.ArgumentParser(description="Inspect and grade public CRE Bench development examples")
    sub = parser.add_subparsers(dest="command", required=True)
    verify = sub.add_parser("verify", help="Verify frozen public example hashes")
    verify.add_argument("case", type=Path)
    scoring = sub.add_parser("grade", help="Grade a saved JSON answer; does not call a model")
    scoring.add_argument("case", type=Path)
    scoring.add_argument("answer", type=Path)
    scoring.add_argument("--record", type=Path, help="Write a new immutable local grade record")
    args = parser.parse_args()
    try:
        if args.command == "verify":
            manifest = verify_case(args.case)
            print(json.dumps({"case_id": manifest["case_id"], "verified_files": len(manifest["sha256"])}))
            return 0
        # A corrupt case is infrastructure failure; an invalid answer is a recorded output failure.
        verify_case(args.case)
        try:
            answer = read_json(args.answer)
            result = grade(args.case, answer)
        except (json.JSONDecodeError, ValueError) as error:
            result = {"result_type": "development_example_check", "model_evaluation": False,
                      "all_checks_pass": False, "status": "invalid_output", "error": str(error)}
        result["provenance"] = {"tool_version": __version__, "created_at": datetime.now(timezone.utc).isoformat(),
                                "answer_sha256": sha256(args.answer),
                                "manifest_sha256": sha256(args.case / "manifest.json"),
                                "grader_sha256": sha256(Path(__file__).with_name("grade.py"))}
        content = json.dumps(result, indent=2, allow_nan=False) + "\n"
        if args.record:
            with args.record.open("x") as stream:
                stream.write(content)
        print(content)
        return 0 if result["all_checks_pass"] else 1
    except (OSError, ValueError, KeyError) as error:
        print(f"Cannot grade: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
