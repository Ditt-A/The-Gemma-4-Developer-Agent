# Gemma 4 Budget-Aware Verified V1

A single Gemma 4 31B agent with bounded navigation, exact-source editing and
verification after the final edit. Its public score is **0.15**, from submission
57549113, confirmed on 24 October 2026.
The upstream public score of 0.22 belongs to flexonafft V10 and is not a result
for this notebook.

The model, sampler, nine native tools and 28-call / 8-minute task limits remain
identical to that source. Changes are confined to its system prompt: preserve
verification for the final revision, distinguish real failures from environment
problems, retain command exit codes, and stop promptly after submission.

Run all cells to build `submission.zip`. No training data, credentials, inference
server or internet access is required to package the agent. A separate Kaggle
L4x4 notebook is provided for GPU compatibility checks; the historical short run
did not complete inference. The per-task cap
does not guarantee that every hidden task fits within the global 12-hour limit.

Sources and Apache-2.0 attribution are included in the archive's `NOTICE.txt`.
