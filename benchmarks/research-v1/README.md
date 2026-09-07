# CRE research benchmark: comps and qualified leads

Status: protocol design, September 6, 2026. No cases have been frozen or scored. This is a separate cohort from workflow-v1; it does not change any published score.

The customer question is whether the system finds usable, verifiable opportunities and market evidence with less analyst effort. A long list of plausible addresses or people is insufficient. Evaluate the delivered shortlist, its supporting evidence, and the consequential errors.

## Planned tasks

| Task | Initial case slots | Deliverable | Principal challenge |
|---|---:|---|---|
| Sales comps | 6 | Ranked shortlist of up to five closed transactions, an Excel comp grid, and a short conclusion | Comparable property and transaction selection; verified consideration, date, rights conveyed, units/area, and justified normalization |
| Rent comps | 6 | Up to five comparable leases or listings with a clearly labeled rent basis and an Excel grid | Executed vs asking rent; gross vs net; period/area units; concessions; term and property differences |
| Sponsor prospects | 6 | Ranked shortlist of up to ten distinct operating sponsor firms with relevant decision makers and source-backed fit | Actual activity in the requested market, asset class and deal-size range; ownership/control and current employment |
| Refinance prospects | 6 | Up to ten property-owner opportunities with debt evidence, timing, uncertainty and appropriate business contacts | Matching property, owner and loan; distinguishing recorded origination from current outstanding balance, and stated maturity from inferred maturity |

These 24 slots define pilot coverage, not a claim of adequate statistical power. Comps span multifamily, retail and industrial, with different submarkets and source layouts. Prospect briefs vary geography, asset class, deal size and role. Include sparse/no-match cases; incomplete results may be the correct answer. Allocate half the slots to public development and half to a held-out qualification set, split by underlying market/property/ownership group and source template where feasible. Do not reuse the six published financing packets as unseen cases.

## Comparison conditions

1. **Common source corpus:** every participant receives the same frozen, rights-cleared records. Direct GPT-5 and Opus 5 select and reason from that packet; generic agents may search the same corpus with the same public tools. Use native Lev only if its external sources can be restricted or independently audited for this condition; otherwise mark that comparison unavailable. No hidden Lev enrichment in a same-data result.
2. **Discovery workflow:** give the same business brief and as-of time to Lev and to GPT-5/Opus 5 agents with documented search and retrieval tools. Record native data entitlements, external services, source coverage and retrieval timestamps. This measures the whole product/data workflow; an advantage cannot be attributed exclusively to the model. A bare API without retrieval is not a competing live-discovery system.
3. **Matched-source follow-up:** when release rights permit, give baseline agents the permissible evidence retrieved by Lev, and vice versa, under a separate frozen diagnostic protocol. This helps distinguish finding evidence from interpreting it. It is not a replacement for the original results.

The initial paid pilot should start with two sales-comp and two sponsor-prospect development cases in the common-corpus condition. Freeze inputs, answer sets and scoring before seeing outputs. Use that pilot to measure cost and ambiguity, then freeze the full execution plan before qualification. No claim that these runs have occurred.

## Source construction and truth

For controlled cases, build a candidate pool with at least twenty records, including relevant choices, plausible near misses, duplicate records and conflicting/stale versions. Begin with original fictional records for grader development; use permitted authentic layouts and sourced records for qualification. Fictional company/contact fixtures use reserved example domains and are explicitly labeled. They do not establish live lead-finding performance.

An as-of timestamp belongs to each case. Store effective date, publication date and retrieval date separately. Exclude later knowledge. A model may not treat an old deed as proof of today's ownership, a historic loan amount as its outstanding balance, or a nominal loan term as a confirmed unextended maturity. Property-manager, registered-agent and owner identities are separate relationships.

Build references independently of Lev's results and directory. Use permitted deed/assessor records, executed transaction or lease evidence, public company portfolios and team pages, and other sources appropriate to each field. Track redistribution rights per record. Public visibility alone is not permission to redistribute an entire commercial dataset. Publish original fixtures, permitted evidence, hashes and scoring; keep licensed/customer records restricted where required.

Two CRE reviewers should independently label candidate eligibility, ranked relevance, verified facts and accepted alternatives before the final freeze, with disagreements adjudicated and reviewer identities recorded. This review has not occurred. Reviewers should not see the tested system identity when judging submitted shortlists. A Lev-produced answer is never its own ground truth.

For open discovery, pool and deduplicate submissions from all systems and independent researcher searches, then review them blind. Report precision and supported coverage. Do not report web-wide recall: the total number of eligible results is unknown. Any pooled-recall diagnostic must disclose its pool construction and incompleteness.

## Scoring contract

Publish separate measures; do not collapse them into an overall winner score.

