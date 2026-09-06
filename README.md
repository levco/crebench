# CRE Bench by Lev

An open project for evaluating AI on commercial real estate documents, financial analysis, and work products.

**Development preview: no model benchmark results have been published.** The current executable slice is one original synthetic public case with a deterministic grader. It is not a validated CRE benchmark or a held-out test. Underwriting-workbook and OM evaluation are specified but not implemented yet.

## Reproduce the public example

Requires Python 3.11+ and Node 20+; no third-party dependencies for this slice.

```sh
git clone https://github.com/levco/crebench.git
cd crebench
python3 -m unittest discover -s tests -v
python3 -m crebench verify cases/public/harbor-court-001
python3 -m crebench grade cases/public/harbor-court-001 cases/public/harbor-court-001/reference-answer.json
npm run build
python3 -m http.server 4173 --directory dist
```

The reference answer is a disclosed worked solution, not model output. Grading it verifies the public plumbing, not model capability. Author a separate answer to practice, using only the manifest's `system_inputs`. Use `--record path.json` to preserve hashes and a grade record; existing records cannot be overwritten. Exit codes: 0 all checks pass, 1 answer fails, 2 infrastructure/command error.

## What exists

- Original CSV rent roll and operating statement, a conflicting source summary, interest-only sizing assumptions, public answer key, output contract and manifest.
- 27 financial/extraction fields, separate evidence checks, discrepancy set checks, arithmetical consistency and immutable local records.
- Responsive static research website with a source-to-answer explorer, downloadable examples and truthful empty results.
- Negative tests for false conflicts, incorrect occupancy, bad calculations, fabricated citations, malformed output and input/key drift.

## What comes next

See [methodology](docs/methodology.md), [roadmap](docs/roadmap.md), [governance](docs/governance.md) and [contributing](CONTRIBUTING.md). More formats, authentic documents, independent CRE review, provider and Lev adapters, workbook recalculation, OM rendering, calibrated judges and a costed pilot are required before scored publication.

## Structure

`crebench/` grader and CLI · `cases/public/` licensed public examples · `tests/` validation · `site/` website sources · `tools/` build utilities · `docs/` method and governance.

Only `dist/` is deployed. The build copies an explicit public file list; it does not publish repository internals. Do not put customer documents, held-out keys or credentials in this repository or its history.

## Ownership and license

Created and published by Lev. New original code, documentation and the fictional example are MIT licensed; the license does not grant trademark rights. No consultant code or private customer material has been incorporated in this initial release. The initial scope was informed by an earlier methodology engagement with The AI Consulting Network; its private materials are not redistributed here. See [NOTICE](NOTICE).
