# Research release figure contract

Delivery: reusable SVG and PNG research figures, embedded in the existing CRE Bench website, plus the underlying public CSV/JSON. The figures are static publication artifacts; the site's case selector provides the interactive audit. Render from recorded results only.

| Figure | Question | Form and grain | Denominator / limits |
|---|---|---|---|
| research-agent-quality | Can native and general agents return verified comp/lead shortlists? | Four task panels, three horizontal bars each | Six synthetic cases per task; verified/available requested slots, four empty cases reported separately |
| research-direct-quality | How does Lev compare with direct foundation-model calls? | Four task panels, Lev plus two direct controls | Same supplied text; direct controls have no tools or file requirement |
| research-screening | Which systems correctly accept and reject the candidate records? | Four task panels, five labeled bars | 120 decisions per task and system, including zero-match cases; not independent observations |
| research-cost | What did each full condition cost? | Five horizontal bars | All 24 attempts per condition; gateway-reported API charges vs trace-estimated Lev inference, no retail price claim |
| research-material-errors | How often did the shortlist contain a consequential error? | Five horizontal bars | Cases with at least one material finding out of 24, with total findings labeled; repeated cases can expose one cause |
| research-case-matrix | Where do errors cluster? | 24 by 5 annotated screening matrix | 20 candidate decisions per cell; percentages and family separators, no confidence intervals |

Scales: all bar percentages begin at 0 and end at 100, with an outside label showing numerator/denominator. Cost axis begins at zero. No average blends document, financial, screening, and delivery checks into an overall winner. The matrix uses one sequential scale and explicit 0-100 legend.

Palette: retain the established website's Lev forest (#08331F), GPT blue (#3B69BC), and Opus terracotta (#B56750). Direct controls use open, hatched bars with labeled rows. Category identity is deliberate; no redundant legend on directly labeled bars. White background, quiet grid, readable dark labels. These are Lev-owned figures with Lev branding in the surrounding page and publisher credit in each figure, not OpenAI-branded research.

QA: inspect exported PNGs, desktop and mobile website layouts, text labels, links and data consistency. All 120 planned rows must exist. Final exports require all 120 attempts finished and all answer-bearing runs graded. Four template families with six variants are not 24 independent real deals. Independent practitioner review remains pending.

Artifact inspection maps semantically equivalent column headings uniformly (for example $/SF and PSF). It does not alter model files or values. Blank CSV/XLSX cells fail the brief's explicit-unknown annotation requirement; this is a delivery issue, not a fabricated numeric claim. All four artifact checks and any mapper limitations are inspectable per run.

Final audit: scoring v1.1 corrects unit-labeled wrappers and accurate source-proven parent/SPV annotations; v1 grades and the original frozen grader remain public. One GPT-5 direct run timed out twice: 119 answers / 120 attempted conditions. Unanswered target slots and decisions remain in aggregate success denominators, while factual-error rates use returned-answer counts. GPT-5 direct cost is a lower bound; two timeout charges are unknown. Native internal execution has partial audit coverage and is not a confirmed common-corpus pass.
