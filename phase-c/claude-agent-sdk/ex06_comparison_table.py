#!/usr/bin/env python3
"""Exercise 6: Comparison Table — Empirical summary of all findings.

Questions answered: All four, synthesized.

Run: uv run python phase-c/claude-agent-sdk/ex06_comparison_table.py
"""
import asyncio
import os
import tempfile
from collections import Counter

from dotenv import load_dotenv

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TaskStartedMessage,
    TextBlock,
    ToolUseBlock,
    query,
)

load_dotenv(override=True)

MODEL = os.environ.get("CLAUDE_MODEL")


async def probe_tool_inventory() -> list[str]:
    """Probe 1: Ask Claude to list its available tools."""
    print("Probe 1: Tool inventory...", flush=True)
    tools: list[str] = []
    async for msg in query(
        prompt=(
            "List every tool you have access to. Output ONLY tool names, "
            "one per line, no descriptions, no numbering. "
            "Do NOT use any tools to answer."
        ),
        options=ClaudeAgentOptions(model=MODEL, max_turns=1),
    ):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    for line in block.text.strip().splitlines():
                        name = line.strip().strip("-•*").strip()
                        if name and not name.startswith("#"):
                            tools.append(name)
    print(f"  Found {len(tools)} tools")
    return tools


async def probe_todowrite() -> bool:
    """Probe 2: Does a multi-step task trigger TodoWrite?"""
    print("Probe 2: TodoWrite presence...", flush=True)
    used_todo = False
    with tempfile.TemporaryDirectory(prefix="c1_ex06_") as tmpdir:
        async for msg in query(
            prompt=(
                "Create three files: hello.py, world.py, and main.py that imports both. "
                "Use todos to track progress."
            ),
            options=ClaudeAgentOptions(
                model=MODEL,
                max_turns=10,
                cwd=tmpdir,
                permission_mode="bypassPermissions",
            ),
        ):
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, ToolUseBlock) and block.name == "TodoWrite":
                        used_todo = True
    print(f"  TodoWrite used: {used_todo}")
    return used_todo


async def probe_subagent_spawn() -> bool:
    """Probe 3: Does a complex task trigger subagent spawning?"""
    print("Probe 3: Subagent auto-spawn...", flush=True)
    spawned = False
    tool_counts: Counter[str] = Counter()
    async for msg in query(
        prompt=(
            "Explore this repository's structure and summarize what each top-level "
            "directory contains. Be thorough but concise."
        ),
        options=ClaudeAgentOptions(model=MODEL, max_turns=10),
    ):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, ToolUseBlock):
                    tool_counts[block.name] += 1
                    if block.name in ("Agent", "Task"):
                        spawned = True
        elif isinstance(msg, TaskStartedMessage):
            spawned = True
    print(f"  Subagent spawned: {spawned}")
    print(f"  Tools: {dict(tool_counts)}")
    return spawned


async def probe_plan_mode() -> str:
    """Probe 4: What does permission_mode='plan' do?"""
    print("Probe 4: Plan mode behavior...", flush=True)
    tool_counts: Counter[str] = Counter()
    with tempfile.TemporaryDirectory(prefix="c1_ex06_plan_") as tmpdir:
        async for msg in query(
            prompt="Create a file called test.txt with 'hello' in it.",
            options=ClaudeAgentOptions(
                model=MODEL,
                max_turns=5,
                cwd=tmpdir,
                permission_mode="plan",
            ),
        ):
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, ToolUseBlock):
                        tool_counts[block.name] += 1

            elif isinstance(msg, ResultMessage):
                pass

    any_tools = bool(tool_counts)
    behavior = "no tool execution (as documented)" if not any_tools else "tools executed (unexpected)"
    print(f"  Behavior: {behavior}")
    return behavior


