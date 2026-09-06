# Financial pilot: corrected scoring

One public fictional case. Every retained response is included. Formatting is diagnostic; financial and source-reference checks are separate.

| Model | Run | Financial checks | Reference checks | Seconds |
|---|---|---|---|---|
| xiaomi/mimo-v2.5 | r1-1 | 23/30 | 9/27 | 37.929 |
| xiaomi/mimo-v2.5-pro | r1-2 | 29/30 | 27/27 | 126.192 |
| inclusionai/ling-3.0-flash-sante | r1-3 | 29/30 | 0/27 | 18.37 |
| xiaomi/mimo-v2.5 | r2-1 | 29/30 | 27/27 | 116.86 |
| xiaomi/mimo-v2.5-pro | r2-2 | 28/30 | 0/27 | 101.156 |
| inclusionai/ling-3.0-flash-sante | r2-3 | 29/30 | 0/27 | 28.147 |
| xiaomi/mimo-v2.5 | r3-1 | 29/30 | 27/27 | 65.371 |
| xiaomi/mimo-v2.5-pro | r3-2 | 29/30 | 27/27 | 90.159 |
| inclusionai/ling-3.0-flash-sante | r3-3 | 29/30 | 0/27 | 19.01 |

## Financial failures

- r1-1 (xiaomi/mimo-v2.5): occupied_units, occupied_area_sf, unit_occupancy_pct, area_occupancy_pct, annual_in_place_rent, studio_occupied_units, conflicts.exact_set
- r1-2 (xiaomi/mimo-v2.5-pro): conflicts.exact_set
- r1-3 (inclusionai/ling-3.0-flash-sante): conflicts.exact_set
- r2-1 (xiaomi/mimo-v2.5): conflicts.exact_set
- r2-2 (xiaomi/mimo-v2.5-pro): operating_revenue, noi
- r2-3 (inclusionai/ling-3.0-flash-sante): conflicts.exact_set
- r3-1 (xiaomi/mimo-v2.5): conflicts.exact_set
- r3-2 (xiaomi/mimo-v2.5-pro): conflicts.exact_set
- r3-3 (inclusionai/ling-3.0-flash-sante): conflicts.exact_set

## Interpretation

The 30 financial checks are 27 values, one exact conflict-set check and two consistency checks. They are correlated checks on one case, not 30 independent transactions. The 27 reference checks measure the supplied canonical references, not evidence discovery. No statistical ranking is supported by three repetitions on one case.

All raw responses and original execution outcomes remain unchanged. The supplemental scorer removes presentation wrappers and recognizes equivalent constraint labels. It never computes missing answers or replaces incorrect numbers. The scoring correction was developed after inspecting earlier responses and applies to all runs; it was not preregistered before their generation.

See [the correction policy](../../docs/scoring-correction-2026-09-06.md) and [the machine-readable report](financial-v2.json) for normalization logs, exact failed checks and hashes.
