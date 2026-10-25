# Exact reproduction: Budget-Aware V10

This notebook reproduces the four-file `submission.zip` from
[flexonafft V10](https://www.kaggle.com/code/flexonafft/gemma-4-budget-aware-coding-agent-v2?scriptVersionId=357955943).
It was the highest-scoring public Code notebook when checked on 24 October 2026,
with a linked public score of **0.22**. Our submission 57577673 scored **0.17**,
confirmed on 25 October 2026. The artifact was reproduced; the 0.22 score was not.

The prompt, model, nine tools, sampling and evaluation configuration are unchanged.
The final cell requires a byte-for-byte identical ZIP: 3,713 bytes, SHA-256
`6ff73d104725cc31deadd18787f3f55e5ce534889cec82387e3b280637d34887`.
No V1 prompt edits or additional archive members are included.

Run all cells to build `/kaggle/working/submission.zip`. Packaging needs no GPU,
model download or network access. Gemma inference happens during competition evaluation.
The repository also retains our separate V1 experiment, whose public score was 0.15.

Original attribution: Igor Zharov / flexonafft; based on matterhorn3838's
[Gemma 4 SuperAgent](https://www.kaggle.com/code/matterhorn3838/gemma-4-superagent),
which credits the official starter and community graph-tool investigations.
Apache-2.0 licensing and credits are preserved in the repository LICENSE and NOTICE.txt.
