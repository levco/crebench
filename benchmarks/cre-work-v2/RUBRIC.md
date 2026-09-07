# CRE Work v2 rubric (candidate for independent qualification)

Scoring is separated by task. No single composite winner is inferred from
incommensurate tasks, missing measurements, or incomplete cohorts.

## 1. Ingestion

Score each requested fact against the case reference with a declared unit and
tolerance. Whole counts are exact; currency allows max($1, 0.01% of reference);
ratios allow 0.0001 in decimal form. Unknown and zero differ. Check unit-type
breakdowns, annual/monthly conversion, physical/area occupancy, and the
authority and effective date of the selected rent and expense documents.

Separately score location support (filename plus page/cell) and semantic
support. Automated location checks establish that a cited location exists;
they do not by themselves prove that it supports the claim. Label these
different measurements explicitly. Original-file and verified-text conditions
must have their own scores. Record indexing/upload failures separately.

## 2. Underwriting and OM

Check delivered file readability, requested content, numerical accuracy,
formula-linked outputs, sensitivity behavior, and agreement between XLSX,
PDF and final answer. Recalculate copies in an independent spreadsheet engine.
Never repair the delivered originals. Critical failures include materially
incorrect NOI/NCF, loan capacity, cash-out, in-place rent or occupancy, and
unsupported ownership/property/transaction claims. A critical failure prevents
professional acceptance even if presentation earns full marks.

Human scoring: 0 unusable, 1 substantial rework, 2 minor material corrections,
3 ready after normal verification. Also record professional preference without
provider identity, verification minutes, correction minutes, and exact edits.
Two reviewers independently assess acceptance; adjudicate disagreements.
Automated section-count checks are not a professional-readiness score.

## 3. Revisions

Use the same conversation and its original files. Provide only the frozen
revision request and additional source. Grade revised values and the actual
updated files. Compare all unaffected facts against the original reference;
check retention of specifically approved text. Report initial and revision
success separately and end-to-end success only when both pass. A skipped or
failed initial stage remains in the denominator. References to old values are
allowed when clearly labeled as an explicit before/after comparison.

## 4. Judgment

Assess every named issue in the brief as present, absent, or unresolved, with
support. Known issues use precision/recall and false-positive rate; unknown
critical information uses an abstention/clarification score. Include clean
controls. Assess interpretation beyond enumerated issues through blind human
review. Do not reward an unsupported accusation or an indiscriminate warning.

## 5. Live discovery

Freeze geography, property/transaction criteria, as-of date, target count,
ranking preferences and search allowance before retrieval. Store each search
and opened source with retrieval time. Verify identities, deal dates, source
publication dates, prices/sizes/units, contact role and employer, and whether
figures are asking terms or executed terms. Unknown terms must remain unknown.
Report verified precision@target (unfilled slots are unfilled), precision among
returned results, and evidence quality. Recall is only over the disclosed,
independently audited pooled candidate set; the complete web universe is unknown.

## 6. Lender qualification

Distinguish product discovery, program eligibility and ranking. A dated source
must support each material qualification. Hard constraints in the request are
hard even when a product ranks rather than filters on that attribute. A lender
may be conditionally suitable when a documented exception could apply; do not
turn a typical guideline into a universal prohibition. Do not equate directory
inclusion, historical lending or a suggested match with current approval.
Score stale programs, incompatible property/loan/geography/size, recourse,
leverage, coverage, and missing prerequisites. No lender outreach occurs.

## Reliability, costs and missingness

Retain all three planned trials, infrastructure outcomes and token usage.
The first attempt is the primary success measure; all-three success measures
consistency. Report denominators by independent case and task, including the
number of shared generation families. Never select the best trial.

Record inference, search/data fees, product charges, subscriptions and human
work separately. Unknown is not zero. An all-in cost or cost-per-accepted
deliverable is published only when the needed acceptance and cost components
have actually been measured. Report estimates as estimates and cost lower
bounds when attempts lack billing evidence.

## Grader validation and changes

Before paid execution, test reference answers, deliberate material mutations,
unknown/zero distinction, numeric unit wrappers, changed key names, valid
formatting variants, missing deliveries, source-path escape attempts, and
revision carry-through. Validate solvability without paid model answers.
Freeze the first execution version after these checks. Any later scoring
correction must preserve original grades and show the effect on every system.
