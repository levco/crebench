import csv
from decimal import Decimal
from pathlib import Path
import shutil
import tempfile
import unittest

from crebench.grade import grade, read_json, safe_child, verify_case

CASE = Path(__file__).resolve().parents[1] / "cases/public/harbor-court-001"


class GraderTests(unittest.TestCase):
    def setUp(self):
        self.answer = read_json(CASE / "reference-answer.json")

    def failed(self, answer):
        return {r["criterion"] for r in grade(CASE, answer)["criteria"] if not r["pass"]}

    def test_reference_is_only_a_development_check(self):
        result = grade(CASE, self.answer)
        self.assertTrue(result["all_checks_pass"])
        self.assertFalse(result["model_evaluation"])

    def test_key_matches_independent_source_arithmetic(self):
        rows = list(csv.DictReader((CASE / "t12.csv").read_text().splitlines()))
        revenue = sum(Decimal(r["annual_usd"]) for r in rows if r["classification"] in {"operating_revenue", "contra_revenue"})
        expenses = sum(Decimal(r["annual_usd"]) for r in rows if r["classification"] == "operating_expense")
        self.assertEqual(revenue - expenses, 150000)
        self.assertEqual(self.answer["fields"]["noi"]["value"], revenue - expenses)

    def test_key_matches_independent_rent_roll(self):
        rows = list(csv.DictReader((CASE / "rent-roll.csv").read_text().splitlines()))
        active = [r for r in rows if r["status"] == "active"]
        self.assertEqual(len(active), 9)
        self.assertEqual(sum(int(r["area_sf"]) for r in active), 6500)
        self.assertEqual(sum(int(r["monthly_rent_usd"]) * 12 for r in active), 177600)

    def test_pending_counted_as_active_fails_both_dimensions(self):
        self.answer["fields"]["occupied_units"]["value"] = 10
        self.answer["fields"]["occupied_area_sf"]["value"] = 7000
        self.assertTrue({"occupied_units", "occupied_area_sf"} <= self.failed(self.answer))

    def test_false_conflict_is_penalized(self):
        self.answer["discrepancies"].append("historical_revenue_differs_from_current_rent")
        self.assertIn("conflicts.exact_set", self.failed(self.answer))

    def test_missing_conflict_is_penalized(self):
        self.answer["discrepancies"].pop()
        self.assertIn("conflicts.exact_set", self.failed(self.answer))

    def test_unit_type_mistake_is_visible(self):
        self.answer["fields"]["studio_occupied_units"]["value"] = 3
        self.assertIn("studio_occupied_units", self.failed(self.answer))

    def test_wrong_math_fails_even_if_nearby(self):
        self.answer["fields"]["noi"]["value"] = 150001
        self.assertTrue({"noi", "noi.reconciles"} <= self.failed(self.answer))

    def test_max_loan_must_be_the_minimum(self):
        self.answer["fields"]["max_loan"]["value"] = 1714286
        self.assertIn("loan.minimum_constraint", self.failed(self.answer))

    def test_wrong_resolution_fails(self):
        self.answer["fields"]["resolution"]["value"] = "use_reported_summary"
        self.assertIn("resolution", self.failed(self.answer))

    def test_boolean_is_not_a_number(self):
        self.answer["fields"]["pending_units"]["value"] = True
        self.assertIn("pending_units", self.failed(self.answer))

    def test_infinite_value_fails(self):
        self.answer["fields"]["noi"]["value"] = float("inf")
        self.assertIn("noi", self.failed(self.answer))

    def test_fabricated_source_ref_fails(self):
        self.answer["fields"]["noi"]["evidence"] = ["nonexistent.pdf:1"]
        self.assertIn("noi.evidence", self.failed(self.answer))

    def test_malformed_shapes_do_not_crash(self):
        for answer in [None, [], {}, {"fields": [], "discrepancies": []},
                       {"fields": {}, "discrepancies": [{}]}]:
            self.assertFalse(grade(CASE, answer)["all_checks_pass"])

    def test_duplicate_conflicts_fail(self):
        self.answer["discrepancies"] *= 2
        self.assertIn("conflicts.exact_set", self.failed(self.answer))

    def test_unknown_field_fails_contract(self):
        self.answer["fields"]["invented"] = {"value": 7, "evidence": []}
        self.assertIn("output.contract", self.failed(self.answer))

    def test_case_input_drift_aborts(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "case"
            shutil.copytree(CASE, root)
            (root / "t12.csv").write_text("modified\n")
            with self.assertRaisesRegex(ValueError, "integrity mismatch"):
                verify_case(root)

    def test_case_key_drift_aborts(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "case"
            shutil.copytree(CASE, root)
            (root / "answer-key.json").write_text("{}")
            with self.assertRaises(ValueError):
                verify_case(root)

    def test_duplicate_json_and_nan_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "answer.json"
            for value in ['{"x":1,"x":2}', '{"x":NaN}']:
                path.write_text(value)
                with self.assertRaises(ValueError):
                    read_json(path)

    def test_manifest_path_cannot_escape(self):
        with self.assertRaises(ValueError):
            safe_child(CASE, "../private.json")


if __name__ == "__main__":
    unittest.main()
