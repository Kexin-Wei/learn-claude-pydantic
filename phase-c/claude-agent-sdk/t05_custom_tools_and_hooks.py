#!/usr/bin/env python3
"""Exercise 5: SDK-Native Primitives — Custom tools, hooks, permissions, structured output.

Question answered: Q4 — What's built-in vs what Claude Code adds on top?
This exercise tests the SDK's OWN value-add (not inherited from Claude Code).

Run: uv run python phase-c/claude-agent-sdk/ex05_custom_tools_and_hooks.py
"""
import asyncio
import json
import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    create_sdk_mcp_server,
    query,
    tool,
)

load_dotenv(override=True)

MODEL = os.environ.get("CLAUDE_MODEL")


# ---------------------------------------------------------------------------
# Part A: Custom in-process tools via @tool + create_sdk_mcp_server
# ---------------------------------------------------------------------------

@tool("lookup_weather", "Get current weather for a city", {"city": str})
async def lookup_weather(args: dict) -> dict:
    """Fake weather lookup — demonstrates custom tool creation."""
    city = args["city"]
    # Simulated response
    data = {
        "Tokyo": "22°C, sunny",
        "London": "14°C, cloudy",
        "New York": "18°C, partly cloudy",
    }
    weather = data.get(city, f"Unknown city: {city}")
    return {"content": [{"type": "text", "text": f"Weather in {city}: {weather}"}]}


@tool("unit_convert", "Convert between units", {"value": float, "from_unit": str, "to_unit": str})
async def unit_convert(args: dict) -> dict:
    """Simple unit converter — another custom tool example."""
    v, f, t = args["value"], args["from_unit"], args["to_unit"]
    conversions = {
        ("km", "miles"): lambda x: x * 0.621371,
        ("miles", "km"): lambda x: x * 1.60934,
        ("celsius", "fahrenheit"): lambda x: x * 9 / 5 + 32,
        ("fahrenheit", "celsius"): lambda x: (x - 32) * 5 / 9,
    }
    key = (f.lower(), t.lower())
    if key in conversions:
        result = conversions[key](v)
        return {"content": [{"type": "text", "text": f"{v} {f} = {result:.2f} {t}"}]}
    return {"content": [{"type": "text", "text": f"Cannot convert {f} to {t}"}], "is_error": True}


async def probe_custom_tools() -> list[str]:
    """Part A: Custom MCP tools that run in-process."""
    print("=" * 60)
    print("PART A: Custom in-process tools (@tool + create_sdk_mcp_server)")
    print("=" * 60)

    server = create_sdk_mcp_server("my_tools", tools=[lookup_weather, unit_convert])

    tools_called: list[str] = []
    prompt = (
        "What's the weather in Tokyo? Also, convert 100 km to miles. "
        "Use the lookup_weather and unit_convert tools."
    )
    print(f"  Prompt: {prompt!r}")
    async for msg in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            model=MODEL,
            max_turns=5,
            mcp_servers={"my_tools": server},
            allowed_tools=["mcp__my_tools__lookup_weather", "mcp__my_tools__unit_convert"],
        ),
    ):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, ToolUseBlock):
                    tools_called.append(block.name)
                    print(f"  [TOOL] {block.name}({block.input})")
                elif isinstance(block, TextBlock):
                    print(f"  [TEXT] {_truncate(block.text.strip())}")

        elif isinstance(msg, ResultMessage):
            print(f"\n  Result: {msg.subtype}, turns={msg.num_turns}")

    print(f"\n  Custom tools called: {tools_called}")
    return tools_called


# ---------------------------------------------------------------------------
# Part B: Structured output via output_format
# ---------------------------------------------------------------------------

async def probe_structured_output() -> bool:
    """Part B: Get structured JSON output. Returns True if output was produced."""
    print("\n" + "=" * 60)
    print("PART B: Structured output (output_format)")
    print("=" * 60)

    schema = {
        "type": "json_schema",
        "json_schema": {
            "name": "movie_review",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "year": {"type": "integer"},
                    "rating": {"type": "number"},
                    "summary": {"type": "string"},
                },
                "required": ["title", "year", "rating", "summary"],
                "additionalProperties": False,
            },
        },
    }

    prompt = "Give me a review of the movie 'Inception' (2010). Return structured JSON."
    print(f"  Prompt: {prompt!r}")
    got_output = False
    async for msg in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            model=MODEL,
            max_turns=1,
            output_format=schema,
        ),
    ):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"  [RAW] {_truncate(block.text, 200)}")

        elif isinstance(msg, ResultMessage):
            print(f"\n  Result: {msg.subtype}")
            if msg.result:
                print(f"  result field: {_truncate(msg.result, 200)}")
                got_output = True
            if msg.structured_output:
                print(f"  structured_output: {json.dumps(msg.structured_output, indent=2)[:300]}")
                got_output = True
            else:
                print("  structured_output: None")
    return got_output


# ---------------------------------------------------------------------------
# Part C: Permission control via can_use_tool callback
# ---------------------------------------------------------------------------

async def probe_permission_control() -> list[str]:
    """Part C: can_use_tool callback for programmatic permission control."""
    print("\n" + "=" * 60)
    print("PART C: Permission control (can_use_tool callback)")
    print("=" * 60)
    print("  Note: can_use_tool requires streaming mode (ClaudeSDKClient), not query().")
    print("  Demonstrating allowed_tools / disallowed_tools instead.\n")

    tools_attempted: list[str] = []
    with tempfile.TemporaryDirectory(prefix="c1_ex05c_") as tmpdir:
        prompt = "Create a file called hello.txt with 'Hello World' in it."
        print(f"  Prompt: {prompt!r}")
        async for msg in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                model=MODEL,
                max_turns=5,
                cwd=tmpdir,
                disallowed_tools=["Write", "Edit"],
            ),
        ):
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, ToolUseBlock):
                        tools_attempted.append(block.name)
                        print(f"  [TOOL] {block.name}")
                    elif isinstance(block, TextBlock):
                        if len(block.text.strip()) < 200:
                            print(f"  [TEXT] {_truncate(block.text.strip())}")

            elif isinstance(msg, ResultMessage):
                print(f"\n  Result: {msg.subtype}, turns={msg.num_turns}")

    print(f"\n  Tools attempted: {tools_attempted}")
    return tools_attempted


def _truncate(s: str, max_len: int = 120) -> str:
    return s[:max_len] + "..." if len(s) > max_len else s


async def main() -> None:
    custom_tools = await probe_custom_tools()
    structured_ok = await probe_structured_output()
    blocked_tools = await probe_permission_control()

    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)
    if custom_tools:
        print(f"  Part A — custom tools called: {', '.join(custom_tools)}")
    else:
        print("  Part A — no custom tools were called")
    print(f"  Part B — structured output: {'produced output' if structured_ok else 'no output'}")
    print(f"  Part C — disallowed_tools: attempted tools = {blocked_tools}")


if __name__ == "__main__":
    asyncio.run(main())
