# Lev native workflow pilot

## Observed outcome

The first deal-context attempt could not read the source files and did not produce financial answers. Directly attaching the same four source files to that chat restored access. No source values or Index facts were corrected by the operator. The recovery produced 24 of the 27 public-key fields; all 24 agree with the key. Three total-unit-by-type fields were not requested by this product prompt and are not silently inferred from the source.

This is a retrospective, publisher-run review of one recovery response, not an independent benchmark score or a fair ranking against the API models. The full 30-check API score is not assigned to this prose response.

## Financial field comparison

Every public-key field is listed. Response locations below refer to the preserved [assistant response excerpt](recovery-response.dom.txt). [Machine-readable observations](observations.json) retain the transcription and semantic mapping for review.

| Field | Public key | Lev recovery observation |
|---|---|---|
| operating_revenue | 246000 | 246000 |
| operating_expenses | 96000 | 96000 |
| noi | 150000 | 150000 |
| total_units | 12 | 12 |
| occupied_units | 9 | 9 |
| vacant_units | 2 | 2 |
| pending_units | 1 | 1 |
| total_area_sf | 8400 | 8400 |
| occupied_area_sf | 6500 | 6500 |
| unit_occupancy_pct | 75 | 75 |
| area_occupancy_pct | 77.38 | 77.38 |
| annual_in_place_rent | 177600 | 177600 |
| studio_total_units | 4 | Not requested / not reported |
| studio_occupied_units | 2 | 2 |
| 1br_total_units | 4 | Not requested / not reported |
| 1br_occupied_units | 4 | 4 |
| 2br_total_units | 4 | Not requested / not reported |
| 2br_occupied_units | 3 | 3 |
| reported_occupied_units | 10 | 10 |
| reported_occupied_area_sf | 7000 | 7000 |
| reported_annual_in_place_rent | 192000 | 192000 |
| ltv_limit | 1560000 | 1560000 |
| dscr_limit | 1714286 | 1714285.71 |
| debt_yield_limit | 1666667 | 1666666.67 |
| max_loan | 1560000 | 1560000 |
| binding_constraint | ltv | ltv |
| resolution | exclude_pending_from_in_place | exclude_pending_from_in_place |

## Workflow and narrative findings

- Original mixed upload failed; CSV upload succeeded; JSON files were accepted after an explicitly disclosed, byte-preserving extension change to TXT.
- Native Index did not show extracted financial facts. A missing property-address prerequisite is a possible setup confounder, so this does not establish the cause of the failure.
- The initial deal-context analysis reported unreadable sources. The full-run reliability result preserves this failure; recovery is not first-pass success.
- The recovered response reconciles the three reported-versus-active figures but calls them "No genuine conflicts". Conflict terminology requires a product-appropriate rubric.
- It labels calculated NOI "as-reported" and flags historical-versus-current rent for further review. Arithmetic correctness does not resolve these provenance and interpretation questions.
- Workbook and OM generation were explicitly excluded from these prompts and remain untested.

## Cost and comparability

Lev USD inference cost, attributable full-run credits, and precise execution latency were not captured. They are unknown, not zero. An account-level extraction debit without deal or conversation attribution is insufficient to price this workflow. Do not convert platform credits into API inference dollars without a documented conversion and complete event attribution.

The API cohort used inline text, a structured schema, no tools, and three repetitions per model. Lev used native product tools, a prose prompt, a blocked initial attempt, and a direct-attachment recovery in the same conversation. The prompt did not request the three total-unit-by-type fields. This difference prevents an equal-conditions score comparison.

## Evidence and disclosure

The public response is an exact slice of the captured accessibility/DOM text for the final assistant answer. Page chrome, account information, and earlier messages are excluded. The original private capture is retained, with its SHA-256 recorded in observations.json. No model values were edited in the public excerpt. The two categorical observations are explicitly labeled manual semantic mappings.

The [initial prompt](analysis-prompt.txt), [recovery prompt](recovery-prompt.txt), and [input mapping and artifact hashes](manifest.json) are public. The underlying model version and deployed product revision were not captured. The original source packet is public; the JSON-to-TXT content-preserving change is disclosed. No answer key or expected values were supplied to Lev. Lev owns and publishes this evaluation; independent practitioner review is pending.