- **Shortlist usefulness:** unique, verified eligible results divided by requested result slots. For controlled sparse cases only, cap the slot denominator at the adjudicated number available. For zero-eligible controlled cases, score correct abstention separately rather than inventing a percentage. In discovery, report accepted count, requested-slot yield and precision among returned results together so returning one safe item cannot masquerade as a complete search.
- **Ranking:** graded relevance at the requested cutoff (five comps, ten prospects), with reviewer labels fixed before model output for controlled cases. Accept ties and multiple valid shortlists. Show the relevance definition and eligible count; no single arbitrarily preferred list is the only passing answer.
- **Field accuracy and evidence:** score each required fact and its supporting source separately. A working link alone does not support the claimed value. Match the actual property, transaction, firm, person and date. Claims labeled unknown are distinguished from incorrect confident claims; unknown mandatory fields reduce usable yield without being called fabricated.
- **Material errors:** count false closed sales, invented prices/rents, unsupported financial adjustments, wrong owner/person joins, stale roles presented as current, and asserted maturity/refinance need without supporting evidence. Display these errors beside averages. Material numeric tolerances and categorical failure rules must be fixed per case before execution.
- **Output usability:** inspect the actual Excel/CSV and rendered brief. Require stable identifiers, deduplication, original citations, units, dates and qualification notes. Check comp-grid formulas and recompute normalized price/rent values. Lead CSVs must keep firm, property, person, role and evidence relationships intact. Formatting cannot offset a false fact.
- **Effort, cost and time:** record total inference, paid search/data/contact charges, native credits, failed attempts, active elapsed time and analyst verification/correction minutes. Show cost per verified eligible result as well as total case cost. Zero accepted results produce no finite cost-per-result ratio. Unmeasured components remain unknown. Credit prices are separate from internal inference cost.

Sales-comp keys must distinguish a single-asset sale from a portfolio allocation, arms-length vs related-party/distressed conditions, stabilized vs redevelopment assets, estate/interest conveyed, and appropriate size units. Record asking prices separately. Do not permit an unsupported percentage adjustment merely because it makes values converge. Prefer a justified range and limitations when the evidence does not support a precise estimate.

Rent-comp keys must explicitly define whether the task asks for face rent or effective rent, the treatment of free rent/TI/escalations, and the gross/net expense basis. Unknown concessions must not become zero concessions. Do not blend annual $/SF with monthly $/unit or use office rentable area as interchangeable with another area measure.

Prospect eligibility requires evidence for every mandatory brief constraint. A CRE-sounding title or company name alone is insufficient. Deduplicate property-owning SPVs to the operating sponsor when the relationship is evidenced; preserve individual property opportunities separately. Separate verified business contacts, business switchboards, stale contacts, guessed patterns and unavailable details. A published email is not proof of deliverability. Do not test by contacting people or sending email.

## Concrete brief templates

**Sales comps:** As of the stated date, find up to five closed sales relevant to the subject's property type, size, condition, location and ownership interest. Explain any expanded geography or time window. Deliver a sortable comp grid with transaction evidence, price per declared unit, exclusions, and a supported conclusion. Show uncertainty where consideration or portfolio allocation is unavailable.

**Sponsor prospects:** Find up to ten distinct operating sponsors with evidenced activity in the specified market, asset class and transaction-size band. For each, identify a relevant current finance/acquisitions decision maker where evidence exists; attach the qualifying transaction or portfolio evidence, employment evidence, dates, business contact provenance and reasons to prioritize. Do not fill missing facts with guesses.

**Refinance prospects:** Identify property-owner opportunities meeting the stated financing criteria within the defined date window. Separate confirmed maturities from inferred dates and unavailable loan status; account for evidenced amendments/extensions. Provide the entity chain, loan source, trigger, qualification gaps and an appropriate current business contact where supported. Rank confirmed matches separately from research-needed candidates.

## Release and executive presentation

Preserve unsuccessful runs and immutable versions. Use one fresh attempt per system/case for the first diagnostic pilot, then preregister repeated trials with a fixed budget. Do not rerun selectively to improve a system's result. Later reliability estimates cluster by case/market/ownership group, rather than counting repeated contact fields as independent observations.

Publish four task panels with verified results per requested shortlist, material-error incidence, evidence completeness, and cost/analyst minutes per accepted result. Let a reader open the actual comp or prospect, its evidence and rejection rationale. Separate common-corpus and product-discovery results and identify missing capability or unavailable access. Publish no win claim before reviewed runs exist.

## Design grounding

Lev's [product descriptions](https://www.lev.com/products) include sales-comps and origination workflows. Its [help center](https://www.lev.com/docs/learn) includes market insights, CRM and Lev Agent; the inspected sponsor-help source asks for market/location, property focus and typical deal size, with a contact CSV as output. These establish relevant tasks, not measured product capabilities.

The FDIC's [commercial real estate lending examination material](https://www.fdic.gov/risk-management-manual-examination-policies/commercial-real-estate-lending) emphasizes genuinely comparable sales, supported market analysis and scrutiny of excessive adjustments. That informs the comparability and evidence checks; this benchmark does not certify an appraisal or regulatory compliance.
