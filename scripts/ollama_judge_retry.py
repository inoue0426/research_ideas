#!/usr/bin/env python3

import argparse
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_URL = "http://localhost:11434/api/generate"


def extract_expected_pair_ids(prompt: str):
    ids = re.findall(r'"pair_id"\s*:\s*"(p\d+)"', prompt)
    seen = []
    for pair_id in ids:
        if pair_id not in seen:
            seen.append(pair_id)
    return seen


def build_format(expected_pair_ids):
    if not expected_pair_ids:
        return "json"
    n = len(expected_pair_ids)
    return {
        "type": "object",
        "properties": {
            "comparisons": {
                "type": "array",
                "minItems": n,
                "maxItems": n,
                "items": {
                    "type": "object",
                    "properties": {
                        "pair_id": {"type": "string", "enum": expected_pair_ids},
                        "winner": {"type": "string", "enum": ["A", "B", "draw"]},
                        "reason": {"type": "string"},
                    },
                    "required": ["pair_id", "winner", "reason"],
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
        "options": {
            "temperature": 0,
            "num_predict": 4096,
        },
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


def validate_pairwise(text, expected_pair_ids):
    if not expected_pair_ids:
        return True, ""
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON: {exc}"
    comparisons = obj.get("comparisons")
    if not isinstance(comparisons, list):
        return False, "missing comparisons list"
    returned = [x.get("pair_id") for x in comparisons if isinstance(x, dict)]
    if len(returned) != len(expected_pair_ids):
        return False, f"expected {len(expected_pair_ids)} comparisons, got {len(returned)}"
    if set(returned) != set(expected_pair_ids):
        return False, f"expected pair IDs {expected_pair_ids}, got {returned}"
    if len(set(returned)) != len(returned):
        return False, f"duplicate pair IDs: {returned}"
    return True, ""


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
    expected_pair_ids = extract_expected_pair_ids(base_prompt)
    output_format = build_format(expected_pair_ids)

    last_error = ""
    text = ""
    for attempt in range(1, args.retries + 1):
        prompt = base_prompt
        if attempt > 1 and expected_pair_ids:
            prompt += (
                "\n\nIMPORTANT RETRY: Your prior output was incomplete. "
                f"Return exactly {len(expected_pair_ids)} comparisons, one for each pair_id: "
                + ", ".join(expected_pair_ids)
                + ". Do not stop after the first comparison."
            )
        text = call_ollama(args.url, args.model, prompt, args.timeout, output_format)
        ok, last_error = validate_pairwise(text, expected_pair_ids)
        if ok:
            Path(args.output_file).write_text(text + "\n", encoding="utf-8")
            print(text)
            return
        print(f"Ollama output validation failed on attempt {attempt}: {last_error}")

    raise RuntimeError(f"Ollama failed to produce complete pairwise output after {args.retries} attempts: {last_error}")


if __name__ == "__main__":
    main()
