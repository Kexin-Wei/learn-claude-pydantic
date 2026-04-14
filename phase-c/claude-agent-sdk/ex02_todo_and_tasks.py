#!/usr/bin/env python3
"""Exercise 2: TodoWrite / Task Management — Does the SDK provide it?

Question answered: Q1 — Does it provide TodoWrite / task management?

Run: uv run python phase-c/claude-agent-sdk/ex02_todo_and_tasks.py
"""
import asyncio
import os
import tempfile
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    SystemMessage,
    TaskNotificationMessage,
    TaskProgressMessage,
    TaskStartedMessage,
    TextBlock,
    ToolUseBlock,
    UserMessage,
    query,
)

load_dotenv(override=True)

MODEL = os.environ.get("CLAUDE_MODEL")


async def probe_todowrite(prompt: str, label: str) -> dict[str, int]:
    """Run a prompt and count which tools are used, watching for TodoWrite."""
    print(f"\n{'=' * 60}")
    print(f"PROBE: {label}")
    print(f"Prompt: {prompt!r}")
    print("=" * 60)

    tool_counts: Counter[str] = Counter()
    task_messages: list[str] = []

    with tempfile.TemporaryDirectory(prefix="c1_ex02_") as tmpdir:
        async for msg in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                model=MODEL,
                max_turns=15,
                cwd=tmpdir,
                permission_mode="bypassPermissions",
            ),
        ):
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, ToolUseBlock):
                        tool_counts[block.name] += 1
                        if block.name == "TodoWrite":
                            print(f"  [TodoWrite] {_truncate(str(block.input), 200)}")

            elif isinstance(msg, TaskStartedMessage):
                task_messages.append(f"TaskStarted: {msg.description}")
                print(f"  [TaskStarted] {msg.description}")

            elif isinstance(msg, TaskProgressMessage):
                task_messages.append(f"TaskProgress: {msg.description}")

            elif isinstance(msg, TaskNotificationMessage):
                task_messages.append(f"TaskNotification: {msg.status} — {msg.summary}")
                print(f"  [TaskNotification] {msg.status} — {_truncate(msg.summary)}")

            elif isinstance(msg, ResultMessage):
                print(f"\n  Result: {msg.subtype}, turns={msg.num_turns}, cost=${msg.total_cost_usd:.4f}" if msg.total_cost_usd else f"\n  Result: {msg.subtype}")

    print(f"\n  Tools used: {dict(tool_counts)}")
    print(f"  TodoWrite used: {'YES' if 'TodoWrite' in tool_counts else 'NO'} ({tool_counts.get('TodoWrite', 0)} times)")
    print(f"  Task lifecycle messages: {len(task_messages)}")

    return dict(tool_counts)


def _truncate(s: str, max_len: int = 120) -> str:
    return s[:max_len] + "..." if len(s) > max_len else s


async def main() -> None:
    # Test 1: Multi-step task WITH explicit todo instruction
    tools_with = await probe_todowrite(
        prompt=(
            "Create a Python calculator project with:\n"
            "1. calc.py — add, subtract, multiply, divide functions\n"
            "2. test_calc.py — pytest tests for each function\n"
            "3. README.md — document the API\n"
            "Track your progress with todos as you go."
        ),
        label="Multi-step task WITH 'track with todos' instruction",
    )

    # Test 2: Multi-step task WITHOUT explicit todo instruction
    tools_without = await probe_todowrite(
        prompt=(
            "Create a Python calculator project with:\n"
            "1. calc.py — add, subtract, multiply, divide functions\n"
            "2. test_calc.py — pytest tests for each function\n"
            "3. README.md — document the API"
        ),
        label="Multi-step task WITHOUT todo instruction",
    )

    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)
    print(f"  TodoWrite with instruction:    {'YES' if 'TodoWrite' in tools_with else 'NO'}")
    print(f"  TodoWrite without instruction: {'YES' if 'TodoWrite' in tools_without else 'NO'}")
    print()
    print("  Per official docs (code.claude.com/docs/en/agent-sdk/overview):")
    print("  SDK-documented built-in tools: Read, Write, Edit, Bash, Monitor,")
    print("    Glob, Grep, WebSearch, WebFetch, AskUserQuestion")
    print("  TodoWrite is NOT listed as an SDK built-in tool.")
    print()
    print("  • TodoWrite leaks through because the SDK runs Claude Code as a subprocess")
    print("  • It is NOT an SDK-advertised feature — it's a CLI implementation detail")
    print("  • You should NOT rely on it in SDK apps; use allowed_tools to control tools")
    print("  • TaskStarted/Progress/Notification are SDK message types for subagent lifecycle")


if __name__ == "__main__":
    asyncio.run(main())
