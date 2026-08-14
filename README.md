# Research Ideas

A lightweight repository for capturing, developing, comparing, and evaluating research ideas.

The goal is to **store ideas early, sharpen them into falsifiable questions, compare alternatives explicitly, and progressively invest in the best ones** rather than waiting until an idea is fully formed.

The structure is inspired by Michael A. Fischbach's framework for problem choice and decision trees in science and engineering.

<!-- RESEARCH_ELO_START -->
## Research Elo

Relative LLM-judge ranking of open research ideas. Ratings are comparative feedback, **not an objective measure of scientific value**.

- Ratings within **20 points** are shown as approximate ties.
- Issues remain **Provisional** until they have at least **10 games**.
- **Δ7d** compares the current rating with the latest stored snapshot at least 7 days old; it shows **—** until enough history exists.
- **Opp.** is the number of distinct opponents an issue has faced.
- Small rating changes should not be interpreted as meaningful differences in scientific quality.

| Rank | Issue | Rating | Δ7d | Games | Opp. | Status | Record |
|---:|---|---:|---:|---:|---:|---|---:|
| 1 | [#19 — \[Idea\] When does perturbation transfer fail across biological domains?](https://github.com/inoue0426/research_ideas/issues/19) | **1557** | — | 10 | 9 | 🟢 Established | 10W / 0D / 0L |
| ≈2 | [#4 — \[Idea\] When does the spatial microenvironment override cell-intrinsic drug sensitivity?](https://github.com/inoue0426/research_ideas/issues/4) | **1525** | — | 25 | 14 | 🟢 Established | 15W / 0D / 10L |
| ≈2 | [#11 — \[Idea\] Intervention geometry may transfer better than state geometry](https://github.com/inoue0426/research_ideas/issues/11) | **1523** | — | 6 | 6 | 🟡 Provisional | 5W / 0D / 1L |
| ≈2 | [#13 — \[Idea\] What makes a representation preserve intervention geometry?](https://github.com/inoue0426/research_ideas/issues/13) | **1523** | — | 6 | 6 | 🟡 Provisional | 5W / 0D / 1L |
| ≈2 | [#15 — \[Idea\] Mechanism arbitration under conflicting evidence](https://github.com/inoue0426/research_ideas/issues/15) | **1522** | — | 6 | 6 | 🟡 Provisional | 5W / 0D / 1L |
| ≈2 | [#12 — \[Idea\] Context-aware chemical ↔ genetic shared perturbation space](https://github.com/inoue0426/research_ideas/issues/12) | **1515** | — | 12 | 12 | 🟢 Established | 7W / 1D / 4L |
| ≈2 | [#21 — \[Idea\] Can response-relevant perturbation geometry be separated from mechanistically faithful perturbation geometry?](https://github.com/inoue0426/research_ideas/issues/21) | **1505** | — | 6 | 5 | 🟡 Provisional | 3W / 1D / 2L |
| ≈8 | [#16 — \[Idea\] Foundation models as enablers of otherwise impossible cross-domain translation](https://github.com/inoue0426/research_ideas/issues/16) | **1505** | — | 10 | 8 | 🟢 Established | 5W / 1D / 4L |
| ≈8 | [#20 — \[Idea\] Is there a compositional algebra of biological perturbations?](https://github.com/inoue0426/research_ideas/issues/20) | **1488** | — | 8 | 7 | 🟡 Provisional | 3W / 0D / 5L |
| ≈10 | [#10 — \[Idea\] What biological structures remain transferable across domain shifts?](https://github.com/inoue0426/research_ideas/issues/10) | **1480** | — | 17 | 9 | 🟢 Established | 6W / 1D / 10L |
| ≈10 | [#14 — \[Idea\] Shared causal geometry across biological modalities](https://github.com/inoue0426/research_ideas/issues/14) | **1477** | — | 10 | 8 | 🟢 Established | 3W / 0D / 7L |
| ≈10 | [#9 — \[Idea\] Dataset generation for drug response/target interaction mechanism](https://github.com/inoue0426/research_ideas/issues/9) | **1477** | — | 16 | 14 | 🟢 Established | 6W / 0D / 10L |
| ≈10 | [#7 — \[Idea\] Uncertainty-aware Drug-conditioned spatial INR](https://github.com/inoue0426/research_ideas/issues/7) | **1476** | — | 18 | 14 | 🟢 Established | 5W / 2D / 11L |
| ≈10 | [#17 — \[Idea\] Human-in-the-loop mechanism refinement](https://github.com/inoue0426/research_ideas/issues/17) | **1471** | — | 9 | 7 | 🟡 Provisional | 2W / 0D / 7L |
| 15 | [#3 — \[Idea\] Resolving Conflicting Drug–Target Evidence via TextGrad-Based Mechanism Optimization](https://github.com/inoue0426/research_ideas/issues/3) | **1456** | — | 13 | 9 | 🟢 Established | 3W / 0D / 10L |

_Updated automatically by Research Elo workflows. Last update: 2026-08-14 17:32 UTC._
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
