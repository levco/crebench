# Harbor Court: extraction, reconciliation and sizing

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
