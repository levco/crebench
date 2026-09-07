# CRE Work v2: diagnostic results

This is a partial diagnostic release, funded and published by Lev. It is not a practitioner-qualified ranking. All new public packets are synthetic: 20 packets, four shared authoring families, zero authentic customer deals.

Recorded workflow stages: 37; completed: 36; proposed full matrix: 720. The principal comparison contains 8 matched stages from 4 packets, one trial per stage. Initial and revised stages are correlated, not independent transactions.

| System | Ingestion | Financial calculations | Risk flags | Correct sensitivity scenarios | Inference cost |
| --- | --- | --- | --- | --- | --- |
| Lev Agent | 126/144 (87.5%) | 51/96 (53.1%) | 60/64 (93.8%) | 12/24 | $17.79 estimated |
| GPT-5 API agent | 137/144 (95.1%) | 94/96 (97.9%) | 56/64 (87.5%) | 20/24 | ≥ $2.07 |
| Opus 5 API agent | 144/144 (100.0%) | 96/96 (100.0%) | 60/64 (93.8%) | 24/24 | ≥ $19.97 |
| Opus 4.7 API agent | 139/144 (96.5%) | 60/96 (62.5%) | 60/64 (93.8%) | 6/24 | ≥ $11.97 |

Interpretation: compare each column independently. Input accuracy, financial calculations, workbook behavior and cost measure different things. Financial errors can propagate through several dependent outputs; their count is not a count of independent failures. The scoring tolerance is not a practitioner materiality judgment.

## What the Lev results expose

The following values come from unaltered Lev answers and the source-derived reference. Initial GPR was independently re-summed from the actual certified XLSX cells for office, retail and industrial; their reference totals agree. Retail also has an executed $350/month Suite 001 amendment. The instructions explicitly keep stabilized GPR separate from that in-place amendment.

| Packet / stage | Field | Reference | Lev answer | Difference |
| --- | --- | --- | --- | --- |
| in-01 / initial | gross_potential_rent | 1,402,800.00 | 1,401,900.00 | -900.00 |
| in-01 / initial | uw_noi | 902,612.20 | 901,782.85 | -829.35 |
| in-01 / initial | maximum_loan | 9,020,580.43 | 9,012,269.92 | -8,310.51 |
| in-01 / revision | gross_potential_rent | 1,405,500.00 | 1,404,600.00 | -900.00 |
| in-01 / revision | uw_noi | 905,100.25 | 904,270.90 | -829.35 |
| in-01 / revision | maximum_loan | 8,400,193.75 | 8,392,476.00 | -7,717.75 |
| mf-01 / initial | annual_in_place_rent | 894,600.00 | 974,400.00 | +79,800.00 |
| mf-01 / revision | annual_in_place_rent | 920,400.00 | 977,100.00 | +56,700.00 |
| of-01 / initial | gross_potential_rent | 1,618,800.00 | 1,615,200.00 | -3,600.00 |
| of-01 / initial | uw_noi | 1,042,534.20 | 1,039,216.80 | -3,317.40 |
| of-01 / initial | maximum_loan | 8,340,273.60 | 8,313,734.40 | -26,539.20 |
| of-01 / revision | gross_potential_rent | 1,621,500.00 | 1,620,600.00 | -900.00 |
| of-01 / revision | uw_noi | 1,045,022.25 | 1,044,192.90 | -829.35 |
| of-01 / revision | maximum_loan | 8,090,494.84 | 8,084,074.06 | -6,420.78 |
| rt-01 / initial | annual_in_place_rent | 743,100.00 | 735,300.00 | -7,800.00 |
| rt-01 / initial | unit_001_monthly_rent | 7,000.00 | 6,650.00 | -350.00 |
| rt-01 / initial | gross_potential_rent | 818,700.00 | 814,500.00 | -4,200.00 |
| rt-01 / initial | uw_noi | 528,590.05 | 524,720.00 | -3,870.05 |
| rt-01 / initial | maximum_loan | 5,090,126.41 | 5,052,857.00 | -37,269.41 |
| rt-01 / initial | total_area_sf | 32,150.00 | 31,150.00 | -1,000.00 |
| rt-01 / revision | annual_in_place_rent | 745,800.00 | 741,600.00 | -4,200.00 |
| rt-01 / revision | unit_001_monthly_rent | 7,000.00 | 6,650.00 | -350.00 |
| rt-01 / revision | gross_potential_rent | 821,400.00 | 817,200.00 | -4,200.00 |
| rt-01 / revision | uw_noi | 531,078.10 | 527,208.00 | -3,870.10 |
| rt-01 / revision | maximum_loan | 4,931,439.50 | 4,895,501.00 | -35,938.50 |

