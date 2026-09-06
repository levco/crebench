"""Deterministic checks for the public, fully disclosed development example.

This grades values and declared source locations. It does not judge natural
language explanations, run a model, or establish professional usability.
"""

from decimal import Decimal, InvalidOperation
from pathlib import Path
import hashlib
import json


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    def reject_constant(value):
        raise ValueError(f"Non-finite JSON number: {value}")

    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    return json.loads(Path(path).read_text(), parse_constant=reject_constant,
                      object_pairs_hook=unique_pairs)


def safe_child(root, name):
    path = Path(name)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("Case path must stay inside the case directory")
    target = (root / path).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError("Case path resolves outside the case directory")
    return target


def verify_case(case):
    case = Path(case)
    manifest = read_json(case / "manifest.json")
    if manifest["split"] != "public" or manifest["status"] != "development_example":
        raise ValueError("This initial grader only supports public development cases")
    for name, digest in manifest["sha256"].items():
        if sha256(safe_child(case, name)) != digest:
            raise ValueError(f"Case integrity mismatch: {name}")
    if not {"answer-key.json", "prompt.md"}.issubset(manifest["sha256"]):
        raise ValueError("Manifest must bind prompt and answer key")
    return manifest


def numeric(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Expected a JSON number")
    result = Decimal(str(value))
    if not result.is_finite():
        raise ValueError("Expected a finite number")
    return result


def value_matches(actual, criterion):
    expected = criterion["value"]
    if isinstance(expected, (float, int)) and not isinstance(expected, bool):
        try:
            return abs(numeric(actual) - numeric(expected)) <= Decimal(str(criterion["tolerance"]))
        except (ValueError, InvalidOperation):
            return False
    return type(actual) is type(expected) and actual == expected


def grade(case, answer):
    manifest = verify_case(case)
    key = read_json(Path(case) / "answer-key.json")
    rows = []

    def record(criterion, passed, kind, material=True):
        rows.append({"criterion": criterion, "pass": bool(passed),
                     "kind": kind, "material": material})

    valid_root = isinstance(answer, dict)
    fields = answer.get("fields", {}) if valid_root else {}
    if not isinstance(fields, dict):
        fields = {}
    record("output.contract", valid_root and set(answer) == {"fields", "discrepancies"}
           and set(fields) == set(key["fields"]), "format", False)
    for name, criterion in key["fields"].items():
        item = fields.get(name)
        valid = isinstance(item, dict) and set(item) == {"value", "evidence"}
        record(name, valid and value_matches(item.get("value"), criterion), "accuracy")
        evidence = item.get("evidence") if valid else None
        # Public contract requires the complete, canonical set of source refs.
        matches = isinstance(evidence, list) and all(isinstance(x, str) for x in evidence)
        matches = matches and len(evidence) == len(set(evidence)) and set(evidence) == set(criterion["evidence"])
        record(name + ".evidence", matches, "source_reference", False)

    actual_conflicts = answer.get("discrepancies") if valid_root else None
    record("conflicts.exact_set", isinstance(actual_conflicts, list)
           and all(isinstance(x, str) for x in actual_conflicts)
           and len(actual_conflicts) == len(set(actual_conflicts))
           and set(actual_conflicts) == set(key["discrepancies"]), "conflict")

    def number(name):
        return numeric(fields[name]["value"])

    try:
        reconciles = abs(number("noi") - (number("operating_revenue") - number("operating_expenses"))) <= Decimal("0.01")
    except (KeyError, TypeError, ValueError, InvalidOperation):
        reconciles = False
    record("noi.reconciles", reconciles, "calculation")
    try:
        constraints = [number("ltv_limit"), number("dscr_limit"), number("debt_yield_limit")]
        sizing_consistent = abs(number("max_loan") - min(constraints)) <= Decimal("1")
    except (KeyError, TypeError, ValueError, InvalidOperation):
        sizing_consistent = False
    record("loan.minimum_constraint", sizing_consistent, "calculation")
    passed = sum(row["pass"] for row in rows)
    return {"case_id": manifest["case_id"], "split": "public",
            "result_type": "development_example_check", "model_evaluation": False,
            "passed": passed, "total": len(rows),
            "material_errors": sum(not r["pass"] for r in rows if r["material"]),
            "all_checks_pass": passed == len(rows), "criteria": rows,
            "limitations": ["Public answer key; not held out", "No expert qualification yet",
                            "Checks declared source refs, not prose reasoning", "No artifact usability assessment"]}