async def main() -> None:
    print("=" * 70)
    print("TRACK C1 — CLAUDE AGENT SDK EMPIRICAL COMPARISON")
    print("=" * 70)
    print()

    tools = await probe_tool_inventory()
    has_todo = await probe_todowrite()
    has_subagent = await probe_subagent_spawn()
    plan_behavior = await probe_plan_mode()

    print("\n" + "=" * 70)
    print("FINDINGS TABLE")
    print("=" * 70)

    # SDK-documented built-in tools (per code.claude.com/docs/en/agent-sdk/overview):
    # Read, Write, Edit, Bash, Monitor, Glob, Grep, WebSearch, WebFetch, AskUserQuestion
    sdk_documented_tools = {
        "Read", "Write", "Edit", "Bash", "Monitor", "Glob", "Grep",
        "WebSearch", "WebFetch", "AskUserQuestion",
    }

    rows = [
        ("Agent loop (tool use cycle)", "Yes", "SDK core"),
        ("Read/Write/Edit/Bash/Glob/Grep", "Yes (documented)", "SDK built-in tools"),
        ("Monitor/WebSearch/WebFetch", "Yes (documented)", "SDK built-in tools"),
        ("AskUserQuestion", "Yes (documented)", "SDK built-in tool"),
        ("Subagents (Agent tool)", "Yes (documented)", "agents param + Agent tool"),
        ("Built-in general-purpose agent", "Yes (auto)", "Auto-spawns when Agent in allowedTools"),
        ("AgentDefinition", "Yes (SDK-native)", "ClaudeAgentOptions.agents"),
        ("TodoWrite (task planning)", f"{'Leaks' if has_todo else 'No'}", "NOT documented — CLI artifact"),
        ("Plan-then-execute workflow", "NO", f"plan mode = {plan_behavior}"),
        ("Custom tools (@tool)", "Yes (SDK-native)", "@tool + create_sdk_mcp_server"),
        ("Hooks (lifecycle events)", "Yes (SDK-native)", "PreToolUse, PostToolUse, Stop, etc."),
        ("Permission modes", "Yes (SDK-native)", "default/dontAsk/acceptEdits/bypass/plan"),
        ("can_use_tool callback", "Yes (SDK-native)", "Runtime permission decisions"),
        ("Structured output", "Yes (SDK-native)", "output_format param"),
        ("Extended thinking", "Yes (config)", "thinking param (Enabled/Adaptive)"),
        ("Session management", "Yes (SDK-native)", "resume, fork, list/get/rename/tag"),
        ("File checkpointing", "Yes (SDK-native)", "enable_file_checkpointing"),
        ("Skills (on-demand)", "Yes (via settingSources)", ".claude/skills/ loaded on demand"),
        ("CLAUDE.md / rules", "Yes (via settingSources)", "Project instructions"),
        ("Auto memory", "NO", "CLI-only feature, never loaded by SDK"),
        ("Agent teams", "NO", "CLI-only feature"),
    ]

    print(f"{'Capability':<38} {'Provided?':<22} {'Source'}")
    print("-" * 90)
    for cap, provided, source in rows:
        print(f"{cap:<38} {provided:<22} {source}")

    print("\n" + "=" * 70)
    print("ANSWERS TO THE 4 QUESTIONS")
    print("=" * 70)

    print("""
Q1: Does it provide TodoWrite / task management?
    NO — TodoWrite is NOT in the SDK's documented built-in tools.
    It leaks through because the SDK runs Claude Code as a subprocess,
    but it's not an SDK-advertised feature. Don't rely on it.

Q2: Does it auto-spawn subagents or require manual orchestration?
    BOTH — The SDK documents subagents as a first-class feature:
    - AgentDefinition for custom agents via the `agents` parameter
    - A built-in `general-purpose` subagent auto-spawns when Agent is in allowedTools
    - Claude decides when to delegate based on agent descriptions
    Orchestration is Claude's judgment, not automatic routing.

Q3: Does it have planner mode / plan-then-execute?
    NO — permission_mode='plan' prevents ALL tool execution.
    Per docs: "No tool execution; Claude plans without making changes."
    There is no plan-then-execute workflow. Planning is emergent behavior.

Q4: What's built-in vs what Claude Code adds on top?
    SDK-documented built-in tools (10): Read, Write, Edit, Bash, Monitor,
      Glob, Grep, WebSearch, WebFetch, AskUserQuestion
    SDK-native features: @tool, hooks, can_use_tool, output_format,
      session management, file checkpointing, streaming, AgentDefinition,
      thinking config, sandbox, permission modes, plugins, skills (via settingSources)
    CLI-only (NOT in SDK): TodoWrite, auto memory, agent teams

BOTTOM LINE: The SDK runs Claude Code as a subprocess but has a SMALLER
documented surface than the CLI. It provides 10 built-in tools, subagents,
hooks, permissions, MCP, and session management. TodoWrite, auto memory,
and agent teams are CLI-only features that are not part of the SDK contract.
""")


if __name__ == "__main__":
    asyncio.run(main())
