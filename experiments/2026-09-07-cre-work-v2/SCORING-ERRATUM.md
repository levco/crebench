# Scoring v1.1 correction during initial diagnostic review

Recorded on 2026-09-07 after the first Magnolia native answer and two API
initial/revision pairs were available, before publication. Original prompts,
source documents, model outputs, runner, reference keys and v1 grades remain
unchanged. No model is rerun or given corrected facts.

1. The reference generator carried the INITIAL pending-occupant risk into the
   revision even when the new certified roll showed zero remaining pending
   occupants. The revised snapshot no longer has unpossessed pending occupants;
   v1.1 expects that current risk to be absent. The affected cases are determined
   solely from initial pending count > 0 and revised pending count = 0, applied
   uniformly to every condition. Risk precision/recall is recomputed. The
   initial historical manager discrepancy remains in the original record.
2. Evidence arrays containing objects such as {file, loc} are valid under the
   business brief, which did not require each array item to be a string. A
   lossless filename/location mapping enables the same citation-location check.
   No factual value, source choice or substantive citation is corrected.
3. The requested names ltv_limit, dscr_limit and debt_yield_limit did not specify
   whether the answer should be a covenant ratio or dollar loan capacity. The
   native output used ratios while API outputs used capacities. All three are
   excluded from scored denominators for every provider and every case. Both
   interpretations remain visible in original per-field results. The financial
   denominator is 12, not 15; maximum_loan and actual workbook behavior remain
   scored. This exclusion was recorded after initial Magnolia and office runs
   began. The next version must explicitly name and define both quantities.

The correction adapter is separate from the frozen v1 grader. Preserve both
versions and publish all per-field adjustments. Independent practitioner
qualification remains pending. A citation-location check does not establish
semantic source support or professional acceptance.
