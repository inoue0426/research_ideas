#!/usr/bin/env python3

import argparse
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_URL = "http://localhost:11434/api/generate"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--output-file", required=True)
    parser.add_argument("--model", default=os.environ.get("OLLAMA_MODEL", "qwen3:30b"))
    parser.add_argument("--url", default=os.environ.get("OLLAMA_URL", DEFAULT_URL))
    parser.add_argument("--timeout", type=int, default=1800)
    args = parser.parse_args()

    prompt = Path(args.prompt_file).read_text(encoding="utf-8")
    payload = {
        "model": args.model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "think": False,
        "options": {"temperature": 0},
    }

    req = urllib.request.Request(
        args.url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            result = json.load(resp)
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Ollama request failed: {exc}") from exc

    text = result.get("response")
    # Compatibility fallback for thinking-capable models/older Ollama behavior.
    if not isinstance(text, str) or not text.strip():
        text = result.get("thinking")

    if not isinstance(text, str) or not text.strip():
        raise RuntimeError(
            "Ollama returned neither response nor thinking text. "
            f"Keys: {sorted(result.keys())}"
        )

    Path(args.output_file).write_text(text.strip() + "\n", encoding="utf-8")
    print(text.strip())


if __name__ == "__main__":
    main()
