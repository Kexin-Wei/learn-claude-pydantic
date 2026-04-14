#!/usr/bin/env python3
"""Exercise 3: Hooks & Tracing — lifecycle events and observability.

Question answered: Q3 — Does it have tracing, task tracking, planning?

Run: uv run python phase-c/openai-agents-sdk/ex03_hooks_and_tracing.py
"""
import asyncio
import os

from dotenv import load_dotenv

from agents import Agent, Runner, RunHooks, AgentHooks, RunContextWrapper, function_tool

load_dotenv(override=True)

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


@function_tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


class TrackingRunHooks(RunHooks):
    """Run-level hooks that track which events fired."""

    def __init__(self):
        self.events: list[str] = []

    async def on_agent_start(self, context, agent):
        self.events.append("agent_start")
        print(f"  [HOOK] agent_start: {agent.name}")

    async def on_agent_end(self, context, agent, output):
        self.events.append("agent_end")
        print(f"  [HOOK] agent_end: {agent.name}")

    async def on_tool_start(self, context, agent, tool):
        self.events.append("tool_start")
        print(f"  [HOOK] tool_start: {tool.name}")

    async def on_tool_end(self, context, agent, tool, result):
        self.events.append("tool_end")
        print(f"  [HOOK] tool_end: {tool.name} → {str(result)[:80]}")

    async def on_llm_start(self, context, agent, system_prompt, input_items):
        self.events.append("llm_start")
        print(f"  [HOOK] llm_start: {agent.name}")

    async def on_llm_end(self, context, agent, response):
        self.events.append("llm_end")
        print(f"  [HOOK] llm_end: {agent.name}")


async def probe_run_hooks() -> dict:
    """Part A: Run-level hooks."""
    print("=" * 60)
    print("PART A: Run-level hooks (RunHooks)")
    print("=" * 60)

    agent = Agent(
        name="calculator",
        instructions="Use the add tool. Be concise.",
        tools=[add],
        model=MODEL,
    )

    hooks = TrackingRunHooks()
    result = await Runner.run(
        agent,
        input="What is 3 + 7?",
        hooks=hooks,
    )
    print(f"\n  Result: {result.final_output}")
    return {"events": hooks.events}


async def probe_agent_hooks() -> dict:
    """Part B: Agent-level hooks."""
    print(f"\n{'=' * 60}")
    print("PART B: Agent-level hooks (AgentHooks)")
    print("=" * 60)

    events: list[str] = []

    class MyAgentHooks(AgentHooks):
        async def on_start(self, context, agent):
            events.append("start")
            print(f"  [AGENT HOOK] start: {agent.name}")

        async def on_end(self, context, agent, output):
            events.append("end")
            print(f"  [AGENT HOOK] end: {agent.name} → {str(output)[:80]}")

    agent = Agent(
        name="greeter",
        instructions="Say hello. Be concise.",
        hooks=MyAgentHooks(),
        model=MODEL,
    )

    result = await Runner.run(agent, input="Hi!")
    print(f"\n  Result: {result.final_output}")
    return {"events": events}


async def probe_tracing() -> dict:
    """Part C: Built-in tracing."""
    print(f"\n{'=' * 60}")
    print("PART C: Tracing (built-in)")
    print("=" * 60)

    from agents import set_tracing_disabled

    # Check if tracing APIs exist
    has_set_disabled = callable(set_tracing_disabled)
    has_set_processors = hasattr(__import__("agents"), "set_trace_processors")
    print(f"  set_tracing_disabled available: {has_set_disabled}")
    print(f"  set_trace_processors available: {has_set_processors}")
    return {"has_set_disabled": has_set_disabled, "has_set_processors": has_set_processors}


async def main() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: Set OPENAI_API_KEY in .env")
        return

    run = await probe_run_hooks()
    agent = await probe_agent_hooks()
    tracing = await probe_tracing()

    def yn(val: bool) -> str:
        return "YES" if val else "NO"

    run_events = sorted(set(run["events"]))
    agent_events = sorted(set(agent["events"]))

    print(f"\n{'=' * 60}")
    print("KEY FINDINGS")
    print("=" * 60)
    print(f"  RunHooks events fired:   {', '.join(run_events)}")
    print(f"  AgentHooks events fired: {', '.join(agent_events)}")
    print(f"  {yn(tracing['has_set_disabled'])}  Built-in tracing (set_tracing_disabled)")
    print(f"  {yn(tracing['has_set_processors'])}  Custom trace processors (set_trace_processors)")


if __name__ == "__main__":
    asyncio.run(main())
