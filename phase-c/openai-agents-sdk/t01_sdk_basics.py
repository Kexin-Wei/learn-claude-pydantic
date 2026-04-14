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


async def probe_basic_agent() -> dict:
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
    return {"has_response": bool(result.final_output), "raw_responses": len(result.raw_responses)}


async def probe_custom_tools() -> dict:
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

    tool_calls = []
    for item in result.new_items:
        item_type = type(item).__name__
        if "ToolCall" in item_type:
            tool_calls.append(item_type)
            print(f"  [TOOL CALL] {item}")
        elif "ToolOutput" in item_type:
            print(f"  [TOOL OUTPUT] {item}")
    return {"tool_called": bool(tool_calls), "tool_call_count": len(tool_calls)}


async def probe_web_search() -> dict:
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
    return {"has_response": bool(result.final_output)}


async def probe_structured_output() -> dict:
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
    output_type = type(result.final_output).__name__
    print(f"  Type: {output_type}")
    print(f"  Data: {result.final_output}")
    return {"is_pydantic": output_type == "MovieReview"}


async def main() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: Set OPENAI_API_KEY in .env")
        return

    basic = await probe_basic_agent()
    tools = await probe_custom_tools()
    web = await probe_web_search()
    structured = await probe_structured_output()

    def yn(val: bool) -> str:
        return "YES" if val else "NO"

    print(f"\n{'=' * 60}")
    print("KEY FINDINGS")
    print("=" * 60)
    print("  OpenAI Agents SDK provides:")
    print(f"    {yn(basic['has_response'])}  Agent + Runner.run() — automatic agent loop")
    print(f"    {yn(tools['tool_called'])}  @function_tool — custom tools ({tools['tool_call_count']} call(s) observed)")
    print(f"    {yn(web['has_response'])}  WebSearchTool — built-in web search")
    print(f"    {yn(structured['is_pydantic'])}  Structured output via output_type (Pydantic)")


if __name__ == "__main__":
    asyncio.run(main())
