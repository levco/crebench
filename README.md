# CRE Bench by Lev

An open evaluation of commercial real estate document understanding, financial analysis, delivered work products, and comp/lead research. Published and funded by Lev, which also participates in the evaluation.

[Explore the results](https://crebench.vercel.app/results.html) · [Inspect the cases](https://crebench.vercel.app/tasks.html) · [Method](https://crebench.vercel.app/method.html) · [Reproduce](https://crebench.vercel.app/reproduce.html)

Workflow v1 uses six original fictional financing packets, each with four PDFs and an XLSX rent roll, across multifamily, retail and industrial. Lev's native product, GPT-5 in a generic agent harness and Claude Opus 5 in the same harness receive the same business brief and files. Separate direct API controls use a text-only representation. All responses and unfavorable findings are retained.

The four task scores cover 17 source facts, 22 financial outputs, ten workbook acceptance checks and ten memo acceptance checks per case. Source-location evidence is scored separately. There is no blended overall winner. Actual workbooks are recalculated and changed-input copies are tested; original PDFs receive text and page-layout review.

**Limits:** One fresh attempt per case and system. AI-assisted case creation and author review with provider identities visible. No independent practitioner validation yet. Concise synthetic packets are not representative of all customer documents. Lev uses deployed agent 7.9 / Claude Opus 4.7; generic baselines use the recorded gateway model IDs. Tools, provider defaults and compute differ. These are custom agents, not the consumer ChatGPT or Claude applications. Costs distinguish gateway-reported inference from Lev trace estimates and exclude unattributed setup and platform costs.

## Comp and lead research

Research v1 adds 24 synthetic cases: sales comps, rent comps, sponsor qualification and refinance screening. Each case has twenty candidate records plus source updates, evaluated by native Lev, GPT-5 and Opus 5 with generic tools, and both models as direct API controls. The source packet, core factual grader and reference keys were frozen before execution. Original outputs, unsuccessful selections and every generated file version remain available.

[Research charts](https://crebench.vercel.app/research) · [Every case](https://crebench.vercel.app/research-cases) · [Executive report](experiments/2026-09-07-research-v1/REPORT.md) · [Frozen protocol](benchmarks/research-v1/execution-protocol.md)

These are four shared synthetic task families, not a live discovery test or 24 independent customer deals. All 120 research conditions were attempted; 119 returned answers and one GPT-5 direct condition exhausted its timeout retries. Headline denominators retain its unanswered slots/decisions, and its unreported charges remain unknown. Scores distinguish verified yield, selection precision, candidate screening, source-ID evidence, consequential findings and file consistency. Four zero-match cases have separate abstention results. The artifact mapper was implemented during the audit against criteria frozen beforehand; it maps equivalent representations uniformly without modifying model outputs. Generic CSV null-to-blank losses are explicitly attributed to the benchmark serializer when original tool inputs prove model-supplied nulls. Native backend tool metadata shows no retrieval, but internal file execution is absent; equal data access is unverified and native results are a separately labeled product condition.

Replay the research scores and publication figures with public Python packages (Python 3.12+ for the pinned figure-export dependencies):

```sh
python3 -m pip install -r requirements-research.txt
python3 tools/collect-research.py
python3 tools/report-research.py
python3 tools/plot-research.py
```

## Verify recorded results without model calls

Requires Python 3.11+ and Node 20+.

```sh
python3 -m pip install -r requirements-review.txt
python3 tools/collect-workflow-results.py experiments/2026-09-06-workflow-v1
python3 -m unittest discover -s tests -v
npm run build
npm run check:site
python3 -m http.server 4173 --directory dist
```

To independently recalculate original and published perturbation workbooks, install LibreOffice and put `soffice` on PATH:

```sh
python3 tools/replay-workflow-audits.py experiments/2026-09-06-workflow-v1 \
  --output work/independent-replay
```

This makes no API calls. It verifies original hashes, changed input cells, preservation of other formulas and independently calculated expected outputs. It records the local LibreOffice version and formula errors; it does not silently repair the delivered workbooks. The scored engine was LibreOfficeDev 26.8.0.0.alpha0.

## Inspect the protocol and records

- [`benchmarks/workflow-v1/`](benchmarks/workflow-v1/): six source packets, briefs, keys, reference workbooks, independent key checks and frozen rubric.
- [`experiments/2026-09-06-workflow-v1/`](experiments/2026-09-06-workflow-v1/): frozen manifest, responses, API tool calls, original deliveries, recalculation/perturbation evidence and attributed reviews.
- [`crebench/`](crebench/): source transforms, generic bounded tools, API runner, deterministic grader, presentation normalization and exact-context billing-resumption adapter.
- [`experiments/2026-09-06-workflow-development/costs.json`](experiments/2026-09-06-workflow-development/costs.json): separate adapter smoke tests and costs, excluded from scored runs.
- [`docs/`](docs/): disclosed corrections, source-location interpretation, governance and prior history.
- [`benchmarks/research-v1/`](benchmarks/research-v1/): 24 frozen original cases for sales/rent comps and qualified sponsor/refinance leads.
- [`experiments/2026-09-07-research-v1/`](experiments/2026-09-07-research-v1/): 120 planned conditions, original research responses/files, costs, scoring, figures and the executive report.
- [Earlier development pilot](https://crebench.vercel.app/pilot.html): a separate one-case cohort with its original limitations and corrections.

The original runner and all 72 frozen manifest hashes are retained. Nine gateway credit interruptions resumed their exact saved requests, with original consumed turns, tools, artifacts and costs retained. Administrative credit waiting is excluded from active run latency and explicitly logged. Completed workflows were not selectively rerun.

**Artifact-generation reproduction limit:** The scored general-agent writer used the Codex-bundled `@oai/artifact-tool` runtime, unavailable from the public npm registry when checked. Its wrapper is open, but identical new artifact generation requires that runtime. Numerical regrading and independent replay of the published XLSX files use public dependencies only. A fully public generation adapter is future work and must not be represented as identical to the scored harness. Lev's backend remains proprietary; sanitized native outputs and review evidence are public.

## Ownership and contributions

Original benchmark code, website, fictional cases and reviews are MIT licensed. No trademark rights are granted. Private customer documents, credentials, native internal prompts and private account traces are not redistributed. The earlier consultant engagement informed project scope; this original implementation does not imply consultant endorsement.

Report a case, source, key or scoring problem with the exact input and criterion. Corrections must apply uniformly to every affected system and retain original records. See [CONTRIBUTING.md](CONTRIBUTING.md) and the [public governance page](https://crebench.vercel.app/governance.html).

Research headlines use the documented [scoring v1.1 erratum](experiments/2026-09-07-research-v1/SCORING-ERRATUM.md). The pre-execution v1 grader and all original grades are retained; v1.1 adds source/unit-checked representation mappings without correcting model facts or rerunning conditions.
