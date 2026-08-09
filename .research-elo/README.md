# Research Elo v0

Experimental relative rating for research-idea issues.

## How it works

1. Open **Actions → Research Elo → Run workflow**.
2. Enter an open issue number authored by the repository owner.
3. The workflow selects up to five similarly rated open issues.
4. GitHub Copilot CLI judges each pair, with A/B order randomized.
5. Standard Elo updates are applied with `K = 24`.
6. The target issue receives a comment with its rating, rank, record, and comparison reasons.
7. Rating state is stored in `ratings.json`.

The workflow is manual on purpose for v0. Once the judging behavior is useful and stable, it can be triggered automatically when an issue is created or substantially edited.

## Interpretation

The rating is a **relative LLM-judge signal**, not an objective measure of scientific value. Small differences should not be interpreted literally. The useful outputs are the ranking trend, repeated wins/losses against neighboring ideas, and the judge's reasons.

The judge is instructed not to reward writing length or English polish, and not to invent literature facts. Issue content is treated as untrusted data to reduce prompt-injection risk.
