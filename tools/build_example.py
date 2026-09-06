"""Generate an original synthetic public fixture. Never a model baseline.

The key uses explicitly specified answers, not answers derived by the grader.
Independent practitioner qualification is still pending.
"""

from pathlib import Path
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "cases/public/harbor-court-001"
CASE.mkdir(parents=True, exist_ok=True)


def write_json(name, obj):
    (CASE / name).write_text(json.dumps(obj, indent=2) + "\n")


def write_csv(name, rows):
    with (CASE / name).open("w", newline="") as f:
        csv.writer(f, lineterminator="\n").writerows(rows)


write_csv("t12.csv", [
    ["account", "classification", "annual_usd"],
    ["Rental income", "operating_revenue", 240000],
    ["Rent abatements", "contra_revenue", -6000],
    ["Expense reimbursements", "operating_revenue", 12000],
    ["Property taxes", "operating_expense", 30000],
    ["Insurance", "operating_expense", 12000],
    ["Repairs", "operating_expense", 18000],
    ["Utilities", "operating_expense", 24000],
    ["Management", "operating_expense", 12000],
    ["Roof replacement", "capital_expenditure", 40000],
    ["Debt service", "financing", 90000],
])
write_csv("rent-roll.csv", [
    ["unit", "unit_type", "area_sf", "status", "commencement", "monthly_rent_usd"],
    ["101", "studio", 500, "active", "2024-01-01", 1200],
    ["102", "studio", 500, "active", "2024-06-01", 1200],
    ["103", "studio", 500, "vacant", "", ""],
    ["104", "studio", 500, "pending", "2026-02-01", 1200],
    ["201", "1br", 700, "active", "2024-01-01", 1600],
    ["202", "1br", 700, "active", "2024-01-01", 1600],
    ["203", "1br", 700, "active", "2024-01-01", 1600],
    ["204", "1br", 700, "active", "2024-01-01", 1600],
    ["301", "2br", 900, "active", "2024-01-01", 2000],
    ["302", "2br", 900, "active", "2024-01-01", 2000],
    ["303", "2br", 900, "active", "2024-01-01", 2000],
    ["304", "2br", 900, "vacant", "", ""],
])
write_json("source-summary.json", {"reported_occupied_units": 10, "reported_occupied_area_sf": 7000,
                                   "reported_annual_in_place_rent": 192000,
                                   "note": "The preparer's occupied total includes the signed pending lease."})
write_json("sizing-inputs.json", {"property": "Harbor Court (fictional)", "as_of": "2025-12-31",
                                 "t12_period": "2025-01-01 through 2025-12-31", "valuation": 2400000,
                                 "max_ltv": 0.65, "min_dscr": 1.25, "min_debt_yield": 0.09,
                                 "annual_interest_rate": 0.07, "debt_service_method": "interest_only"})

fields = {}


def field(name, value, evidence, tolerance=0):
    fields[name] = {"value": value, "evidence": evidence, "tolerance": tolerance}


rev = ["t12.csv:2-4"]
exp = ["t12.csv:5-9"]
rr = ["rent-roll.csv:2-13"]
field("operating_revenue", 246000, rev, 0.01)
field("operating_expenses", 96000, exp, 0.01)
field("noi", 150000, rev + exp, 0.01)
field("total_units", 12, rr)
field("occupied_units", 9, rr)
field("vacant_units", 2, rr)
field("pending_units", 1, rr)
field("total_area_sf", 8400, rr)
field("occupied_area_sf", 6500, rr)
field("unit_occupancy_pct", 75, rr, 0.01)
field("area_occupancy_pct", 77.38, rr, 0.01)
field("annual_in_place_rent", 177600, rr, 0.01)
for kind, count in [("studio", 2), ("1br", 4), ("2br", 3)]:
    field(kind + "_total_units", 4, rr)
    field(kind + "_occupied_units", count, rr)
