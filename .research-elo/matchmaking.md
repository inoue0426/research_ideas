# Research Elo matchmaking

## Bootstrap

The local bootstrap uses a complete single round robin over all open owner-authored research ideas. With `n` ideas this evaluates exactly `n(n-1)/2` unordered pairs, once each. The schedule is deterministically shuffled so online Elo update order is not correlated with GitHub issue number. Prompts are evaluated in batches of up to five comparisons by the fixed local Qwen3 judge.

A clean bootstrap resets every idea to 1500 before the round robin. At completion every idea has exactly `n-1` games and `n-1` distinct opponents.

## Ongoing matchmaking

After bootstrap, scheduled runs remain Elo-style online updates. The target is the least-played idea. Opponents are chosen by:

1. fewest previous meetings for that unordered pair;
2. smallest Elo distance;
3. deterministic random tie-break.

This keeps pair coverage balanced before concentrating additional evidence around close ratings.

## Interpretation

A complete round robin is compatible with Elo; Elo does not require selective matchmaking. Elo remains an online sequential update, so a small order effect remains. The deterministic shuffled bootstrap makes that order reproducible rather than eliminating it. If order-invariant batch estimation becomes important, Bradley-Terry fitting should be treated as a separate rating method rather than silently labeled Elo.
