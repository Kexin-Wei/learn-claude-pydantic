#!/usr/bin/env python3
"""Exercise 4: Plan Mode — Does the CLI have plan-then-execute?

Question answered: Q3 — Does it have planner mode / plan-then-execute?

Run: uv run python phase-c/claude-code-cli/ex04_plan_mode.py
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

TASK_PROMPT = (
    "Create a Python module called 'stats.py' with functions for mean, median, "
    "and standard deviation. Then create 'test_stats.py' with pytest tests."
)


def run_claude(prompt: str, *, cwd: str, max_turns: int = 5, extra_args: list[str] | None = None) -> list[dict]:
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
    # Part A: --permission-mode plan
    print("=" * 60)
    print("PART A: --permission-mode plan")
    print("=" * 60)

    with tempfile.TemporaryDirectory(prefix="c1_cli_ex04a_") as tmpdir:
        messages = run_claude(
            TASK_PROMPT,
            cwd=tmpdir,
            extra_args=["--permission-mode", "plan"],
        )
        tools = extract_tools(messages)
        text = extract_text(messages)

        for msg in messages:
            if msg.get("type") == "result":
                print(f"  Result: {msg.get('subtype')}, turns={msg.get('num_turns')}")
                if msg.get("stop_reason"):
                    print(f"  Stop reason: {msg.get('stop_reason')}")

        print(f"\n  Tools used: {dict(tools)}")
        any_tools = bool(tools)
        print(f"  Any tools executed: {'YES' if any_tools else 'NO'}")
        if text:
            # Show first 300 chars of response
            print(f"  Response preview: {text[:300]}...")
        print("  → Plan mode = plan-then-execute. In headless (-p) mode, plan auto-approves.")

    # Part B: --effort levels
    print(f"\n{'=' * 60}")
    print("PART B: --effort levels (low vs high)")
    print("=" * 60)

    for effort in ("low", "high"):
        with tempfile.TemporaryDirectory(prefix=f"c1_cli_ex04_{effort}_") as tmpdir:
            messages = run_claude(
                "What is 2 + 2? Answer in one word.",
                cwd=tmpdir,
                max_turns=1,
                extra_args=["--effort", effort],
            )
            text = extract_text(messages)
            for msg in messages:
                if msg.get("type") == "result":
                    cost = msg.get("total_cost_usd", "N/A")
                    print(f"  [{effort}] Answer: {text.strip()[:50]}, cost=${cost}, duration={msg.get('duration_ms')}ms")

    print(f"\n{'=' * 60}")
    print("KEY FINDINGS")
    print("=" * 60)
    if "ExitPlanMode" in tools:
        print("  • --permission-mode plan: plan-then-execute flow confirmed (ExitPlanMode called)")
    elif not any_tools:
        print("  • --permission-mode plan: no tools executed (planned only)")
    else:
        print(f"  • --permission-mode plan: tools executed without ExitPlanMode: {dict(tools)}")


if __name__ == "__main__":
    main()