Lev produced original XLSX and PDF files for all four native packets and their revisions. In retail it corrected an initial area-total error during revision, while retaining the erroneous amendment interpretation. Inspect the original files and field grades to distinguish input selection, arithmetic and artifact behavior. Do not infer that formula-connected files have correct starting assumptions.

## Consumer product and lender checks

Claude Chat used its native tools and displayed Opus 5 High setting on one initial packet and its revision. Its small comparison is displayed separately; it does not restrict the broader Lev/API chart to that one packet. Per-task consumer inference cost is unmeasured. ChatGPT product access was unavailable in the inspected session.

The lender evidence track has 56 recorded runs. It tests a fixed set of eight dated program-evidence probes. Category, source-ID and no-invented-approval checks are automated; they are not full professional explanation scores. The category mismatches involve missing DSCR; the explanations still identify the missing financial information. Native lender-directory ranking remains unmeasured.

## Live research

There are 18 recorded model/brief cells across six research briefs. Completion is separate from source verification. See [source audit](../2026-09-07-live-discovery-v1/SOURCE-AUDIT.md) for supported facts and defects: announcement dates presented as execution dates, a contact-name/email mismatch in a Lev row, a Lev office loan retained despite an acknowledged extension from 2027 to 2029, and a scheduled rent reported without its free-rent concession in a GPT-5 row. Those findings remain visible for both products and APIs. Full returned-set precision and pooled recall remain unmeasured.

## Cost and execution integrity

The cumulative inference-token authorization remains $200: $110 reserved for prior work, $37 workflow APIs, $26 discovery APIs, $2 lender APIs and $25 native products. A one-time $100 gateway credit purchase cost $112.36 including processing fee and tax; auto-reload was off. Funding is separate from inference consumption. Native costs are matched trace estimates, API costs use reported usage, and missing usage remains unknown or a lower bound. Search/data services, subscriptions, indexing and human effort are not included in an all-in price.

This expansion records $81.37 of API-reported inference plus native main-trace estimates. This excludes the prior project reservation and the unmeasured components above. Inspect the [attempt-level cost ledger](cost-ledger.json).

The original credential and balance errors remain recorded. Recovery continued saved conversations with their remaining frozen turn/tool limits; it did not feed reference answers or silently replace bad outputs. Budget stops and missing repetitions are not treated as completed work. The native research brief requests the same search allowance, but the native product is not mechanically capped by the public harness; actual tool parity is not established.

## Remaining qualification

Complete the frozen cohort and repeat trials when funding and access allow; qualify references with two independent CRE reviewers; measure actual correction time and cross-file agreement; audit every research result; run dedicated native lender matching; and qualify authentic, rights-cleared deal packets. Coded original-file review packets and blank score sheets are generated by `tools/build-cre-review-packet.py`. No completed human acceptance or inter-reviewer agreement is claimed.

Scoring v1.1 excludes three ambiguous ratio/capacity fields uniformly, fixes the revised occupancy-risk key and accepts equivalent citation objects. Original v1 grades and all unaltered answers are retained. Citation-location existence does not establish semantic support. See [scoring erratum](SCORING-ERRATUM.md), [rubric](../../benchmarks/cre-work-v2/RUBRIC.md) and [review protocol](../../benchmarks/cre-work-v2/REVIEW-PACKET.md).
