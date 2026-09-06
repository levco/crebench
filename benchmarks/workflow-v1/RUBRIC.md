# Workflow v1 rubric and execution protocol

Version: 1.0. Frozen before scored execution. Six cases, one fresh attempt per system and case. Three assets types are represented twice each. This is a small, original synthetic evaluation, not a population estimate or an independently reviewed industry standard.

## The buying decision

Can a CRE professional trust the facts, change the underwriting, and send the financing narrative for internal review? Report four separate task scores, critical financial errors, completion, time, cost, and operator interventions. Do not blend them into a single winner or let presentation compensate for incorrect debt sizing.

### 1. Document extraction and evidence

Score the case's explicitly requested source facts individually, with equal weight within a case. Include unit/suite count, physical and area occupancy, rent, historical income and expense classification, lease dates and amendment precedence. A missing answer fails an answerable check. A justified unknown passes an explicitly unanswerable check. Zero and missing are different.

Evidence is a separate score: each checked answer must identify an actual provided document and page, worksheet/row, or named clause that supports it. A filename alone supports document-level provenance but does not receive location-level credit. Correct arithmetic without supporting source discovery does not pass evidence checks. The evaluator verifies citations against the input, not a pre-supplied list of acceptable reference IDs. A copied wrong-period figure fails even if it is cited accurately.

### 2. Financial analysis

Score each requested financial output against independently reconciled keys. Currency tolerance: the greater of $1 or 0.01% of the expected value; ratios and rates: 0.0001 in decimal units; occupancy: 0.01 percentage point; integer counts and dates exact. Rounding is accepted, reasoning errors are not repaired. A formatting error alone is diagnostic and cannot erase financially correct, unambiguous content.

Distinguish historical T12, current rent roll, and underwritten projections. Reconcile NOI before replacement reserves and NCF after reserves, respecting lender-specific management and debt-yield conventions. Apply the specified index floor, spread, sizing-rate floor, monthly amortization, IO period, leverage and coverage constraints. The lowest permitted constraint determines sizing. Calculate refinance cash after existing debt, loan-based fees and stated fixed closing costs. Stress EGI down 5% and the sizing rate up 100 bps, holding other assumptions as instructed. Do not infer lender approval from a mathematical maximum.

**Critical errors:** loan maximum, normalized NOI/NCF, binding constraint, occupancy, or lease authority materially wrong; an unsupported missing input presented as verified; a projected value labeled historical; an invented market/sponsor fact. Show the exact magnitude and source. A field outside tolerance is a check failure; materiality for the critical-error flag is >1% for monetary underwriting outputs, >1 percentage point for occupancy, or any categorical authority/verification error. Both measures are published.

### 3. Underwriting workbook

Ten equally weighted acceptance checks per case:

1. A real, openable XLSX is delivered.
2. Inputs, units, as-of dates and source references are identifiable.
3. Historical and underwritten cash flows remain separate and reconcile.
4. The base NOI/NCF and loan size match the case key.
5. Material calculated outputs use inspectable formulas rather than only pasted results.
6. Raising the valuation cap rate by 50 bps changes value and LTV capacity correctly.
7. Raising the sizing rate by 100 bps changes the amortizing constraint correctly.
8. Reducing EGI by 5% changes management, NOI/NCF and sizing correctly under the stated rules.
9. Workbook has no broken references, formula errors, required external links, macros, or hidden hard-coded override that prevents these scenarios.
10. Normal-zoom rendering is readable: labels/units are visible, key figures are not clipped, and a reviewer can locate the decision and assumptions.

Perturbations are performed on copies of the delivered artifact. Record edited cells, actual recalculated outputs, expected outputs, engine/version, and any unavailable native-engine verification. A JSON/CSV/table is useful financial output but is not a delivered workbook. A failed renderer/tool counts toward artifact completion; the underlying financial answer can still earn its separate score.

### 4. Financing memorandum

Ten equally weighted checks: delivered readable PDF or native export; property/as-of/purpose; transaction and sources/uses; accurate historical vs underwritten financial table; supported loan/constraint/coverage; tenant/lease/occupancy discussion; risks and unresolved evidence; explicit and correctly labeled assumptions; source references; usable hierarchy, tables and page layout. Financial claims are checked deterministically where possible. Claims absent from sources must be labeled assumptions and permitted by the brief. Fictional market comps, sponsor achievements, lender commitments or unconditional repayment assurances fail the unsupported-claims check.

