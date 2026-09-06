# CRE Bench workflow evaluation

Status at freeze: six original packets, reference models, 385 independent checks and separate three-system artifact smoke validation complete. No scored workflow runs have started.

## Purpose

Help a CRE buyer understand where Lev's native product improves on general-purpose agents and direct foundation-model calls. Measure the correctness and usefulness of completed work, its reliability, and its attributable cost. Preserve unfavorable results.

## First full release

Six original, realistic fictional deal packets, spanning multifamily, retail, and industrial financing. Distinct scenarios cover stabilized refinance, lease-up/current-versus-pro-forma, amendment precedence, floating-rate floors, management/reserve conventions, and incomplete or conflicting evidence. They are informed by private professional materials reviewed in Drive and Slack; private source documents are not redistributed.

Each packet supports four linked tasks:
1. Extract financial and lease facts from source documents, with source locations and explicit unknowns.
2. Reconcile historical and underwritten cash flow, apply the specified lender's constraints, and size debt.
3. Deliver a native underwriting workbook with inspectable formulas, recalculation, and sensitivity behavior.
4. Deliver a financing memorandum with accurate financials, defensible claims, complete decision context, and usable rendering.

The evaluation includes Lev's native workflow, GPT-5 and Claude Opus 5 in the same general-purpose agent harness, and direct API financial baselines. Execution adapters and model identities must be proven before freeze. Expose tooling and input transformations; never label a custom harness as the consumer ChatGPT or Claude product.

## Order of operations

- Read representative work and authoritative underwriting conventions.
- Write source packets, briefs, deterministic keys, rubric, artifact acceptance checks, and a reproducible reference workbook.
- Independently recalculate the key using a second implementation and review ambiguous conventions. Record machine and author review honestly; do not imply independent practitioner review occurred.
- Use disjoint smoke fixtures to validate each adapter and artifact transport. Do not test scored cases while tuning the harness.
- Freeze all case, prompt, key, rubric, and runner hashes before execution. Record a bounded cost reservation and exact system settings.
- Execute fresh runs with all planned systems. Preserve blocked attempts, tool calls, artifacts, timings, costs, and mechanical recovery separately.
- Grade with deterministic checks plus a disclosed author review protocol for visual and narrative quality. AI-assisted review is labeled and cannot be portrayed as professional human preference.
- Publish complete results, artifacts, reproducibility instructions, and corrections. Update the site with an executive comparison, task-level charts, per-case evidence, cost/time views, and explicit limitations.

## Presentation rules

No chart starts with a predetermined winner. Use a shared zero-based scale, clear denominators, equal case weighting, visible missing outcomes, and consistent colors. Display win/tie/loss by task only for comparable conditions. Separate financial accuracy from presentation quality and from execution completion. A material financial error cannot be offset by attractive formatting. A small synthetic suite is not a representative real-world accuracy estimate.

## Open work

Frozen execution, case-level grading, public release and complete product-cost attribution remain outstanding. Native workflow inference cost can be estimated from matched traces; customer pricing remains separate. Prior one-case pilot results remain separately labeled historical development evidence.
