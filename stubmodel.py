#!/usr/bin/env python3
"""
stubmodel.py — A local, offline stand-in for an LLM.

CLI contract:
    python stubmodel.py --prompt <file> --input <text|@file>
                        [--temperature 0.0] [--seed N]
                        [--max-tokens 256] [--call-index N]

Outputs one JSON object to stdout:
    {"output": "...", "tokens_in": 92, "tokens_out": 24,
     "finish": "stop", "latency_ms": 340}

Exit codes: 0 ok · 2 bad arguments · 3 prompt or input file unreadable.
"""

import argparse
import json
import sys
import math
import hashlib
import time
import random
from pathlib import Path


def compute_tokens(text: str) -> int:
    """Token rule: ceil(len(text) / 4)."""
    return math.ceil(len(text) / 4)


def classify_ticket(text: str, temperature: float, seed: int | None) -> str:
    """
    Classify a ticket into one of: billing, account, technical, other.

    At temperature 0.0, deterministic based on hash.
    Above 0.0, non-deterministic unless seeded.
    """
    if seed is not None:
        random.seed(seed)

    # Deterministic at temperature 0
    if temperature == 0.0:
        text_hash = hashlib.md5(text.encode()).hexdigest()
        hash_val = int(text_hash[:8], 16)
        categories = ["billing", "account", "technical", "other"]
        chosen = categories[hash_val % len(categories)]
    else:
        # Non-deterministic: random category, influenced by keyword hints
        if any(w in text.lower() for w in ["invoice", "charge", "payment", "refund", "bill"]):
            if random.random() < (1.0 - temperature):
                chosen = "billing"
            else:
                chosen = random.choice(["account", "technical", "other"])
        elif any(w in text.lower() for w in ["login", "account", "password", "access", "user"]):
            if random.random() < (1.0 - temperature):
                chosen = "account"
            else:
                chosen = random.choice(["billing", "technical", "other"])
        elif any(w in text.lower() for w in ["error", "crash", "bug", "slow", "timeout"]):
            if random.random() < (1.0 - temperature):
                chosen = "technical"
            else:
                chosen = random.choice(["billing", "account", "other"])
        else:
            chosen = random.choice(["billing", "account", "technical", "other"])

    return chosen


def main():
    parser = argparse.ArgumentParser(description="Offline LLM stand-in for testing")
    parser.add_argument("--prompt", required=True, help="Path to prompt file")
    parser.add_argument("--input", required=True, help="Input text or @file")
    parser.add_argument("--temperature", type=float, default=0.0, help="Temperature (0.0 = deterministic)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--max-tokens", type=int, default=256, help="Max output tokens")
    parser.add_argument("--call-index", type=int, default=0, help="Call index (for tracing)")
    parser.add_argument("--help-only", action="store_true", help="Print help and exit")

    try:
        args = parser.parse_args()
    except SystemExit as e:
        if e.code != 0:
            sys.exit(2)
        sys.exit(0)

    if args.help_only:
        parser.print_help()
        sys.exit(0)

    # Read prompt
    try:
        prompt_path = Path(args.prompt)
        if not prompt_path.exists():
            print(f"Error: prompt file not found: {args.prompt}", file=sys.stderr)
            sys.exit(3)
        prompt_text = prompt_path.read_text()
    except Exception as e:
        print(f"Error reading prompt: {e}", file=sys.stderr)
        sys.exit(3)

    # Read input
    if args.input.startswith("@"):
        try:
            input_path = Path(args.input[1:])
            if not input_path.exists():
                print(f"Error: input file not found: {args.input[1:]}", file=sys.stderr)
                sys.exit(3)
            input_text = input_path.read_text()
        except Exception as e:
            print(f"Error reading input file: {e}", file=sys.stderr)
            sys.exit(3)
    else:
        input_text = args.input

    # Simulate processing
    start_time = time.time()

    # Generate output based on prompt and input
    if "classify" in prompt_text.lower():
        # Classification task
        category = classify_ticket(input_text, args.temperature, args.seed)
        output = json.dumps({"category": category, "confidence": 0.95})
    else:
        # Default echo-like behavior
        output = input_text[:100] + "..."

    # Truncate to max_tokens if needed
    max_output_len = args.max_tokens * 4  # Rough estimate
    if len(output) > max_output_len:
        output = output[:max_output_len]
        finish = "length"
    else:
        finish = "stop"

    latency_ms = int((time.time() - start_time) * 1000)
    tokens_in = compute_tokens(prompt_text + input_text)
    tokens_out = compute_tokens(output)

    # Output JSON
    result = {
        "output": output,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "finish": finish,
        "latency_ms": latency_ms
    }

    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    main()
