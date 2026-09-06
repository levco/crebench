# Scoring correction: presentation is not financial accuracy

The initial strict parser rejected all nine accessible-model responses before their
financial contents could be evaluated. This was a harness limitation. Original
responses, errors and records remain immutable; supplemental rescoring applies to
every retained answer, without new model calls or answer-key-driven repairs.

The next six calls use the requested GPT-5 and Claude Opus 5 models, the same case
packet, and the gateway's structured-output schema. The schema supplies field
names and types, never expected values. All six requests and scoring code were
committed before execution at 7ace77c.

While reviewing the first responses, a further presentation defect was found:
`LTV`, `ltv`, and `ltv_limit` were treated as different answers. The binding-constraint
normalizer now recognizes these spellings and the equivalent DSCR and debt-yield
spellings. It applies the same mapping regardless of the correct answer or model.
Duplicate copies of an identical conflict ID are also presentation noise; false
or missing conflict IDs remain financial failures. All affected runs, including
the earlier accessible-model cohort, receive the same supplemental scorer.

## Rules

- Remove a single Markdown JSON fence or surrounding prose.
- Accept flat fields or `{fields: ...}`, scalar values or value/evidence objects.
- Accept unambiguous numeric display strings such as `$150,000` and `75%`.
- Normalize predefined constraint-label spellings without inferring the answer.
- Never calculate or replace a model's numeric value during normalization.
- Never use the answer key to choose among alternative answers.
- Duplicate JSON keys, multiple answer blocks, incomplete JSON and non-finite
  numbers require review rather than silent favorable selection.
- Score 27 values, one conflict-set check and two consistency checks separately
  from 27 reference-compliance checks. Formatting is diagnostic only.
- A missing evidence list does not invalidate an otherwise correct field value.

A result report records original answer hashes, initial execution outcomes and the
supplemental scorer hash. This is an explicitly disclosed development correction,
not a claim that the revised scorer was frozen before these responses.

Structured-output request documentation:
https://vercel.com/docs/ai-gateway/sdks-and-apis/openai-chat-completions/structured-outputs
