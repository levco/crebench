# Administrative credit interruption and exact-context resumption

The shared Vercel AI Gateway exhausted its prepaid credit balance during execution and rejected nine workflows with HTTP 402 `insufficient_funds`. Fifteen API workflows had completed. Eight rejected requests were first calls; the ninth was Opus 5 agent / Market Row, at model turn 10 after nine returned model turns.

These are infrastructure interruptions, not model-quality failures. Their original requests, results, partial artifacts and known costs remain in the execution archive. Every interrupted workflow is resumed after credit replenishment; completed workflows are never rerun or selected for a better result.

`crebench/resume_workflow.py` restores the exact rejected request, verifies the wire SHA-256, and continues using the same model, prompts, tools, output limits and remaining turn/tool allowance. Original tool results, self-corrections and artifact-version counters remain. No answer hints or gold data enter the continuation. Resumed API attempts are stored in a separate `billing-resumption` directory; original result snapshots are retained there. The frozen runner, rubric, keys and source files remain unchanged.

The elapsed administrative wait for credit is excluded from the 1,800-second active execution allowance, while the original consumed execution time remains. Reported latency therefore identifies active execution separately from the interruption. HTTP 402 responses contain no token usage; their unknown accounting is not silently represented as zero. Known model-response charges remain visible even when total attributable cost is incomplete.

The user subsequently authorized up to $200 in model tokens without further approval. The original experiment's more conservative $100 request-reservation cap is retained. A prepaid top-up is a credit purchase, not inference consumption, and is reported separately from actual benchmark usage.

The resumption adapter was verified against all nine archived wire requests and all 72 frozen file hashes, and tested with a fake model response to prove retention of context, prior tool counts, artifact versions, consumed time, original files and partial costs before resuming live requests.
