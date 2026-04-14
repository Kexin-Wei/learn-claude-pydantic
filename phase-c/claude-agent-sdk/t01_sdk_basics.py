#!/usr/bin/env python3
"""Exercise 1: SDK Basics — What does query() give you out of the box?

Question answered: Q4 — What's built-in vs what Claude Code adds on top?

Run: uv run python phase-c/claude-agent-sdk/ex01_sdk_basics.py
"""
import asyncio
import os
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    StreamEvent,
    SystemMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
    query,
)

load_dotenv(override=True)

WORKDIR = Path(__file__).parent
MODEL = os.environ.get("CLAUDE_MODEL")


def classify_message(msg: object) -> str:
    """Return a human-readable label for a message type."""
    match msg:
        case AssistantMessage():
            return "AssistantMessage"
        case UserMessage():
            return "UserMessage"
        case SystemMessage():
            return "SystemMessage"
        case ResultMessage():
            return "ResultMessage"
        case StreamEvent():
            return "StreamEvent"
        case _:
            return type(msg).__name__


async def probe_default_tools() -> list[str]:
    """Send a simple prompt and observe which tools the SDK uses."""
    print("=" * 60)
    print("PROBE 1: Default tool availability")
    print("Prompt: 'List the Python files in this directory'")
    print("=" * 60)

    message_types: Counter[str] = Counter()
    tools_used: list[str] = []

    prompt = "List the Python files in this directory. Be brief."
    print(f"  Prompt: {prompt!r}")
    async for msg in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            model=MODEL,
            max_turns=3,
            cwd=str(WORKDIR),
        ),
    ):
        label = classify_message(msg)
        message_types[label] += 1

        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, ToolUseBlock):
                    tools_used.append(block.name)
                    print(f"  [TOOL USE] {block.name}({_truncate(str(block.input))})")
                elif isinstance(block, TextBlock):
                    print(f"  [TEXT] {_truncate(block.text)}")
                elif isinstance(block, ToolResultBlock):
                    print(f"  [TOOL RESULT] {_truncate(str(block.content))}")

        elif isinstance(msg, UserMessage):
            # Tool results come back as UserMessages
            if isinstance(msg.content, list):
                for block in msg.content:
                    if isinstance(block, ToolResultBlock):
                        print(
                            f"  [TOOL RESULT] {_truncate(str(block.content))}"
                        )

        elif isinstance(msg, ResultMessage):
            print(f"\n--- Result ---")
            print(f"  subtype:    {msg.subtype}")
            print(f"  turns:      {msg.num_turns}")
            print(f"  cost:       ${msg.total_cost_usd:.4f}" if msg.total_cost_usd else "  cost: N/A")
            print(f"  session_id: {msg.session_id}")
            print(f"  duration:   {msg.duration_ms}ms")

    print(f"\n--- Summary ---")
    print(f"  Message types seen: {dict(message_types)}")
    print(f"  Tools used: {tools_used}")
    return tools_used


async def probe_tool_inventory() -> list[str]:
    """Ask Claude to list all tools it has access to."""
    print("\n" + "=" * 60)
    print("PROBE 2: Full tool inventory")
    print("Prompt: 'List every tool you have access to, one per line'")
    print("=" * 60)

    prompt = (
        "List every tool you currently have access to. "
        "Output ONLY the tool names, one per line, no descriptions. "
        "Do NOT use any tools to answer this — just list them from your system prompt."
    )
    print(f"  Prompt: {prompt!r}")
    tool_names: list[str] = []
    async for msg in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            model=MODEL,
            max_turns=1,
            cwd=str(WORKDIR),
        ),
    ):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(block.text)
                    for line in block.text.strip().splitlines():
                        name = line.strip().strip("-•*").strip()
                        if name and not name.startswith("#"):
                            tool_names.append(name)

        elif isinstance(msg, ResultMessage):
            print(f"\n  (cost: ${msg.total_cost_usd:.4f})" if msg.total_cost_usd else "")
    return tool_names


def _truncate(s: str, max_len: int = 120) -> str:
    return s[:max_len] + "..." if len(s) > max_len else s


async def main() -> None:
    tools_used = await probe_default_tools()
    tool_list = await probe_tool_inventory()

    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)
    if tools_used:
        print(f"  Probe 1 used these tools: {', '.join(tools_used)}")
    else:
        print("  Probe 1: no tool calls detected")
    if tool_list:
        print(f"  Probe 2 reported {len(tool_list)} tools: {', '.join(tool_list)}")
    else:
        print("  Probe 2: model returned no tool list")


if __name__ == "__main__":
    asyncio.run(main())
