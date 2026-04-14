#!/usr/bin/env python3
"""Exercise 2: TodoWrite / Task Management — Does the CLI provide it?

Question answered: Q1 — Does it provide TodoWrite / task management?

Run: uv run python phase-c/claude-code-cli/ex02_todo_and_tasks.py
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


def run_claude(prompt: str, *, cwd: str, max_turns: int = 15, extra_args: list[str] | None = None) -> list[dict]:
    """Run claude -p and return parsed stream-json messages."""
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "stream-json", "--verbose",
        "--max-turns", str(max_turns),
        "--dangerously-skip-permissions",
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
    """Count tool usage from stream-json messages."""
    counts: Counter[str] = Counter()
    for msg in messages:
        if msg.get("type") == "assistant":
            for block in msg.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    counts[block["name"]] += 1
    return counts


def probe(prompt: str, label: str) -> dict[str, int]:
    """Run a prompt in a temp dir and report tool usage."""
    print(f"\n{'=' * 60}")
    print(f"PROBE: {label}")
    print("=" * 60)

    with tempfile.TemporaryDirectory(prefix="c1_cli_ex02_") as tmpdir:
        messages = run_claude(prompt, cwd=tmpdir)
        tools = extract_tools(messages)

        # Show TodoWrite usage
        if "TodoWrite" in tools:
            for msg in messages:
                if msg.get("type") == "assistant":
                    for block in msg.get("message", {}).get("content", []):
                        if block.get("type") == "tool_use" and block["name"] == "TodoWrite":
                            print(f"  [TodoWrite] {json.dumps(block['input'])[:200]}")

        # Print result
        for msg in messages:
            if msg.get("type") == "result":
                cost = msg.get("total_cost_usd", "N/A")
                print(f"  Result: {msg.get('subtype')}, turns={msg.get('num_turns')}, cost=${cost}")

        print(f"\n  Tools used: {dict(tools)}")
        print(f"  TodoWrite used: {'YES' if 'TodoWrite' in tools else 'NO'} ({tools.get('TodoWrite', 0)} times)")
        return dict(tools)


def main() -> None:
    tools_with = probe(
        prompt=(
            "Create a Python calculator project with:\n"
            "1. calc.py — add, subtract, multiply, divide functions\n"
            "2. test_calc.py — pytest tests for each function\n"
            "3. README.md — document the API\n"
            "Track your progress with todos as you go."
        ),
        label="Multi-step task WITH 'track with todos' instruction",
    )

    tools_without = probe(
        prompt=(
            "Create a Python calculator project with:\n"
            "1. calc.py — add, subtract, multiply, divide functions\n"
            "2. test_calc.py — pytest tests for each function\n"
            "3. README.md — document the API"
        ),
        label="Multi-step task WITHOUT todo instruction",
    )

    print(f"\n{'=' * 60}")
    print("KEY FINDINGS")
    print("=" * 60)
    print(f"  TodoWrite with instruction:    {'YES' if 'TodoWrite' in tools_with else 'NO'}")
    print(f"  TodoWrite without instruction: {'YES' if 'TodoWrite' in tools_without else 'NO'}")
    print()
    if "TodoWrite" in tools_with or "TodoWrite" in tools_without:
        print("  • TodoWrite IS available in CLI")
        if "TodoWrite" in tools_with and "TodoWrite" not in tools_without:
            print("  • Only used when explicitly asked to track todos")
        elif "TodoWrite" in tools_with and "TodoWrite" in tools_without:
            print("  • Used even without explicit instruction — proactive task tracking")
    else:
        print("  • TodoWrite was NOT used in either probe")
        print("  • May need more complex tasks or explicit nudging to trigger it")


if __name__ == "__main__":
    main()
