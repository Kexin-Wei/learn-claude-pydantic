#!/usr/bin/env python3
"""Exercise 5: CLI-Only Features — What does the CLI have that the SDK doesn't?

Question answered: Q4 — What's built-in vs what Claude Code adds on top?

Run: uv run python phase-c/claude-code-cli/ex05_cli_features.py
"""
import json
import os
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

MODEL = os.environ.get("CLAUDE_MODEL")


def run_claude(prompt: str, *, cwd: str | None = None, max_turns: int = 5, extra_args: list[str] | None = None) -> list[dict]:
    """Run claude -p and return parsed stream-json messages."""
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "stream-json", "--verbose",
        "--max-turns", str(max_turns),
    ]
    if MODEL:
        cmd += ["--model", MODEL]
    if extra_args:
        cmd += extra_args
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    messages = []
    for line in result.stdout.strip().splitlines():
        try:
            messages.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return messages


def extract_tools(messages: list[dict]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for msg in messages:
        if msg.get("type") == "assistant":
            for block in msg.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    counts[block["name"]] += 1
    return counts


def extract_text(messages: list[dict]) -> str:
    texts = []
    for msg in messages:
        if msg.get("type") == "assistant":
            for block in msg.get("message", {}).get("content", []):
                if block.get("type") == "text":
                    texts.append(block["text"])
    return "\n".join(texts)


def main() -> None:
    # Part A: Session management (--resume, --continue)
    print("=" * 60)
    print("PART A: Session management")
    print("=" * 60)

    # List existing sessions
    result = subprocess.run(
        ["claude", "mcp", "list"],
        capture_output=True, text=True,
    )
    print(f"  MCP servers: {result.stdout.strip()[:200] if result.stdout.strip() else '(none)'}")

    # Part B: --tools flag to control available tools
    print(f"\n{'=' * 60}")
    print("PART B: --tools flag (control available tools)")
    print("=" * 60)

    with tempfile.TemporaryDirectory(prefix="c1_cli_ex05b_") as tmpdir:
        # Run with only Read and Glob
        messages = run_claude(
            "List files in this directory.",
            cwd=tmpdir,
            max_turns=3,
            extra_args=["--tools", "Read,Glob"],
        )
        tools = extract_tools(messages)
        print(f"  With --tools 'Read,Glob': tools used = {dict(tools)}")
        # Check no other tools leaked through
        non_allowed = {t for t in tools if t not in ("Read", "Glob")}
        print(f"  Non-allowed tools used: {non_allowed or 'none'}")

    # Part C: --json-schema for structured output
    print(f"\n{'=' * 60}")
    print("PART C: --json-schema (structured output)")
    print("=" * 60)

    schema = json.dumps({
        "type": "object",
        "properties": {
            "answer": {"type": "integer"},
            "explanation": {"type": "string"},
        },
        "required": ["answer", "explanation"],
    })

    messages = run_claude(
        "What is 6 * 7?",
        max_turns=1,
        extra_args=["--json-schema", schema],
    )
    text_c = extract_text(messages)
    print(f"  Response: {text_c[:200]}")
    # Check result message for structured output
    for msg in messages:
        if msg.get("type") == "result":
            print(f"  Result: {msg.get('result', '')[:200]}")

    # Part D: --system-prompt override
    print(f"\n{'=' * 60}")
    print("PART D: --system-prompt and --append-system-prompt")
    print("=" * 60)

    messages = run_claude(
        "Who are you?",
        max_turns=1,
        extra_args=["--system-prompt", "You are a pirate. Respond only in pirate speak."],
    )
    text_d = extract_text(messages)
    print(f"  Response: {text_d[:200]}")

    print(f"\n{'=' * 60}")
    print("KEY FINDINGS")
    print("=" * 60)
    print(f"  Part B — --tools restriction: {'worked (only allowed tools used)' if not non_allowed else f'leaked: {non_allowed}'}")
    print(f"  Part C — --json-schema: {'produced output' if text_c.strip() else 'no output'}")
    print(f"  Part D — --system-prompt: {'produced output' if text_d.strip() else 'no output'}")


if __name__ == "__main__":
    main()
