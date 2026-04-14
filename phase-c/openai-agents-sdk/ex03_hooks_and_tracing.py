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


# ── Custom hooks ──────────────────────────────────────────────

class MyRunHooks(RunHooks):
    """Run-level hooks — fires for every agent in the run."""

    async def on_agent_start(self, context, agent, input_list):
        print(f"  [HOOK] agent_start: {agent.name}")

    async def on_agent_end(self, context, agent, output):
        print(f"  [HOOK] agent_end: {agent.name}")

    async def on_tool_start(self, context, agent, tool):
        print(f"  [HOOK] tool_start: {tool.name}")

    async def on_tool_end(self, context, agent, tool, result):
        print(f"  [HOOK] tool_end: {tool.name} → {str(result)[:80]}")

    async def on_llm_start(self, context, agent, llm_input):
        print(f"  [HOOK] llm_start: {agent.name}")

    async def on_llm_end(self, context, agent, result):
        print(f"  [HOOK] llm_end: {agent.name}")


@function_tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


async def probe_run_hooks() -> None:
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

    result = await Runner.run(
        agent,
        input="What is 3 + 7?",
        hooks=MyRunHooks(),
    )
    print(f"\n  Result: {result.final_output}")


async def probe_agent_hooks() -> None:
    """Part B: Agent-level hooks."""
    print(f"\n{'=' * 60}")
    print("PART B: Agent-level hooks (AgentHooks)")
    print("=" * 60)

    class MyAgentHooks(AgentHooks):
        async def on_start(self, context, agent, input_list):
            print(f"  [AGENT HOOK] start: {agent.name}")

        async def on_end(self, context, agent, output):
            print(f"  [AGENT HOOK] end: {agent.name} → {str(output)[:80]}")

    agent = Agent(
        name="greeter",
        instructions="Say hello. Be concise.",
        hooks=MyAgentHooks(),
        model=MODEL,
    )

    result = await Runner.run(agent, input="Hi!")
    print(f"\n  Result: {result.final_output}")


async def probe_tracing() -> None:
    """Part C: Built-in tracing."""
    print(f"\n{'=' * 60}")
    print("PART C: Tracing (built-in)")
    print("=" * 60)

    # OpenAI Agents SDK has built-in tracing that sends to OpenAI dashboard
    # You can also add custom trace processors
    from agents import set_tracing_disabled

    # Tracing is on by default — sends to OpenAI
    print("  Tracing is enabled by default (sends to OpenAI dashboard)")
    print("  Disable with: set_tracing_disabled(True)")
    print("  Custom processors: set_trace_processors([your_processor])")
    print("  Compare Claude: no built-in tracing dashboard")


async def main() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: Set OPENAI_API_KEY in .env")
        return

    await probe_run_hooks()
    await probe_agent_hooks()
    await probe_tracing()

    print(f"\n{'=' * 60}")
    print("KEY FINDINGS")
    print("=" * 60)
    print("  OpenAI hooks:")
    print("    RunHooks   — on_agent_start/end, on_tool_start/end, on_llm_start/end, on_handoff")
    print("    AgentHooks — on_start/end, on_tool_start/end, on_llm_start/end, on_handoff")
    print("  Compare Claude hooks:")
    print("    PreToolUse, PostToolUse, Stop, SubagentStart, SubagentStop, etc.")
    print()
    print("  OpenAI tracing:")
    print("    Built-in → OpenAI dashboard (or custom processors)")
    print("  Claude tracing:")
    print("    No built-in dashboard. Hooks + session management for observability.")
    print()
    print("  Task tracking / planning:")
    print("    OpenAI: NO — no TodoWrite equivalent, no plan mode")
    print("    Claude CLI: YES (TodoWrite). SDK: leaks through, not documented.")


if __name__ == "__main__":
    asyncio.run(main())
