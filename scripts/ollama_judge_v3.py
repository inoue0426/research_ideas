#!/usr/bin/env python3

import argparse
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_URL = "http://localhost:11434/api/generate"


def extract_pairs(prompt: str):
    match = re.search(r"\nPAIRS:\n(.*?)\n\nReturn STRICT JSON", prompt, flags=re.S)
    if not match:
        raise RuntimeError("Could not extract PAIRS JSON from prompt")
    pairs = json.loads(match.group(1))
    if not isinstance(pairs, list) or not pairs:
        raise RuntimeError("PAIRS must be a non-empty list")
    return pairs


def build_format(pairs):
    pair_ids = [p["pair_id"] for p in pairs]
    issue_ids = sorted({int(p["A"]) for p in pairs} | {int(p["B"]) for p in pairs})
    return {
        "type": "object",
        "properties": {
            "comparisons": {
                "type": "array",
                "minItems": len(pairs),
                "maxItems": len(pairs),
                "items": {
                    "type": "object",
                    "properties": {
                        "pair_id": {"type": "string", "enum": pair_ids},
                        "winner_issue": {"type": "integer", "enum": [0] + issue_ids},
                        "reason": {"type": "string"},
                    },
                    "required": ["pair_id", "winner_issue", "reason"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["comparisons"],
        "additionalProperties": False,
    }


def call_ollama(url, model, prompt, timeout, output_format):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": output_format,
        "think": False,
        "options": {"temperature": 0, "num_predict": 4096},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.load(resp)
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Ollama request failed: {exc}") from exc

    text = result.get("response")
    if not isinstance(text, str) or not text.strip():
        text = result.get("thinking")
    if not isinstance(text, str) or not text.strip():
        raise RuntimeError(
            "Ollama returned neither response nor thinking text. "
            f"Keys: {sorted(result.keys())}"
        )
    return text.strip()


def validate_and_translate(text, pairs):
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc}"

    comparisons = obj.get("comparisons")
    if not isinstance(comparisons, list):
        return None, "missing comparisons list"

    by_id = {p["pair_id"]: p for p in pairs}
    returned = {}
    for comp in comparisons:
        if not isinstance(comp, dict):
            return None, "comparison is not an object"
        pair_id = comp.get("pair_id")
        if pair_id in returned:
            return None, f"duplicate pair_id: {pair_id}"
        returned[pair_id] = comp

    if set(returned) != set(by_id):
        return None, f"expected pair IDs {sorted(by_id)}, got {sorted(returned)}"

    translated = []
    for pair in pairs:
        comp = returned[pair["pair_id"]]
        a = int(pair["A"])
        b = int(pair["B"])
        winner_issue = comp.get("winner_issue")
        reason = str(comp.get("reason", "")).strip()

        if winner_issue == 0:
            winner = "draw"
        elif winner_issue == a:
            winner = "A"
        elif winner_issue == b:
            winner = "B"
        else:
            return None, (
                f"{pair['pair_id']}: winner_issue {winner_issue} is not one of "
                f"the paired issues #{a}/#{b} or 0"
            )

        # Make winner/reason contradictions much easier to catch and audit.
        if winner_issue != 0 and f"#{winner_issue}" not in reason:
            return None, (
                f"{pair['pair_id']}: reason must explicitly name winning issue "
                f"#{winner_issue}; got {reason!r}"
            )

        translated.append({
            "pair_id": pair["pair_id"],
            "winner": winner,
            "reason": reason,
        })

    return {"comparisons": translated}, ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--output-file", required=True)
    parser.add_argument("--model", default=os.environ.get("OLLAMA_MODEL", "qwen3:30b"))
    parser.add_argument("--url", default=os.environ.get("OLLAMA_URL", DEFAULT_URL))
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--retries", type=int, default=3)
    args = parser.parse_args()

    base_prompt = Path(args.prompt_file).read_text(encoding="utf-8")
    pairs = extract_pairs(base_prompt)
    output_format = build_format(pairs)

    numeric_instructions = """

IMPORTANT OUTPUT RULES FOR THIS RUN:
- Ignore the A/B labels when expressing the final winner.
- For each pair, return winner_issue as the exact numeric GitHub issue number that deserves the research time.
- Use winner_issue = 0 only for a draw.
- The reason MUST explicitly name the selected winner as #<issue number> and explain why it wins over the other issue.
- Never write a reason that praises one issue while selecting the other.
- Return one result for every pair_id and no extra prose.
"""

    last_error = ""
    for attempt in range(1, args.retries + 1):
        prompt = base_prompt + numeric_instructions
        if attempt > 1:
            prompt += (
                "\nRETRY: Your previous output failed consistency validation. "
                "Re-check every winner_issue against its reason before returning JSON."
            )

        text = call_ollama(args.url, args.model, prompt, args.timeout, output_format)
        translated, last_error = validate_and_translate(text, pairs)
        if translated is not None:
            output = json.dumps(translated, ensure_ascii=False)
            Path(args.output_file).write_text(output + "\n", encoding="utf-8")
            print(output)
            return
        print(f"Ollama output consistency validation failed on attempt {attempt}: {last_error}")

    raise RuntimeError(
        f"Ollama failed to produce consistent pairwise output after {args.retries} attempts: {last_error}"
    )


if __name__ == "__main__":
    main()
