#!/usr/bin/env python3

import argparse
import json
import random
import sys

sys.path.insert(0, "scripts")
import research_elo_core_v2 as research_elo

SEED = 20260824
BATCH_SIZE = research_elo.MAX_OPPONENTS


def build_schedule():
    issues = research_elo.fetch_open_owner_issues()
    numbers = sorted(int(issue["number"]) for issue in issues)
    rng = random.Random(SEED)
    rng.shuffle(numbers)

    batches = []
    pair_count = 0
    for i, target in enumerate(numbers):
        opponents = numbers[i + 1 :]
        rng.shuffle(opponents)
        for start in range(0, len(opponents), BATCH_SIZE):
            chunk = opponents[start : start + BATCH_SIZE]
            if chunk:
                batches.append({"target": target, "opponents": chunk})
                pair_count += len(chunk)

    expected = len(numbers) * (len(numbers) - 1) // 2
    if pair_count != expected:
        raise RuntimeError(f"Round-robin schedule has {pair_count} pairs; expected {expected}")
    return {"seed": SEED, "issues": numbers, "pair_count": pair_count, "batches": batches}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    schedule = build_schedule()
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(schedule, f, indent=2)
        f.write("\n")
    print(f"Round robin: {len(schedule['issues'])} issues, {schedule['pair_count']} unique pairs, {len(schedule['batches'])} batches")


if __name__ == "__main__":
    main()
