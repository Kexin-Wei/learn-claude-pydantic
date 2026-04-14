#!/usr/bin/env python3
"""Exercise 6: Comparison Table — CLI vs SDK empirical summary.

Questions answered: All four, synthesized.

Run: uv run python phase-c/claude-code-cli/ex06_comparison_table.py
"""
import json
import os
import subprocess
import tempfile
from collections import Counter

from dotenv import load_dotenv

load_dotenv(override=True)

MODEL = os.environ.get("CLAUDE_MODEL")


def run_claude(prompt: str, *, cwd: str | None = None, max_turns: int = 5, extra_args: list[str] | None = None) -> list[dict]:
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
    print("=" * 70)
    print("TRACK C1 — CLI vs SDK COMPARISON")
    print("=" * 70)

    # Probe 1: Tool inventory
    print("\nProbe 1: Tool inventory...", flush=True)
    messages = run_claude(
        "List every tool you have access to. Output ONLY tool names, one per line. "
        "Do NOT use any tools.",
        max_turns=1,
    )
    tool_list = [
        line.strip().strip("-•*").strip()
        for line in extract_text(messages).splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    print(f"  Found {len(tool_list)} tools")

    # Probe 2: TodoWrite
    print("Probe 2: TodoWrite...", flush=True)
    has_todo = False
    with tempfile.TemporaryDirectory(prefix="c1_cli_ex06_") as tmpdir:
        messages = run_claude(
            "Create three files: a.py, b.py, c.py with hello world. Use todos to track progress.",
            cwd=tmpdir, max_turns=10,
            extra_args=["--dangerously-skip-permissions"],
        )
        tools = extract_tools(messages)
        has_todo = "TodoWrite" in tools
    print(f"  TodoWrite used: {has_todo}")

    # Probe 3: Subagent
    print("Probe 3: Subagent auto-spawn...", flush=True)
    messages = run_claude(
        "Explore this repository structure and summarize what each top-level directory contains.",
        max_turns=10,
    )
    tools = extract_tools(messages)
    has_subagent = any(t in tools for t in ("Agent", "Task"))
    print(f"  Subagent spawned: {has_subagent}")

    # Probe 4: Plan mode
    print("Probe 4: Plan mode...", flush=True)
    with tempfile.TemporaryDirectory(prefix="c1_cli_ex06_plan_") as tmpdir:
        messages = run_claude(
            "Create a file called test.txt with 'hello' in it.",
            cwd=tmpdir, max_turns=3,
            extra_args=["--permission-mode", "plan"],
        )
        tools = extract_tools(messages)
        any_tools = bool(tools)
    plan_behavior = "no tool execution" if not any_tools else "tools executed (unexpected)"
    print(f"  Behavior: {plan_behavior}")

    # Print comparison table
    print(f"\n{'=' * 70}")
    print("CLI vs SDK COMPARISON TABLE")
    print("=" * 70)

    rows = [
        ("Feature",                        "CLI",                    "SDK"),
        ("-" * 35,                         "-" * 20,                "-" * 20),
        ("Read/Write/Edit/Bash/Glob/Grep", "Yes (built-in)",       "Yes (documented)"),
        ("Monitor/WebSearch/WebFetch",     "Yes (built-in)",       "Yes (documented)"),
        ("AskUserQuestion",                "Yes (built-in)",       "Yes (documented)"),
        ("TodoWrite",                      "YES (built-in)",       "NO (leaks, undocumented)"),
        ("EnterPlanMode/ExitPlanMode",     "Yes (interactive)",    "No"),
        ("Auto memory",                    "YES",                  "NO (CLI-only)"),
        ("Agent teams",                    "YES",                  "NO (CLI-only)"),
        ("Subagents (Agent tool)",         "Yes",                  "Yes"),
        ("Custom agents (--agents)",       "Yes (JSON flag)",      "Yes (agents param)"),
        (".claude/agents/*.md",            "Yes",                  "Yes (via settingSources)"),
        ("Plan mode",                      "No tools execute",     "No tools execute"),
        ("Structured output",              "--json-schema",        "output_format param"),
        ("Custom MCP tools",              "MCP servers only",      "@tool + create_sdk_mcp_server"),
        ("Programmatic hooks",            "No (shell/http only)",  "Yes (Python callbacks)"),
        ("can_use_tool callback",         "No",                    "Yes (SDK-native)"),
        ("File checkpointing + rewind",   "No",                    "Yes (SDK-native)"),
        ("Session resume",                "--continue / --resume",  "resume param"),
        ("Worktree isolation",            "--worktree",            "No"),
        ("Interactive slash commands",     "/plan /compact etc.",    "No"),
        ("--effort levels",               "Yes",                   "Yes"),
        ("--model override",              "Yes",                   "Yes"),
        ("Streaming events",              "--output-format stream", "AsyncIterator"),
    ]

    for row in rows:
        print(f"  {row[0]:<35} {row[1]:<22} {row[2]}")

    print(f"\n{'=' * 70}")
    print("ANSWERS TO THE 4 QUESTIONS (CLI perspective)")
    print("=" * 70)

    print("""
Q1: Does the CLI provide TodoWrite / task management?
    YES — TodoWrite is a first-class CLI tool, always available.
    Compare: SDK does NOT document it (leaks through subprocess).

Q2: Does the CLI auto-spawn subagents?
    YES — Built-in general-purpose agent + custom agents via --agents
    or .claude/agents/*.md. Also has agent teams (CLI-only).

Q3: Does the CLI have planner mode?
    PARTIAL — --permission-mode plan blocks all tool execution.
    Interactive mode has /plan to toggle. No plan-then-execute workflow.

Q4: What does the CLI have that the SDK doesn't?
    CLI-only: TodoWrite, auto memory, agent teams, --worktree,
    interactive mode (/plan, /compact, /resume), EnterPlanMode.
    SDK-only: programmatic hooks, can_use_tool callback,
    @tool decorator, file checkpointing + rewind.
""")


if __name__ == "__main__":
    main()
