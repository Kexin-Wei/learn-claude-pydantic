#!/usr/bin/env python3
"""Exercise 1: GLM Basics — Chat completion and tool use.

Question answered: Q1 — Agent capabilities: tool use, multi-turn, code execution

Run: uv run python phase-c/glm/ex01_glm_basics.py
"""
import json
import os

from dotenv import load_dotenv
from zhipuai import ZhipuAI

load_dotenv(override=True)

API_KEY = os.environ.get("ZHIPUAI_API_KEY")
MODEL = os.environ.get("GLM_MODEL", "glm-4-flash")


def probe_basic_chat() -> None:
    """Part A: Basic chat completion."""
    print("=" * 60)
    print(f"PART A: Basic chat completion (model={MODEL})")
    print("=" * 60)

    client = ZhipuAI(api_key=API_KEY)
    user_prompt = "What is 2 + 2? Answer in one word."
    print(f"  Prompt: {user_prompt}")
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Be concise."},
            {"role": "user", "content": user_prompt},
        ],
    )

    choice = response.choices[0]
    print(f"  Response: {choice.message.content}")
    print(f"  Model: {response.model}")
    print(f"  Usage: {response.usage}")
    print(f"  Finish reason: {choice.finish_reason}")


def probe_multi_turn() -> None:
    """Part B: Multi-turn conversation."""
    print(f"\n{'=' * 60}")
    print("PART B: Multi-turn conversation")
    print("=" * 60)

    client = ZhipuAI(api_key=API_KEY)
    user_prompt = "What is the Pythagorean theorem?"
    messages = [
        {"role": "system", "content": "You are a math tutor. Be concise."},
        {"role": "user", "content": user_prompt},
    ]

    # Turn 1
    print(f"  Prompt (turn 1): {user_prompt}")
    response = client.chat.completions.create(model=MODEL, messages=messages)
    reply1 = response.choices[0].message.content
    print(f"  Turn 1: {reply1[:150]}...")

    # Turn 2 — follow-up
    messages.append({"role": "assistant", "content": reply1})
    followup_prompt = "Give me a concrete example with numbers."
    messages.append({"role": "user", "content": followup_prompt})
    print(f"  Prompt (turn 2): {followup_prompt}")
    response = client.chat.completions.create(model=MODEL, messages=messages)
    reply2 = response.choices[0].message.content
    print(f"  Turn 2: {reply2[:150]}...")


def probe_tool_use() -> None:
    """Part C: Function calling / tool use."""
    print(f"\n{'=' * 60}")
    print("PART C: Function calling (tool use)")
    print("=" * 60)

    client = ZhipuAI(api_key=API_KEY)

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather for a city",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The city name, e.g. Beijing",
                        },
                    },
                    "required": ["city"],
                },
            },
        },
    ]

    user_prompt = "What's the weather in Beijing?"
    messages = [
        {"role": "user", "content": user_prompt},
    ]

    # First call — model should request tool use
    print(f"  Prompt: {user_prompt}")
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
    )
    choice = response.choices[0]
    print(f"  Finish reason: {choice.finish_reason}")

    if choice.message.tool_calls:
        tool_call = choice.message.tool_calls[0]
        print(f"  Tool call: {tool_call.function.name}({tool_call.function.arguments})")

        # Simulate tool result
        messages.append(choice.message.model_dump())
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps({"city": "Beijing", "temp": "22°C", "condition": "sunny"}),
        })

        # Second call — model uses tool result
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
        )
        print(f"  Final response: {response.choices[0].message.content[:200]}")
    else:
        print(f"  No tool call — model responded directly: {choice.message.content[:200]}")


def probe_streaming() -> None:
    """Part D: Streaming response."""
    print(f"\n{'=' * 60}")
    print("PART D: Streaming")
    print("=" * 60)

    client = ZhipuAI(api_key=API_KEY)
    user_prompt = "Count from 1 to 5, one number per line."
    print(f"  Prompt: {user_prompt}")
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": user_prompt}],
        stream=True,
    )

    print("  Stream: ", end="")
    for chunk in response:
        delta = chunk.choices[0].delta
        if delta.content:
            print(delta.content, end="", flush=True)
    print()


def main() -> None:
    if not API_KEY:
        print("ERROR: Set ZHIPUAI_API_KEY in .env")
        print("Get your key at: https://open.bigmodel.cn/")
        return

    probe_basic_chat()
    probe_multi_turn()
    probe_tool_use()
    probe_streaming()

    print(f"\n{'=' * 60}")
    print("KEY FINDINGS")
    print("=" * 60)
    print("  GLM SDK provides (raw LLM API):")
    print("    YES  Chat completions (messages in, message out)")
    print("    YES  Function calling (you define tools, model requests calls)")
    print("    YES  Streaming (SSE-style chunks)")
    print("    YES  Multi-turn (you manage message history yourself)")
    print()
    print("  GLM SDK does NOT provide:")
    print("    NO   Agent loop — you build the while loop yourself")
    print("    NO   Built-in tools — no Bash, Read, Write, Glob, etc.")
    print("    NO   TodoWrite / task management")
    print("    NO   Hooks / lifecycle events")
    print("    NO   Subagents / agent orchestration")
    print("    NO   Plan mode")
    print("    NO   Session management / resume")
    print("    NO   Permission system")
    print()
    print("  The ZhipuAI SDK is comparable to the RAW Anthropic SDK")
    print("  (client.messages.create), not to the Claude Agent SDK.")
    print("  The gap between this and Claude Code is the entire harness.")


if __name__ == "__main__":
    main()
