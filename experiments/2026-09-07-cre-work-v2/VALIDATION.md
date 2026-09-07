# Publication validation — September 7, 2026

- 90 automated repository tests passed, including independent sums from the
  actual certified rent-roll cells for all 20 packets and both stages.
- All 358 frozen input, reference and execution-code hashes across the three
  new protocols matched their original manifests.
- Publication checks verified 37 workflow records, 36 completed stages, original
  artifact hashes, derived workbook audits and eight common stage/case pairs.
- Site checks verified 551 local links/assets, score arithmetic, figure-to-data
  hashes, original file hashes and public-only output.
- Desktop charts and the case filter were inspected in Chrome. The standalone
  vertical charts were visually inspected. The browser's temporary viewport
  override did not produce a verified phone-width page, so a complete mobile
  browser acceptance check is not claimed. The override was reset.
- Text scans of the public expansion files found no credential, signed-link,
  test-account email or customer-package markers. An apparent API-key substring
  inside opaque provider reasoning ciphertext was a false positive; original
  response bytes were preserved.
- All paid execution processes settled before final cost reconciliation. The
  live-research bridge was stopped. No automatic credit reload was enabled.

Reproduce the local publication checks with the dependencies in the README:

```sh
python3 -m unittest discover -s tests -v
python3 tools/check-expansion.py
npm run build
npm run check:site
```

The supplemental publication manifest is a post-execution integrity snapshot.
It must not be presented as proof of preregistration or independent review.
The original pre-execution manifests and later scoring/budget amendments remain
separate. Human acceptance, correction time, full research-source precision and
dedicated native lender-directory ranking remain unmeasured.
