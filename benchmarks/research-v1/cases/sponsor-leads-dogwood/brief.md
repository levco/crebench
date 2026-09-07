# sponsor-leads-dogwood

Fictional CRE research evaluation. As of 2026-08-31, work only from the supplied record extracts and source updates. These records are original fixtures, not real properties or contacts. Do not use external search, other deals, CRM records or contact enrichment; do not send messages or create CRM records. Routine analysis and requested file generation are authorized.

Scope: Multifamily in Tampa. Use evidence published and effective on or before the cutoff. Executed amendments, recorded releases and current company team-page updates override the base extract for the same entity. Unsigned drafts and later-dated evidence do not. Apply entity updates to duplicate records of that entity. Missing is unknown, not zero.

Select up to ten distinct operating sponsors with a closed single-asset acquisition in the specified market/asset class from 2025-09-01 through 2026-08-31, with transaction size $17,500,000–$52,500,000. Exclude brokers, managers, announced bids and portfolio totals. Resolve property SPVs to evidenced operating parents and avoid duplicate sponsors. A current CFO, Head of Acquisitions or Director of Finance verified since 2026-03-01 is required. Registered agents and former employees do not qualify. A business email is optional; report null if it is not published, never guess one. Rank by qualifying transaction date descending, then transaction size descending.
Required facts: entity_id (operating parent), firm_name, transaction_size_usd, event_date, contact_name, contact_role, contact_email.

Return your complete answer as a JSON object (a fenced JSON block is acceptable) with:
- shortlist: ordered array of {record_id, facts: {required facts above}, source_ids: [base and controlling update IDs], rationale}.
- candidate_decisions: one row for EVERY base record, {record_id, eligible: true/false, reason, source_ids}. Eligibility means satisfying the business rules before deduplication; note duplicates in reason. A valid SPV mapped to a qualifying evidenced parent is eligible but must not add a second sponsor slot.
- summary: concise conclusion, including insufficient evidence or no qualifying results.
- limitations: array of uncertainties.
Citations must name the exact S-/U- source identifiers supplied in the packet. Do not claim an unsupported field or contact. Also produce a downloadable comp-grid XLSX for comps or prospect CSV for leads with citations and the same selected facts. Preserve explicit nulls and numeric units. Artifact creation is outside the direct API control and is assessed only for agent/native tracks.
