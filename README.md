# CRE Bench by Lev

An open evaluation of commercial real estate document understanding, financial analysis and delivered work products. Published and funded by Lev, which also participates in the evaluation.

[Explore the results](https://crebench.vercel.app/results.html) · [Inspect the cases](https://crebench.vercel.app/tasks.html) · [Method](https://crebench.vercel.app/method.html) · [Reproduce](https://crebench.vercel.app/reproduce.html)

Workflow v1 uses six original fictional financing packets, each with four PDFs and an XLSX rent roll, across multifamily, retail and industrial. Lev's native product, GPT-5 in a generic agent harness and Claude Opus 5 in the same harness receive the same business brief and files. Separate direct API controls use a text-only representation. All responses and unfavorable findings are retained.

The four task scores cover 17 source facts, 22 financial outputs, ten workbook acceptance checks and ten memo acceptance checks per case. Source-location evidence is scored separately. There is no blended overall winner. Actual workbooks are recalculated and changed-input copies are tested; original PDFs receive text and page-layout review.

**Limits:** One fresh attempt per case and system. AI-assisted case creation and author review with provider identities visible. No independent practitioner validation yet. Concise synthetic packets are not representative of all customer documents. Lev uses deployed agent 7.9 / Claude Opus 4.7; generic baselines use the recorded gateway model IDs. Tools, provider defaults and compute differ. These are custom agents, not the consumer ChatGPT or Claude applications. Costs distinguish gateway-reported inference from Lev trace estimates and exclude unattributed setup and platform costs.

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
- [`benchmarks/research-v1/`](benchmarks/research-v1/): design for sales/rent comps and qualified sponsor/refinance leads; planned, with no scored results yet.
- [Earlier development pilot](https://crebench.vercel.app/pilot.html): a separate one-case cohort with its original limitations and corrections.

The original runner and all 72 frozen manifest hashes are retained. Nine gateway credit interruptions resumed their exact saved requests, with original consumed turns, tools, artifacts and costs retained. Administrative credit waiting is excluded from active run latency and explicitly logged. Completed workflows were not selectively rerun.

**Artifact-generation reproduction limit:** The scored general-agent writer used the Codex-bundled `@oai/artifact-tool` runtime, unavailable from the public npm registry when checked. Its wrapper is open, but identical new artifact generation requires that runtime. Numerical regrading and independent replay of the published XLSX files use public dependencies only. A fully public generation adapter is future work and must not be represented as identical to the scored harness. Lev's backend remains proprietary; sanitized native outputs and review evidence are public.

## Ownership and contributions

Original benchmark code, website, fictional cases and reviews are MIT licensed. No trademark rights are granted. Private customer documents, credentials, native internal prompts and private account traces are not redistributed. The earlier consultant engagement informed project scope; this original implementation does not imply consultant endorsement.

Report a case, source, key or scoring problem with the exact input and criterion. Corrections must apply uniformly to every affected system and retain original records. See [CONTRIBUTING.md](CONTRIBUTING.md) and the [public governance page](https://crebench.vercel.app/governance.html).
