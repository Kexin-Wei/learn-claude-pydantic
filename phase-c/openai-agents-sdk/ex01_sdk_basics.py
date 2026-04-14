#!/usr/bin/env python3
"""Exercise 1: OpenAI Agents SDK Basics — Agent + Runner + built-in tools.

Question answered: Q4 — What's built-in vs DIY?

Run: uv run python phase-c/openai-agents-sdk/ex01_sdk_basics.py
"""
import asyncio
import os

from dotenv import load_dotenv

from agents import Agent, Runner, function_tool, WebSearchTool, RunConfig

load_dotenv(override=True)

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


@function_tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    data = {"Tokyo": "22°C, sunny", "London": "14°C, cloudy", "Beijing": "18°C, clear"}
    return data.get(city, f"Unknown city: {city}")


async def probe_basic_agent() -> None:
    """Part A: Basic Agent + Runner."""
    print("=" * 60)
    print(f"PART A: Basic Agent + Runner (model={MODEL})")
    print("=" * 60)

    agent = Agent(
        name="greeter",
        instructions="You are a helpful assistant. Be concise.",
        model=MODEL,
    )
    result = await Runner.run(agent, input="What is 2 + 2? Answer in one word.")
    print(f"  Response: {result.final_output}")
    print(f"  Items: {len(result.raw_responses)} raw responses")


async def probe_custom_tools() -> None:
    """Part B: Custom function tools."""
    print(f"\n{'=' * 60}")
    print("PART B: Custom function tools (@function_tool)")
    print("=" * 60)

    agent = Agent(
        name="weather-bot",
        instructions="Use tools to answer questions. Be concise.",
        tools=[get_weather],
        model=MODEL,
    )
    result = await Runner.run(agent, input="What's the weather in Tokyo?")
    print(f"  Response: {result.final_output}")

    # Show what tools were called
    for item in result.new_items:
        item_type = type(item).__name__
        if "ToolCall" in item_type:
            print(f"  [TOOL CALL] {item}")
        elif "ToolOutput" in item_type:
            print(f"  [TOOL OUTPUT] {item}")


async def probe_web_search() -> None:
    """Part C: Built-in WebSearchTool."""
    print(f"\n{'=' * 60}")
    print("PART C: Built-in WebSearchTool")
    print("=" * 60)

    agent = Agent(
        name="searcher",
        instructions="Search the web to answer questions. Be concise.",
        tools=[WebSearchTool()],
        model=MODEL,
    )
    result = await Runner.run(agent, input="What is the latest Python version?")
    print(f"  Response: {result.final_output[:200]}")


async def probe_structured_output() -> None:
    """Part D: Structured output via output_type."""
    print(f"\n{'=' * 60}")
    print("PART D: Structured output (output_type)")
    print("=" * 60)

    from pydantic import BaseModel

    class MovieReview(BaseModel):
        title: str
        year: int
        rating: float
        summary: str

    agent = Agent(
        name="reviewer",
        instructions="Return a movie review as structured data.",
        output_type=MovieReview,
        model=MODEL,
    )
    result = await Runner.run(agent, input="Review the movie Inception (2010).")
    print(f"  Type: {type(result.final_output).__name__}")
    print(f"  Data: {result.final_output}")


async def main() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: Set OPENAI_API_KEY in .env")
        return

    await probe_basic_agent()
    await probe_custom_tools()
    await probe_web_search()
    await probe_structured_output()

    print(f"\n{'=' * 60}")
    print("KEY FINDINGS")
    print("=" * 60)
    print("  OpenAI Agents SDK provides:")
    print("    YES  Agent class (name, instructions, tools, model)")
    print("    YES  Runner.run() — automatic agent loop")
    print("    YES  @function_tool — decorator for custom tools")
    print("    YES  WebSearchTool, FileSearchTool, CodeInterpreterTool")
    print("    YES  Structured output via output_type (Pydantic)")
    print("    YES  Streaming (Runner.run_streamed)")


if __name__ == "__main__":
    asyncio.run(main())
