#!/usr/bin/env python3
"""Exercise 4: Plan Mode — Is there a plan-then-execute workflow?

Question answered: Q3 — Does it have planner mode / plan-then-execute?

Run: uv run python phase-c/claude-agent-sdk/ex04_plan_mode.py
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
    TextBlock,
    ThinkingBlock,
    ThinkingConfigAdaptive,
    ThinkingConfigDisabled,
    ThinkingConfigEnabled,
    ToolUseBlock,
    query,
)

load_dotenv(override=True)

MODEL = os.environ.get("CLAUDE_MODEL")

TASK_PROMPT = (
    "Create a Python module called 'stats.py' with functions for mean, median, "
    "and standard deviation. Then create 'test_stats.py' with pytest tests."
)


async def probe_plan_permission_mode() -> bool:
    """Part A: What does permission_mode='plan' actually do? Returns True if tools were blocked."""
    print("=" * 60)
    print("PART A: permission_mode='plan'")
    print("=" * 60)

    tool_counts: Counter[str] = Counter()
    texts: list[str] = []

    with tempfile.TemporaryDirectory(prefix="c1_ex04a_") as tmpdir:
        print(f"  Prompt: {TASK_PROMPT!r}")
        async for msg in query(
            prompt=TASK_PROMPT,
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
                        print(f"  [TOOL] {block.name}")
                    elif isinstance(block, TextBlock):
                        texts.append(block.text)
                        if len(block.text.strip()) < 300:
                            print(f"  [TEXT] {_truncate(block.text.strip())}")

            elif isinstance(msg, ResultMessage):
                print(f"\n  Result: {msg.subtype}, turns={msg.num_turns}")
                if msg.stop_reason:
                    print(f"  Stop reason: {msg.stop_reason}")

    print(f"\n  Tools used: {dict(tool_counts)}")
    any_tools = bool(tool_counts)
    print(f"  Any tools executed: {'YES' if any_tools else 'NO'}")
    return not any_tools  # True = tools were blocked (expected)


async def probe_thinking() -> int:
    """Part B: Extended thinking as a planning mechanism."""
    print("\n" + "=" * 60)
    print("PART B: Extended thinking (ThinkingConfigEnabled)")
    print("=" * 60)

    thinking_blocks: list[str] = []
    tool_counts: Counter[str] = Counter()

    with tempfile.TemporaryDirectory(prefix="c1_ex04b_") as tmpdir:
        print(f"  Prompt: {TASK_PROMPT!r}")
        try:
            async for msg in query(
                prompt=TASK_PROMPT,
                options=ClaudeAgentOptions(
                    model=MODEL,
                    max_turns=10,
                    cwd=tmpdir,
                    permission_mode="bypassPermissions",
                    thinking={"type": "enabled", "budget_tokens": 5000},
                ),
            ):
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, ThinkingBlock):
                            thinking_blocks.append(block.thinking)
                            print(f"  [THINKING] {_truncate(block.thinking, 200)}")
                        elif isinstance(block, ToolUseBlock):
                            tool_counts[block.name] += 1

                elif isinstance(msg, ResultMessage):
                    print(f"\n  Result: {msg.subtype}, turns={msg.num_turns}")
        except Exception as e:
            print(f"\n  ERROR: {type(e).__name__}: {e}")

    print(f"\n  Thinking blocks: {len(thinking_blocks)}")
    print(f"  Tools used: {dict(tool_counts)}")
    return len(thinking_blocks)


async def probe_effort_levels() -> None:
    """Part C: Compare effort levels."""
    print("\n" + "=" * 60)
    print("PART C: Effort levels (low vs high)")
    print("=" * 60)

    for effort in ("low", "high"):
        tool_counts: Counter[str] = Counter()
        prompt = "What is 2 + 2? Answer in one word."
        with tempfile.TemporaryDirectory(prefix=f"c1_ex04c_{effort}_") as tmpdir:
            print(f"  Prompt: {prompt!r}")
            async for msg in query(
                prompt=prompt,
                options=ClaudeAgentOptions(
                    model=MODEL,
                    max_turns=1,
                    cwd=tmpdir,
                    effort=effort,  # type: ignore[arg-type]
                ),
            ):
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            print(f"  [{effort}] {block.text.strip()}")
                        elif isinstance(block, ThinkingBlock):
                            print(f"  [{effort}] (thinking: {_truncate(block.thinking, 80)})")

                elif isinstance(msg, ResultMessage):
                    cost = f"${msg.total_cost_usd:.4f}" if msg.total_cost_usd else "N/A"
                    print(f"  [{effort}] turns={msg.num_turns}, cost={cost}, duration={msg.duration_ms}ms")


def _truncate(s: str, max_len: int = 120) -> str:
    return s[:max_len] + "..." if len(s) > max_len else s


async def main() -> None:
    tools_blocked = await probe_plan_permission_mode()
    num_thinking = await probe_thinking()
    await probe_effort_levels()

    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)
    print(f"  Part A — plan mode: {'blocked tool execution (as expected)' if tools_blocked else 'tools WERE executed (unexpected)'}")
    print(f"  Part B — extended thinking: {num_thinking} thinking blocks observed")
    print("  Part C — effort levels: see per-level results above")


if __name__ == "__main__":
    asyncio.run(main())
