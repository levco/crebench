# Meadow Commerce: prepare a refinance analysis

You are the CRE analyst preparing a financing package for internal review. Analyze the attached files as of August 31, 2026. All property, borrower, tenant, address and lender details are fictional. Use only this packet; do not research, geocode, invent comps or contact anyone.

Deliver four work products in this fresh workflow:

1. An extraction and financial analysis with source locations, showing historical T12, current contractual rent/occupancy and the supplied underwriting scenario separately. Reconcile authoritative documents and disclose unresolved evidence. Report the fields below in an easily readable table or structured appendix, using these field IDs where practical. JSON formatting is optional. Correct unambiguous financial content matters, not a particular serialization.
2. Loan sizing under each of the three constraints, the binding maximum, actual first-year versus sizing debt service, net cash to/from the borrower, and the specified downside. Follow this lender's definitions exactly. Unknown facts must remain unknown; explicitly permitted provisional assumptions can support conditional calculations.
3. A downloadable XLSX underwriting workbook with editable assumptions, live formulas, historical/underwritten separation, loan sizing, sources/uses and sensitivity outputs. A reviewer must be able to change cap rate, sizing rate and EGI and obtain correct recalculated results. Include a clear location map for these inputs and the loan/NOI/value outputs. Do not deliver only code or a table in place of the workbook.
4. A concise, polished financing memorandum, delivered as a PDF or native memo with PDF export. Include the financing decision, accurate key figures and period labels, tenant/lease discussion, assumptions, limitations, risks and source references. No invented market, sponsor or lender claims. This is an internal-review financing memorandum, not a legal opinion or credit commitment.

If the product requires an outline or generation confirmation, prepare it and request the confirmation. No content changes or corrected answers will be supplied. If a file is missing/unreadable, identify it and continue only where the available evidence permits. Report what you actually delivered and anything blocked.

## Requested analysis fields

Dollar amounts are USD; rates and ratios are decimal unless the ID specifies percent 0-100. Use ISO dates. Cite document/page or worksheet/row and show calculation inputs for derived values.

- `space_count`: unit/suite count.
- `occupied_count`: occupied unit/suite count.
- `total_area_sf`: total rentable square feet.
- `occupied_area_sf`: occupied rentable square feet.
- `occupancy_count_pct`: physical occupancy by count, percent 0-100.
- `occupancy_area_pct`: occupancy by area, percent 0-100.
- `rent_roll_monthly_base`: monthly base rent as printed on the rent roll.
- `effective_monthly_base`: monthly contractual base rent after applying authoritative lease amendments.
- `t12_egi`: historical effective gross income.
- `t12_operating_expenses`: historical operating expense excluding reserves/capex/debt/depreciation.
- `t12_noi_before_reserves`: historical NOI before replacement reserves.
- `t12_reserves`: historical replacement reserves.
- `t12_ncf`: historical NCF after reserves.
- `uw_egi`: underwritten EGI.
- `uw_management_fee`: lender-normalized management fee.
- `uw_operating_expenses`: underwritten operating expense before reserves.
- `uw_noi_before_reserves`: underwritten NOI before reserves.
- `uw_reserves`: underwritten replacement reserves.
- `uw_ncf`: underwritten NCF after reserves.
- `capitalization_value`: indicative value from underwritten NOI before reserves and specified cap rate.
- `contract_rate`: current contractual annual rate, decimal.
- `sizing_rate`: annual underwriting rate, decimal.
- `annual_debt_constant`: annual debt service per dollar of principal using sizing rate and monthly amortization.
- `ltv_limit`: maximum principal under LTV.
- `dscr_limit`: maximum principal under DSCR.
- `debt_yield_limit`: maximum principal under lender debt yield convention.
- `maximum_loan`: minimum of the three constraints.
- `binding_constraint`: LTV, DSCR, or Debt yield.
- `sizing_annual_debt_service`: annual amortizing debt service at maximum loan and sizing rate.
- `sizing_dscr`: NCF divided by sizing annual debt service.
- `sizing_debt_yield`: lender-defined cash-flow numerator divided by maximum loan.
- `first_year_debt_service`: first-year contractual debt service, observing IO if applicable.
- `cash_to_borrower`: loan less existing payoff, loan-based origination fee and fixed closing costs; negative means cash in.
- `stress_uw_noi`: NOI with EGI 5% lower, management recalculated; other expense unchanged.
- `stress_maximum_loan`: sizing with EGI 5% lower AND sizing rate 100 bps higher, cap rate unchanged.
- `subject_lease_monthly_rent`: current authoritative monthly rent for unit/suite 101.
- `subject_lease_expiry`: authoritative current expiry for unit/suite 101, ISO date.
- `subject_lease_deposit`: security deposit for unit/suite 101.
- `verified_renewal_insurance`: verified annual renewal insurance premium; unknown/null if absent, not the scenario allowance.
- `renewal_option_exercised`: whether delivered materials evidence exercise of the renewal option.
- `prepayment_friction`: describe actual prepayment friction, including swap termination if stated.

Keep all rates and assumptions from the packet. Current rate, sizing rate, historic NOI, underwriting NOI and NCF are distinct. The first year of contractual debt service uses the contractual rate and stated IO period. The combined downside is EGI -5% AND sizing rate +100 bps; management is recalculated and the valuation cap rate is unchanged. The workbook should also support cap rate +50 bps separately.
