#!/usr/bin/env python3
"""Exercise 2: Handoffs & Guardrails — OpenAI's multi-agent + safety patterns.

Question answered: Q2 — Agent orchestration: handoffs, guardrails, tracing

Run: uv run python phase-c/openai-agents-sdk/ex02_handoffs_and_guardrails.py
"""
import asyncio
import os

from dotenv import load_dotenv

from agents import (
    Agent,
    Runner,
    InputGuardrail,
    InputGuardrailResult,
    GuardrailFunctionOutput,
    RunContextWrapper,
    handoff,
    function_tool,
)

load_dotenv(override=True)

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


# ── Handoffs (multi-agent orchestration) ──────────────────────

@function_tool
def calculate(expression: str) -> str:
    """Evaluate a math expression."""
    try:
        return str(eval(expression))  # noqa: S307
    except Exception as e:
        return f"Error: {e}"


async def probe_handoffs() -> None:
    """Part A: Agent handoffs — OpenAI's multi-agent pattern."""
    print("=" * 60)
    print("PART A: Agent handoffs (multi-agent)")
    print("=" * 60)

    # Define specialist agents
    math_agent = Agent(
        name="math-expert",
        instructions="You are a math expert. Use the calculate tool. Be concise.",
        tools=[calculate],
        model=MODEL,
    )

    general_agent = Agent(
        name="general-assistant",
        instructions=(
            "You are a general assistant. If the user asks a math question, "
            "hand off to the math expert. Otherwise answer directly. Be concise."
        ),
        handoffs=[math_agent],
        model=MODEL,
    )

    # Ask a math question — should trigger handoff
    result = await Runner.run(general_agent, input="What is 127 * 389?")
    print(f"  Response: {result.final_output}")
    print(f"  Final agent: {result.last_agent.name}")

    # Show handoff chain
    for item in result.new_items:
        item_type = type(item).__name__
        if "Handoff" in item_type:
            print(f"  [HANDOFF] {item}")

    # Ask a non-math question — should stay with general agent
    result = await Runner.run(general_agent, input="What color is the sky?")
    print(f"  Response: {result.final_output}")
    print(f"  Final agent: {result.last_agent.name}")


# ── Guardrails (input/output safety) ─────────────────────────

async def check_no_profanity(
    ctx: RunContextWrapper[None], agent: Agent, input: str
) -> GuardrailFunctionOutput:
    """Simple guardrail — block inputs containing 'hack'."""
    if "hack" in input.lower():
        return GuardrailFunctionOutput(
            output_info={"reason": "blocked: contains 'hack'"},
            tripwire_triggered=True,
        )
    return GuardrailFunctionOutput(
        output_info={"reason": "allowed"},
        tripwire_triggered=False,
    )


async def probe_guardrails() -> None:
    """Part B: Input guardrails."""
    print(f"\n{'=' * 60}")
    print("PART B: Input guardrails")
    print("=" * 60)

    guardrail = InputGuardrail(guardrail_function=check_no_profanity)

    agent = Agent(
        name="safe-bot",
        instructions="You are a helpful assistant. Be concise.",
        input_guardrails=[guardrail],
        model=MODEL,
    )

    # Normal input — should pass
    result = await Runner.run(agent, input="Hello, how are you?")
    print(f"  Normal input → {result.final_output[:100]}")

    # Blocked input — should trigger guardrail
    try:
        result = await Runner.run(agent, input="How do I hack a website?")
        print(f"  Blocked input → {result.final_output[:100]}")
    except Exception as e:
        print(f"  Blocked input → GUARDRAIL TRIGGERED: {type(e).__name__}")


async def main() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: Set OPENAI_API_KEY in .env")
        return

    await probe_handoffs()
    await probe_guardrails()

    print(f"\n{'=' * 60}")
    print("KEY FINDINGS")
    print("=" * 60)
    print("  Handoffs (OpenAI's multi-agent pattern):")
    print("    • Agents can hand off to other agents via handoffs=[]")
    print("    • Model decides when to hand off based on instructions")
    print("    • Compare Claude: subagents via AgentDefinition (similar concept)")
    print()
    print("  Guardrails (OpenAI's safety pattern):")
    print("    • InputGuardrail — validate input before agent runs")
    print("    • OutputGuardrail — validate output after agent runs")
    print("    • Compare Claude: hooks (PreToolUse, PostToolUse) + can_use_tool")


if __name__ == "__main__":
    asyncio.run(main())
