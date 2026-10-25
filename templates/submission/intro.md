# Gemma 4 Budget-Aware Combined V2

One Gemma 4 31B agent combines three changes to the original Budget-Aware V10:

- Greedy decoding with `temperature: 0`.
- Six native tools: run_command, read_file, edit_file, write_file, get_status and submit_patch.
- Prompt instructions to inspect tool errors, correct arguments and switch approach
  after two failures on the same operation. Identical failed calls must not be
  repeated without a concrete change to their inputs or the source state.

The thinking budget (4,096), output cap (8,192), top-p (0.95), and task limits
(28 calls, 8 minutes, 80 turns, command timeout 240 seconds) match V10.
The system prompt starts from V10; the earlier Verified V1 prompt edits are not included.
Recovery is guided by the model prompt, not enforced by a custom tool callback.

This combined candidate has no measured leaderboard score at build time.
Our earlier V1 scored 0.15 and our exact V10 reproduction scored 0.17;
the upstream V10 score of 0.22 belongs to its author's submission.

Run all cells to build `submission.zip`. Packaging needs no GPU or internet.
The separate GPU notebook checks serving compatibility. Neither packaging nor a
scripted compiler fixture measures Gemma's ability to repair real tasks.

Source: [Igor Zharov / flexonafft, Budget-Aware V10](https://www.kaggle.com/code/flexonafft/gemma-4-budget-aware-coding-agent-v2?scriptVersionId=357955943),
based on matterhorn3838's SuperAgent and the official starter.
Apache-2.0 licensing and attribution are included in the archive.
