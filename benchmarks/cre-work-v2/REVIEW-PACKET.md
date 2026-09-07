# Practitioner review packet

Reviewer status: not assigned; no completed human grades. Two independent CRE
reviewers are required for qualification. The publisher has not selected them.
No paid reviewer engagement or external message has been sent.

## Reference qualification, before professional-readiness scoring

For each case, read the original sources and brief before the reference answer.
Independently calculate physical occupancy, contractual rent, stabilized GPR,
NOI, reserves, NCF, cap value, amortizing debt constraints and cash-out. Record
the exact source cells or paragraphs and every ambiguity. Decide whether each
fact has one defensible answer under the specified instructions. Flag unrealistic
or internally inconsistent source wording. A reference disagreement requires
adjudication and a new scoring version; do not silently edit an existing key.

Particular open questions: pending-occupancy boilerplate when no occupants are
pending; the three excluded ratio/capacity field names; treatment of an executed
amendment versus an explicitly separate stabilized GPR assumption; currency
tolerances versus material professional impact; and portfolio-size eligibility
in live sales discovery. Current source-location scores check recognized files,
valid page numbers and nonempty cell addresses; the spreadsheet check searches
across sheets. They do not prove that the cited location supports the claim.

## Coded work-product review

Run `python3 tools/build-cre-review-packet.py` to create coded copies and blank
review sheets under ignored `work/cre-work-v2/reviewer-packet`. The code-to-system
mapping stays separate from the reviewer folder. Files are copied byte for byte;
embedded branding may reveal identity, so record any identity cue. Coded names
alone do not establish successful blinding. Avoid consulting the public provider
comparison until both reviewers submit their first independent scores.

Review the initial workbook and PDF, then the revision and revision notice.
Check figures across the answer, workbook and OM; narrative support; omissions;
source/version authority; live formulas; revision propagation; legibility and
decision usefulness. A correct JSON answer is not proof that its files agree.
Use a working copy for edits, recording exactly what changed. Keep original files.

Use the blank CSV to record 0 unusable / 1 substantial rework / 2 material
correction / 3 ready after normal verification. Record critical failures, actual
verification minutes, correction minutes, approved-text retention, missing
facts, and identity cues. Do not estimate time retrospectively. A critical
financial failure blocks professional acceptance regardless of visual polish.
The second reviewer scores independently; record agreement and an adjudicator's
reason for each disagreement. An empty cell is unmeasured, not zero or failure.

## Data realism and release rights

All 20 published packets are original synthetic material across four shared
authoring families. They are not 20 authentic, independently sourced transactions.
Private deal-room examples informed task design but are not redistributed.
Authentic-deal qualification requires a source inventory, transaction-level
development/test separation, permission to benchmark, and documented rights
before public release of each file and identifying answer. Reviewers should
judge whether synthetic cases reasonably represent the intended customer work.
