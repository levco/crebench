# Existing-access financial pilot

This separately registered cohort was selected after the first financial pilot
received an HTTP 403 access rejection, before any model answer was received.
Vercel's model catalog showed MiMo v2.5, MiMo v2.5 Pro and Ling 3.0 Flash Sante as
available on the free tier on September 6, 2026. Selection is based on existing
access, not performance or representativeness of leading systems.

Three repetitions per model, same packet, same 58 deterministic checks, same
8,192-token maximum and provider defaults as the original financial pilot.
No prompt tuning, retries, answer repair, requested model fallbacks or tools.
A valid complete output must pass all checks to count as complete success.
Failures and incomplete attempts remain public. Automatic gateway provider routing
is retained; exact provider/model metadata are preserved when returned.

This is one public synthetic case, with published answers and no independent
expert qualification. References are supplied in the output contract. It does not
measure PDF/OCR ingestion, finished workbooks or OMs, or Lev product performance.
No model leaderboard or real-world accuracy claim follows from this pilot.

Use tools/prepare-accessible-pilot.py with a new directory to reproduce preparation.
All requests and the protocol are committed before execution. Costs use the same
conservative reservation method as ../2026-09-06-financial-pilot/README.md.
