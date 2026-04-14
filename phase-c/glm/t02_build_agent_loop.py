#!/usr/bin/env python3
"""Exercise 2: Build an agent loop on GLM — what you have to DIY.

Shows what Claude Code gives you for free by building it from scratch on GLM.

Run: uv run python phase-c/glm/ex02_build_agent_loop.py
"""
import json
import os

from dotenv import load_dotenv
from zhipuai import ZhipuAI

load_dotenv(override=True)

API_KEY = os.environ.get("ZHIPUAI_API_KEY")
MODEL = os.environ.get("GLM_MODEL", "glm-4-flash")

# ── Define tools (you must implement every single one) ────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to read"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in a directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path", "default": "."},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to write"},
                    "content": {"type": "string", "description": "Content to write"},
                },
                "required": ["path", "content"],
            },
        },
    },
]


def execute_tool(name: str, args: dict) -> str:
    """Execute a tool call — YOU implement all of this."""
    if name == "read_file":
        try:
            return open(args["path"]).read()
        except FileNotFoundError:
            return f"Error: file not found: {args['path']}"
    elif name == "list_files":
        path = args.get("path", ".")
        try:
            return "\n".join(os.listdir(path))
        except FileNotFoundError:
            return f"Error: directory not found: {path}"
    elif name == "write_file":
        with open(args["path"], "w") as f:
            f.write(args["content"])
        return f"Wrote {len(args['content'])} chars to {args['path']}"
    return f"Unknown tool: {name}"


def agent_loop(prompt: str, max_turns: int = 10) -> None:
    """A minimal agent loop — what Claude Code gives you for free.

    With Claude Agent SDK: 3 lines (query + async for + print).
    With GLM: you build ALL of this yourself.
    """
    client = ZhipuAI(api_key=API_KEY)
    messages: list[dict] = [
        {"role": "system", "content": "You are a helpful coding assistant. Use tools to complete tasks."},
        {"role": "user", "content": prompt},
    ]

    print(f"  Prompt: {prompt}")

    for turn in range(max_turns):
        print(f"\n--- Turn {turn + 1} ---")

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
        )
        choice = response.choices[0]
        message = choice.message

        # If model wants to use tools
        if message.tool_calls:
            # Append assistant message with tool calls
            messages.append(message.model_dump())

            for tool_call in message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                print(f"  [TOOL] {name}({args})")

                result = execute_tool(name, args)
                print(f"  [RESULT] {result[:100]}...")

                # Append tool result
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
        else:
            # Model is done — print final response
            print(f"  [DONE] {message.content}")
            return

    print("  [MAX TURNS REACHED]")


def main() -> None:
    if not API_KEY:
        print("ERROR: Set ZHIPUAI_API_KEY in .env")
        return

    print("=" * 60)
    print("DIY Agent Loop on GLM")
    print("=" * 60)
    print("Task: List files in current directory and read this script")

    agent_loop("List the files in the current directory, then read ex01_glm_basics.py and tell me what it does in one sentence.")

    print(f"\n{'=' * 60}")
    print("WHAT YOU HAD TO BUILD YOURSELF")
    print("=" * 60)
    print("  1. Tool definitions (JSON schema for each tool)")
    print("  2. Tool execution (dispatch + implement every tool)")
    print("  3. Agent loop (while tool_calls: execute + re-call)")
    print("  4. Message history management")
    print("  5. Error handling, timeouts, max turns")
    print()
    print("  What Claude Agent SDK gives you for FREE:")
    print("    • 10 built-in tools (Read, Write, Edit, Bash, Glob, Grep, ...)")
    print("    • Agent loop with automatic tool dispatch")
    print("    • Permission system, hooks, session management")
    print("    • Subagent orchestration")
    print("    • Streaming, structured output, thinking config")
    print()
    print("  GLM SDK = raw LLM API (you build everything)")
    print("  Claude Agent SDK = full agent harness (batteries included)")


if __name__ == "__main__":
    main()