field("reported_occupied_units", 10, ["source-summary.json:/reported_occupied_units"])
field("reported_occupied_area_sf", 7000, ["source-summary.json:/reported_occupied_area_sf"])
field("reported_annual_in_place_rent", 192000, ["source-summary.json:/reported_annual_in_place_rent"], 0.01)
field("ltv_limit", 1560000, ["sizing-inputs.json:/valuation", "sizing-inputs.json:/max_ltv"], 1)
field("dscr_limit", 1714286, rev + exp + ["sizing-inputs.json:/min_dscr", "sizing-inputs.json:/annual_interest_rate"], 1)
field("debt_yield_limit", 1666667, rev + exp + ["sizing-inputs.json:/min_debt_yield"], 1)
field("max_loan", 1560000, rev + exp + ["sizing-inputs.json:/valuation", "sizing-inputs.json:/max_ltv",
      "sizing-inputs.json:/min_dscr", "sizing-inputs.json:/annual_interest_rate", "sizing-inputs.json:/min_debt_yield"], 1)
field("binding_constraint", "ltv", fields["max_loan"]["evidence"])
field("resolution", "exclude_pending_from_in_place", rr + ["sizing-inputs.json:/as_of", "source-summary.json:/note"])
conflicts = ["pending_in_reported_occupied_units", "pending_in_reported_occupied_area", "pending_in_reported_rent"]
write_json("answer-key.json", {"status": "public_unqualified_example", "independent_reviewer": None,
                              "fields": fields, "discrepancies": conflicts})
write_json("reference-answer.json", {"fields": {k: {"value": v["value"], "evidence": v["evidence"]} for k, v in fields.items()},
                                   "discrepancies": conflicts})
(CASE / "prompt.md").write_text('''# Harbor Court: extraction, reconciliation and sizing

This is a fictional public development example. It is not a held-out evaluation.
Use t12.csv, rent-roll.csv, source-summary.json and sizing-inputs.json only.
Prepare answer.json using the fields and canonical source references in output-contract.json.

Calculate operating revenue including abatements and reimbursements. Calculate
operating expenses excluding capital expenditure and debt service. NOI equals the difference.
Distinguish active, pending and vacant units at the as-of date. In-place occupancy
and rent exclude pending leases. Report unit and area occupancy independently.
Provide total and occupied counts for each unit type. Preserve the source-reported
summary separately. Report every identified conflict and select the supported resolution.
T-12 rental income is historical and need not equal annualized rent at the as-of date.

Size an interest-only loan: LTV limit = value × max LTV; DSCR limit = NOI ÷
(min DSCR × annual interest rate); debt-yield limit = NOI ÷ minimum debt yield.
Maximum proceeds is the minimum; name the binding constraint. Dollars for loan
limits round to the nearest dollar; occupancy percentages to two decimals.

Output JSON with exactly fields and discrepancies. Each field contains value and
evidence (a unique list of canonical source references). Use numbers as JSON numbers.
discrepancies is a unique list of supported conflict IDs in the contract; do not invent conflicts.
The resolution enum records the selected action; it does not prove prose reasoning.
Do not read answer-key.json or reference-answer.json if using this as practice.
These keys are public, so this packet is never eligible for hidden-set performance claims.
''')
write_json("output-contract.json", {"fields": {k: {"type": "number" if isinstance(v["value"], (int, float)) else "string",
                                                "canonical_evidence": v["evidence"]} for k, v in fields.items()},
                                    "conflict_ids": conflicts + ["historical_revenue_differs_from_current_rent"],
                                    "resolution_values": ["exclude_pending_from_in_place", "use_reported_summary"]})
inputs = ["t12.csv", "rent-roll.csv", "source-summary.json", "sizing-inputs.json", "prompt.md", "output-contract.json"]
write_json("manifest.json", {"case_id": "harbor-court-001", "deal_cluster": "synthetic-harbor-court-001",
                            "split": "public", "status": "development_example", "version": "0.1.0",
                            "provenance": "Original fictional example authored for Lev; no customer data",
                            "license": "MIT", "independent_reviewer": None, "system_inputs": inputs,
                            "sha256": {n: hashlib.sha256((CASE / n).read_bytes()).hexdigest() for n in inputs + ["answer-key.json"]}})
print(f"Built original public example with {len(fields)} fields")
