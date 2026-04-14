#!/usr/bin/env python3
"""Exercise 3: Subagents — Auto-spawn vs manual orchestration.

Question answered: Q2 — Does it auto-spawn subagents or require manual orchestration?

Run: uv run python phase-c/claude-agent-sdk/ex03_subagents.py
"""
import asyncio
import os
import tempfile
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

from claude_agent_sdk import (
    AgentDefinition,
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    SystemMessage,
    TaskNotificationMessage,
    TaskProgressMessage,
    TaskStartedMessage,
    TextBlock,
    ToolUseBlock,
    query,
)

load_dotenv(override=True)

WORKDIR = Path(__file__).parent
MODEL = os.environ.get("CLAUDE_MODEL")


async def probe_auto_spawn() -> None:
    """Part A: Does the agent auto-spawn subagents for complex tasks?"""
    print("=" * 60)
    print("PART A: Auto-spawn subagents?")
    print("=" * 60)

    tool_counts: Counter[str] = Counter()
    task_events: list[str] = []

    async for msg in query(
        prompt=(
            "Analyze this repository: first explore the directory structure, "
            "then read 2-3 key files, then write a 3-sentence summary of what "
            "this project is about. Work efficiently."
        ),
        options=ClaudeAgentOptions(
            model=MODEL,
            max_turns=10,
            cwd=str(WORKDIR.parent.parent),  # repo root
        ),
    ):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, ToolUseBlock):
                    tool_counts[block.name] += 1
                    # Watch for Agent/Task tool that spawns subagents
                    if block.name in ("Agent", "Task"):
                        print(f"  [SUBAGENT SPAWN] {block.name}: {_truncate(str(block.input), 200)}")

        elif isinstance(msg, TaskStartedMessage):
            task_events.append(f"started: {msg.description}")
            print(f"  [TaskStarted] id={msg.task_id}, desc={_truncate(msg.description)}")

        elif isinstance(msg, TaskNotificationMessage):
            task_events.append(f"done: {msg.status}")
            print(f"  [TaskDone] id={msg.task_id}, status={msg.status}")

        elif isinstance(msg, ResultMessage):
            print(f"\n  Result: {msg.subtype}, turns={msg.num_turns}")

    agent_tool_used = any(t in tool_counts for t in ("Agent", "Task"))
    print(f"\n  Tools: {dict(tool_counts)}")
    print(f"  Agent/Task tool used (auto-spawn): {'YES' if agent_tool_used else 'NO'}")
    print(f"  Task lifecycle events: {len(task_events)}")


async def probe_manual_agents() -> None:
    """Part B: Define custom agents via the agents parameter."""
    print("\n" + "=" * 60)
    print("PART B: Manual agent definitions via `agents` param")
    print("=" * 60)

    tool_counts: Counter[str] = Counter()
    task_events: list[str] = []

    with tempfile.TemporaryDirectory(prefix="c1_ex03_") as tmpdir:
        async for msg in query(
            prompt=(
                "Use the 'researcher' agent to explore this directory and find "
                "all Python files, then use the 'writer' agent to create a "
                "SUMMARY.md listing what you found."
            ),
            options=ClaudeAgentOptions(
                model=MODEL,
                max_turns=15,
                cwd=str(WORKDIR.parent.parent),  # repo root
                permission_mode="bypassPermissions",
                agents={
                    "researcher": AgentDefinition(
                        description="Explores codebases and summarizes findings",
                        prompt="You are a code researcher. Explore the codebase and report your findings concisely.",
                        tools=["Bash", "Read", "Glob", "Grep"],
                        model="haiku",
                    ),
                    "writer": AgentDefinition(
                        description="Writes documentation based on findings",
                        prompt="You are a technical writer. Write clear, concise documentation.",
                        tools=["Write", "Edit"],
                        model="haiku",
                    ),
                },
            ),
        ):
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, ToolUseBlock):
                        tool_counts[block.name] += 1
                        if block.name in ("Agent", "Task"):
                            print(f"  [AGENT CALL] {block.name}: {_truncate(str(block.input), 200)}")
                    elif isinstance(block, TextBlock):
                        if len(block.text.strip()) < 200:
                            print(f"  [TEXT] {block.text.strip()}")

            elif isinstance(msg, TaskStartedMessage):
                task_events.append(f"started: {msg.description}")
                print(f"  [TaskStarted] id={msg.task_id}, desc={_truncate(msg.description)}")

            elif isinstance(msg, TaskNotificationMessage):
                task_events.append(f"done: {msg.status}")
                print(f"  [TaskDone] id={msg.task_id}, status={msg.status}")

            elif isinstance(msg, ResultMessage):
                print(f"\n  Result: {msg.subtype}, turns={msg.num_turns}")

    agent_tool_used = any(t in tool_counts for t in ("Agent", "Task"))
    print(f"\n  Tools: {dict(tool_counts)}")
    print(f"  Agent/Task tool invoked: {'YES' if agent_tool_used else 'NO'}")
    print(f"  Task lifecycle events: {len(task_events)}")


def _truncate(s: str, max_len: int = 120) -> str:
    return s[:max_len] + "..." if len(s) > max_len else s


async def main() -> None:
    await probe_auto_spawn()
    await probe_manual_agents()

    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)
    print("  Per docs (code.claude.com/docs/en/agent-sdk/subagents):")
    print("  • Subagents are a FIRST-CLASS SDK feature (well-documented)")
    print("  • 3 ways to create: programmatic (agents param), filesystem (.claude/agents/),")
    print("    or built-in general-purpose (auto-spawns when Agent in allowedTools)")
    print("  • AgentDefinition: description, prompt, tools, model, skills, memory, mcpServers")
    print("  • Claude decides when to delegate based on agent descriptions")
    print("  • Subagents run in fresh context — only final message returns to parent")
    print("  • Subagents CANNOT spawn their own subagents (no nesting)")
    print("  • TaskStarted/TaskNotification messages track subagent lifecycle")


if __name__ == "__main__":
    asyncio.run(main())
