# Live discovery: frozen business briefs and review rules

Version live-discovery-1. As-of cutoff: 2026-09-07, 00:00 UTC. Run each condition
with a fresh context and no candidate names, source shortlist or reference
answer. This is actual research from a brief, separate from supplied-record
screening. Original search results and cited pages are retained privately when
copyright or account entitlements prevent public redistribution. Publish URLs,
retrieval times, short supporting excerpts, hashes and the audit outcome.

## Common task

Find up to three verified results meeting the brief. Prefer authoritative
transaction participants, company announcements, official property records or
regulatory filings. Open and inspect evidence rather than treating search
snippets as verified. Report source publication date separately from transaction
date and retrieval date. Missing price, rent, balance or contact remains unknown.
No outreach, contact unlocking, CRM modifications or paid data purchases.

Return a JSON object with results (array), exclusions (array), search_summary,
limitations, and sources (array). Each result contains name, address or market,
transaction_date, publication_date, property_type, size_sf, units, price_usd,
annual_rent_psf, buyer_or_owner, contact_name, contact_role, contact_email,
source_urls, and qualification_explanation. Use null for inapplicable/unknown
fields. Explicitly distinguish asking, executed and estimated terms. A
professional contact must have an evidenced current employer and relevant role;
do not infer an email address from a company's naming convention.

## Briefs (run in this order)

1. **Atlanta multifamily sales.** Atlanta metropolitan area; completed sales in
   calendar 2025; at least 100 apartments per property. Identify transaction
   price and unit count where disclosed; compute price/unit only when supported.
2. **Dallas industrial sales.** Dallas-Fort Worth metropolitan area; completed
   industrial/warehouse sales in calendar 2025; at least 25,000 SF. Distinguish
   acquisitions from leases and construction-financing announcements.
3. **Phoenix industrial lease comps.** Phoenix metropolitan area; signed leases
   announced in calendar 2025; at least 50,000 SF. Report executed rent only when
   directly disclosed; do not substitute asking rent, market average or assumed
   escalation. Missing rent does not invalidate an otherwise evidenced lease.
4. **Southeast multifamily buyers.** Three distinct sponsors with an evidenced
   acquisition of at least 100 apartments in NC, SC, GA or FL during calendar
   2025. Resolve transaction SPVs to a supported operating parent and identify
   one publicly evidenced acquisitions/capital-markets professional per sponsor.
5. **Midwest retail buyers.** Three distinct sponsors with an evidenced 2025
   acquisition of a shopping center of at least 25,000 SF in OH, IN, IL or MI.
   Preserve the qualifying transaction when resolving the buyer's parent.
6. **Office refinance prospects.** Three US office properties with a publicly
   documented loan maturity in calendar 2027, using evidence published before
   the cutoff. Identify borrower/owner, originating amount and current balance
   separately. Account for documented extensions; do not infer current balance
   from original principal. Return fewer than three if support is insufficient.

## Conditions and budget

Native Lev Agent uses its available research tools; the exact business brief
and source restrictions apply. GPT-5 and Opus 5 receive generic web-search and
page-open tools. Record actual model/tool availability and any access failures.
A model may make up to 8 searches and 8 page opens, 16 turns, and one transport
retry. The neutral search bridge executes the model's exact query. It does not
add candidates, repair answers or add gold information. Search sources and
query text are recorded. API inference allocation is $5 from the expansion's
previously reserved headroom; unknown search-service cost is separately marked.
Native costs count against the existing $45 native allocation.

Three trials per brief/condition are the target. Dispatch all briefs once in
order before additional trials. Stop at the authorized allocation and label
remaining cells not run. Any access-unavailable product condition remains
visible and is not replaced with a different product under the same label.

## Verification

Freeze the verification criteria before answers are visible. Pool the union
of returned candidates with an independent researcher's candidate set; verify
all under the same criteria with provider identities hidden. Audit each
qualifying fact and each source date, not only whether the URL opens. Duplicate
properties and sponsor entities count once per brief. Report verified yield
out of three, precision among returned entries and unknown-field rates.
Independent review and pooled coverage remain pending until performed. Do not
publish unverified model answers as transaction facts or score them as correct
based on the model's self-reported evidence.
