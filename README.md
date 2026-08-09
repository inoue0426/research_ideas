# Research Ideas

A lightweight repository for capturing, developing, comparing, and evaluating research ideas.

The goal is to **store ideas early, sharpen them into falsifiable questions, compare alternatives explicitly, and progressively invest in the best ones** rather than waiting until an idea is fully formed.

The structure is inspired by Michael A. Fischbach's framework for problem choice and decision trees in science and engineering.

<!-- RESEARCH_ELO_START -->
## Research Elo

Relative LLM-judge ranking of open research ideas. Ratings are comparative feedback, **not an objective measure of scientific value**.

| Rank | Issue | Rating | Games | Record |
|---:|---|---:|---:|---:|
| 1 | [#7 — \[Idea\] Uncertainty-aware Drug-conditioned spatial INR](https://github.com/inoue0426/research_ideas/issues/7) | **1524** | 2 | 2W / 0D / 0L |
| 2 | [#3 — \[Idea\] Resolving Conflicting Drug–Target Evidence via TextGrad-Based Mechanism Optimization](https://github.com/inoue0426/research_ideas/issues/3) | **1489** | 3 | 1W / 0D / 2L |
| 3 | [#4 — \[Idea\] CCC + Spatial Transcriptomics + DTI/DRP](https://github.com/inoue0426/research_ideas/issues/4) | **1487** | 3 | 1W / 0D / 2L |

_Updated automatically after owner-authored issues are opened, edited, or reopened. Last update: 2026-08-09 16:26 UTC._
<!-- RESEARCH_ELO_END -->

## Language

Use whichever language helps you think most precisely. The templates are written in English because research questions, literature searches, papers, and collaborations are often conducted in English, but issue responses may be written in Japanese, English, or a mixture of both. Prefer clarity of reasoning over forced translation.

A useful default is:

- **Think and capture in the fastest language** when an idea is fragile or incomplete.
- **Rewrite the one-sentence research question and key claims in English** before deep evaluation, so they can be compared directly with the literature and reused in papers or discussions.
- Do not translate merely for consistency if translation makes the reasoning less precise.

## Workflow

Use **GitHub Issues as the unit of a research idea**.

1. **Capture observations and ideas quickly** — open a `Quick Research Idea` issue as soon as an observation, tension, limitation, or possible direction seems worth remembering.
2. **Separate observation from explanation** — record what was observed before committing to a hypothesis or method.
3. **Develop selectively** — when an idea survives initial thought, rewrite or reopen it using the `Research Idea — Deep Evaluation` template.
4. **Make predictions explicit** — state what should be observed if the hypothesis is correct and what should be observed if it is wrong.
5. **Test assumptions early** — identify the highest-risk assumption and the earliest go/no-go test.
6. **Compare competing questions** — periodically use `Weekly Problem Tournament` to force a choice among multiple plausible directions.
7. **Update the decision tree** — keep the issue alive as the idea changes; do not treat the original formulation as sacred.
8. **Close deliberately** — close ideas that are no longer worth pursuing. A closed issue is a useful decision record, not a failure.

## Suggested issue lifecycle

`raw idea` → `promising` → `evaluating` → `active` → `completed / parked / rejected`

GitHub labels can be added later if this lifecycle becomes useful in practice. The templates intentionally work without any preconfigured labels.

## What makes a useful research-idea issue?

At minimum, it should make these things explicit:

- **Observation** — What did we notice before explaining it?
- **Problem** — What important problem or unresolved tension does this expose?
- **Impact** — If resolved, why would it matter?
- **Hypothesis** — What non-obvious explanation or possibility are we proposing?
- **Prediction** — What observation would distinguish this hypothesis from alternatives?
- **Risk** — What is the most important uncertain assumption?
- **First test** — What is the fastest test that could change our mind?

For ideas worth deeper investment, also evaluate why the problem remains unsolved, competitive advantage, fixed vs. floating parameters, alternative paths, explicit go/no-go criteria, and how the idea compares with other uses of the same research time.

## Templates

### Quick Research Idea

For low-friction capture. It should take only a few minutes to file.

Use this when the idea is still vague, speculative, or triggered by a paper, dataset, observation, limitation, or conversation. Capture the observation separately from the interpretation so that later reasoning is not anchored to the first explanation.

### Research Idea — Deep Evaluation

For ideas that may justify substantial research time. It guides evaluation of:

- observation, problem, and potential impact
- falsifiable hypothesis and predictions
- novelty, competitive landscape, and why the problem remains unsolved
- assumption analysis
- earliest go/no-go experiment
- fixed vs. floating parameters
- decision tree and pivots
- failure modes and weak-success outcomes
- longer-term opportunity

### Weekly Problem Tournament

For training **problem selection**, not just problem evaluation.

Compare 3–5 candidate questions under the same time budget. Score them on importance, novelty, tractability, time-to-learn, and leverage, then force a single current choice. Record why the winner deserves time now and why the alternatives do not.

A useful cadence is:

`5 raw ideas` → `2 quick evaluations` → `1 deep evaluation` → `1 cheapest discriminating experiment` → `kill / continue`

The exact numbers are not important. The forced comparison is.

## Monthly review

Periodically review rejected and parked ideas rather than only successful ones. Look for systematic biases in your decisions:

- Do you repeatedly start from a method rather than a scientific problem?
- Do you overestimate novelty?
- Do you avoid high-impact questions because the first experiment is uncomfortable?
- Do you keep technically successful but scientifically weak projects alive too long?
- Which assumptions most often kill your ideas?

The accumulated decision history is itself an output of this repository.

## Principle

> Spend more time choosing the problem before spending years solving it.

The repository is intended to preserve not only successful ideas, but also abandoned directions, failed assumptions, pivots, comparisons, and reasons for saying no. Over time, that history should become a useful map of how research decisions were made.
