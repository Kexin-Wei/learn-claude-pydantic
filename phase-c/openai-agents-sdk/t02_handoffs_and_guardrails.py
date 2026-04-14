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


async def probe_handoffs() -> dict:
    """Part A: Agent handoffs — OpenAI's multi-agent pattern."""
    print("=" * 60)
    print("PART A: Agent handoffs (multi-agent)")
    print("=" * 60)

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
    math_agent_name = result.last_agent.name
    handoff_occurred = any("Handoff" in type(item).__name__ for item in result.new_items)

    for item in result.new_items:
        item_type = type(item).__name__
        if "Handoff" in item_type:
            print(f"  [HANDOFF] {item}")

    # Ask a non-math question — should stay with general agent
    result2 = await Runner.run(general_agent, input="What color is the sky?")
    print(f"  Response: {result2.final_output}")
    print(f"  Final agent: {result2.last_agent.name}")
    stayed = result2.last_agent.name == "general-assistant"

    return {
        "handoff_occurred": handoff_occurred,
        "routed_to": math_agent_name,
        "non_math_stayed": stayed,
    }


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


async def probe_guardrails() -> dict:
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
    normal_passed = bool(result.final_output)
    print(f"  Normal input → {result.final_output[:100]}")

    # Blocked input — should trigger guardrail
    blocked = False
    try:
        result = await Runner.run(agent, input="How do I hack a website?")
        print(f"  Blocked input → {result.final_output[:100]}")
    except Exception as e:
        blocked = True
        print(f"  Blocked input → GUARDRAIL TRIGGERED: {type(e).__name__}")

    return {"normal_passed": normal_passed, "blocked": blocked}


async def main() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: Set OPENAI_API_KEY in .env")
        return

    handoff_results = await probe_handoffs()
    guardrail_results = await probe_guardrails()

    def yn(val: bool) -> str:
        return "YES" if val else "NO"

    print(f"\n{'=' * 60}")
    print("KEY FINDINGS")
    print("=" * 60)
    print("  Handoffs (multi-agent orchestration):")
    print(f"    {yn(handoff_results['handoff_occurred'])}  Handoff triggered (routed to: {handoff_results['routed_to']})")
    print(f"    {yn(handoff_results['non_math_stayed'])}  Non-matching input stayed with original agent")
    print()
    print("  Guardrails (input safety):")
    print(f"    {yn(guardrail_results['normal_passed'])}  Normal input passed through")
    print(f"    {yn(guardrail_results['blocked'])}  Harmful input blocked by InputGuardrail")


if __name__ == "__main__":
    asyncio.run(main())
