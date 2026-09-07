# rent-comps-cypress

Fictional CRE research evaluation. As of 2026-08-31, work only from the supplied record extracts and source updates. These records are original fixtures, not real properties or contacts. Do not use external search, other deals, CRM records or contact enrichment; do not send messages or create CRM records. Routine analysis and requested file generation are authorized.

Scope: Industrial in Columbus. Use evidence published and effective on or before the cutoff. Executed amendments, recorded releases and current company team-page updates override the base extract for the same entity. Unsigned drafts and later-dated evidence do not. Apply entity updates to duplicate records of that entity. Missing is unknown, not zero.

Select up to five unique executed leases from 2025-09-01 through 2026-08-31 within 8 miles. Asking/unsigned rents do not qualify. Positive rent and known term, free rent and TI are required; gross leases also require a known expense deduction. Compare effective net rent per sf per year using this client convention: convert the face quote to annual $/sf; increase face rent by the stated annual percentage at months 13, 25, etc.; charge no face rent in the first free_months; deduct annual_expenses_psf/12 in EVERY month for gross leases (NNN deduction is zero); subtract TI once; divide net total by term_months and multiply by 12. This is an undiscounted rent-only convention, not a market appraisal. Rank qualified results by distance ascending, then latest lease date.
Required facts: entity_id, event_date, annual_face_rent_psf, effective_net_rent_psf_year, term_months.

Return your complete answer as a JSON object (a fenced JSON block is acceptable) with:
- shortlist: ordered array of {record_id, facts: {required facts above}, source_ids: [base and controlling update IDs], rationale}.
- candidate_decisions: one row for EVERY base record, {record_id, eligible: true/false, reason, source_ids}. Eligibility means satisfying the business rules before deduplication; note duplicates in reason. A valid SPV mapped to a qualifying evidenced parent is eligible but must not add a second sponsor slot.
- summary: concise conclusion, including insufficient evidence or no qualifying results.
- limitations: array of uncertainties.
Citations must name the exact S-/U- source identifiers supplied in the packet. Do not claim an unsupported field or contact. Also produce a downloadable comp-grid XLSX for comps or prospect CSV for leads with citations and the same selected facts. Preserve explicit nulls and numeric units. Artifact creation is outside the direct API control and is assessed only for agent/native tracks.
