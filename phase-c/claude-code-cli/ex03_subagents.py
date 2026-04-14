#!/usr/bin/env python3
"""Exercise 3: Subagents — Auto-spawn vs manual orchestration via CLI.

Question answered: Q2 — Does it auto-spawn subagents or require manual orchestration?

Run: uv run python phase-c/claude-code-cli/ex03_subagents.py
"""
import json
import os
import subprocess
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

WORKDIR = Path(__file__).parent.parent.parent  # repo root
MODEL = os.environ.get("CLAUDE_MODEL")


def run_claude(prompt: str, *, max_turns: int = 10, extra_args: list[str] | None = None) -> list[dict]:
    """Run claude -p and return parsed stream-json messages."""
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "stream-json",
        "--max-turns", str(max_turns),
    ]
    if MODEL:
        cmd += ["--model", MODEL]
    if extra_args:
        cmd += extra_args
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(WORKDIR))
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


def main() -> None:
    # Part A: Does the CLI auto-spawn subagents?
    print("=" * 60)
    print("PART A: Auto-spawn subagents?")
    print("=" * 60)

    messages = run_claude(
        "Analyze this repository: first explore the directory structure, "
        "then read 2-3 key files, then write a 3-sentence summary of what "
        "this project is about. Work efficiently.",
    )
    tools = extract_tools(messages)
    agent_used = any(t in tools for t in ("Agent", "Task"))

    # Check for task system messages
    task_events = [m for m in messages if m.get("type") == "system" and "task" in m.get("subtype", "")]

    for msg in messages:
        if msg.get("type") == "result":
            print(f"  Result: {msg.get('subtype')}, turns={msg.get('num_turns')}")

    print(f"\n  Tools: {dict(tools)}")
    print(f"  Agent/Task tool used: {'YES' if agent_used else 'NO'}")
    print(f"  Task system events: {len(task_events)}")

    # Part B: Custom agents via --agents flag
    print(f"\n{'=' * 60}")
    print("PART B: Custom agents via --agents flag")
    print("=" * 60)

    agents_json = json.dumps({
        "researcher": {
            "description": "Explores codebases and summarizes findings",
            "prompt": "You are a code researcher. Explore and report concisely.",
            "tools": ["Bash", "Read", "Glob", "Grep"],
            "model": "haiku",
        },
    })

    messages = run_claude(
        "Use the researcher agent to explore this repo and list all Python files.",
        extra_args=[
            "--agents", agents_json,
            "--allowed-tools", "Read", "Glob", "Grep", "Agent",
        ],
    )
    tools = extract_tools(messages)
    agent_used = any(t in tools for t in ("Agent", "Task"))

    for msg in messages:
        if msg.get("type") == "result":
            print(f"  Result: {msg.get('subtype')}, turns={msg.get('num_turns')}")

    print(f"\n  Tools: {dict(tools)}")
    print(f"  Agent tool used: {'YES' if agent_used else 'NO'}")

    print(f"\n{'=' * 60}")
    print("KEY FINDINGS")
    print("=" * 60)
    print("  CLI subagent capabilities:")
    print("    • --agents flag: define custom agents as JSON")
    print("    • .claude/agents/*.md: filesystem-based agent definitions")
    print("    • Built-in general-purpose agent auto-spawns when needed")
    print("    • Agent teams: CLI-only multi-instance coordination")
    print("  Compare with SDK:")
    print("    • SDK has same AgentDefinition + agents param")
    print("    • Agent teams are CLI-only (not available in SDK)")


if __name__ == "__main__":
    main()
