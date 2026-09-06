# Methodology 0.1: development protocol

CRE Bench evaluates the path from original CRE documents to financial understanding and usable work products. Initial scope is debt and financing. This specification is under development; only the CSV/JSON public example and deterministic grader currently run.

## Layers and tracks

Ingestion: operating statements, rent rolls, leases/amendments, and provenance.
Understanding: classification, reconciliation, normalized NOI, debt sizing and defensible resolution of conflicting sources.
Work products: functioning underwriting workbooks and reviewable offering memoranda.

Component tests distinguish reading failures from reasoning failures by controlling intermediate facts. End-to-end tests start from original documents. Common-harness models and actual products have separate result panels and disclosed tool/data access. Professional reference work is measured on a reviewed subset. Matched-base comparisons are required for claims about workflow lift.

## Public example

Harbor Court is fictional. Its 12 units include nine active leases, two vacant units and one pending lease. The source summary includes the pending lease. In-place counts and rent must exclude it; historical T-12 rental income need not equal current annualized rent. Both facts and the resolution are explicit in the task.

The key records 27 values and canonical source references. Grade rows separately cover value correctness, reference-set equality, unknown fields, exact conflict set, NOI self-consistency and minimum loan constraint. A result is a development check, never a model score. It is not independently expert-qualified. Source reference equality does not assess the quality of a prose explanation. Declared CSV line references and JSON Pointers are fixed for this example; the initial grader does not implement general document parsing.

## Corpus and truth

Public, development and held-out cases must be disjoint by underlying deal and source template where feasible. Correlated variants are not independent examples. Plan coverage by asset type, source producer, scan/layout quality, reporting period and financing structure; use pilot variance to determine sample requirements.

Independently review material facts and formulas before freeze. Record source references, tolerances, accepted alternatives, unresolved judgments and reviewer identity. Never train/calibrate graders on held-out model outputs. Publish contamination limitations and version refreshed cases separately.

## Financial and artifact scoring

Grade extraction accuracy separately from calculation consistency. Separate unit occupancy from area occupancy; independently check active/pending/vacant and unit-type detail. Penalize both missed and false discrepancies. An unsupported assumption is not a fact. A material error cannot be canceled by a well-designed artifact.

Workbook evaluation requires formula inspection AND recalculation under input perturbations in a declared engine. OM evaluation requires source-grounded figures AND inspection of rendered readability and usability. These artifact validators are on the roadmap, not included in this release.

## Execution and reporting

Freeze cases, prompts, keys, graders, settings, tool boundaries and provider versions before scored execution. Record hashes, raw outputs, errors, cost and latency. Missing output is visible. Infrastructure incidents and replacement runs must be disclosed. Do not choose the best attempt.

Report by task and track: accuracy, material errors, supported evidence, completion, human correction effort where measured, repeated-run reliability, cost and latency. Use paired case comparisons and deal-cluster uncertainty, not rubric-row independence or three-run ranges as confidence intervals.

The public API pilot runner and financial grader are implemented. Artifact validators, independent human qualification, and statistical reporting remain to be completed. See roadmap for their acceptance criteria.

## Cost reporting

Show cost with every run and model summary. Retain exact currency amounts, their source, and the measurement boundary. Per-run costs include attributable failed attempts and retries; exclude no attempt merely because it failed. Separate inference charges, product credits, subscriptions, external tools, and human effort. Do not imply that an inference-only price is the full workflow cost.

Unknown cost stays null or “Not recorded”; it never becomes zero. A provider-reported zero is labeled as reported. Publish model means and totals only when the underlying costs are complete. Do not allocate whole-packet charges to task stages without stage-level metering. Product credits require an attributable event record and a documented conversion before any USD comparison.

A worked solution that invokes no model has no API inference charge. This is distinct from the measured cost of producing an actual model response.