Review text and rendered pages against these fixed checks. The author sees provider identities; this is not a blinded human study. Record a rationale and evidence excerpt for every non-numeric decision. This initial evaluation is author-reviewed with machine assistance, not independent practitioner preference research. Publish the reviews and artifacts so another reviewer can disagree. Do not call subjective scores human-expert validated. Do not award points for mentioning Lev or benchmark branding.

## Systems, comparable conditions, and interventions

- Lev native: Kyle Graves's authorized test account, fresh isolated deal/chat per case; supplied files and business brief; normal outline/build confirmations allowed. No hand-corrected financial inputs, answer hints, or semantic rescue in first-pass scoring. Explicit tool/UI errors and unchanged-file recovery are recorded separately. Upload the five original files during deal setup and attach the same five originals directly to the fresh chat before the exact shared brief. The product address is initially unset when its geocoder cannot resolve a fictional address; native extraction may populate it from the supplied files. Source-document facts govern. This measures Lev Agent document-to-deliverable workflow, not the separate Index auto-population pipeline. No consumer outreach. Record model/version and matched workflow cost from the actual trace; otherwise unknown.
- GPT-5 agent and Claude Opus 5 agent: identical generic harness, same files and brief, same file-reading, arithmetic, workbook and PDF creation tools, same turn/output/time limits. These are custom general-purpose agent baselines, not the consumer ChatGPT or Claude applications. Publish every tool schema, transformation and output. No CRE-specific calculation or gold-answer tools.
- Direct APIs: same source text/transforms and analysis questions, no agent tools or artifact expectation. Label this text-reasoning control, not native PDF ingestion. Do not rank artifact completion against these intentionally narrower baselines.

Provider defaults are disclosed, not assumed equal compute. No model fallback. One bounded retry for transport errors is permitted, charged and retained. Invalid output can be parsed by deterministic presentation normalization or manually transcribed with exact source excerpts; no answer-key-guided correction. General agent tool feedback is ordinary execution and retained. Operator interpretation, follow-ups, active time and wait time are logged separately. Compare first-pass results; any recovery remains visible and separate.

## Fixed execution limits

General agents: 32 model turns, 96 tool calls, 49,152 output tokens per call, 300-second request timeout, 1,800-second total run limit, concurrency two. Direct control: one call, 32,768 output tokens. One transport retry on 429/5xx or network timeout. API experiment reservation limit: $100, cumulative across resumes. Lev uses the native deployed agent and its product limits; no compute-equivalence claim. Exact gateway model IDs: `openai/gpt-5` and `anthropic/claude-opus-5`. Development smoke runs are excluded from scored results and costs, disclosed separately.

## Cost, time, and review

Include all attempts and model/tool charges for the run. Distinguish gateway-reported API USD, estimated catalog USD, product credits, subscription cost and unattributed cost. Unknown is never zero. Lev workflow inference estimates are matched to the exact chat trace and exclude duplicated run-summary events. They do not include unattributed setup extraction/classification, hosting, OCR, storage or subscription costs. Do not convert Lev credits to USD without an applicable verified price. Report latency from first task submission through final usable artifact, setup time separately, plus intervention count. Report agent token use and compute/tool limits. Cost per successful workflow is only computed where the full attributable cost and success denominator are known.

Freeze case bytes, prompts, keys, rubric, evaluator and runner hashes before scored execution, with a dated commit and selected model catalog. Use a different smoke packet for adapter debugging. Do not rerun selectively or change scoring after seeing who wins. If a defect is found, preserve the old result, publish the correction and regrade every affected system equally. With six paired cases, publish case-level points and totals; avoid significance or broad market superiority claims.

## Grounding and publication

Private materials reviewed include actual financing memoranda, an underwriting workbook, lease documents and lender term sheets. They informed task structure and difficult conventions; no private documents, identifying details or numbers are redistributed. Original fictional cases and benchmark code are public. Source-authoring and scoring were performed by the same AI-assisted project team; independent CRE practitioner review is still absent.

Method references: [OpenAI GDPval](https://openai.com/index/gdpval/) and its [grading limits](https://evals.openai.com/gdpval/grading); [Fannie Mae underwritten DSCR](https://mfguide.fanniemae.com/node/3781); [OCC CRE lending handbook](https://www.occ.treas.gov/publications-and-resources/publications/comptrollers-handbook/files/commercial-real-estate-lending/pub-ch-commercial-real-estate.pdf). These support the evaluation approach and relevant distinctions; the fictional lender terms in each packet govern the calculations, not a claim that one convention applies to every loan.
