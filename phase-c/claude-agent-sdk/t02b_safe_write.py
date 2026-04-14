#!/usr/bin/env python3
"""Exercise 2b: Sandboxed file writing with a custom safe_write tool.

Demonstrates how to replace the built-in Write tool with a sandboxed version
that validates all file paths stay inside the workspace directory.

Pattern: disallowed_tools + create_sdk_mcp_server = sandboxed tools

Run: uv run python phase-c/claude-agent-sdk/ex02b_safe_write.py
"""
import asyncio
import os
import tempfile
from collections import Counter
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


def make_safe_write_tool(workdir: str):
    """Create a safe_write tool that only writes inside workdir."""
    workdir_path = Path(workdir).resolve()

    @tool(
        "safe_write",
        "Write a file. The file_path must be relative (e.g. 'calc.py'). "
        "Files are written inside the workspace directory.",
        {"file_path": str, "content": str},
    )
    async def safe_write(args: dict) -> dict:
        file_path = args["file_path"]
        content = args["content"]

        resolved = (workdir_path / file_path).resolve()
        if not resolved.is_relative_to(workdir_path):
            return {
                "content": [{"type": "text", "text": f"BLOCKED: path '{file_path}' escapes workspace"}],
                "is_error": True,
            }

        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content)
        return {"content": [{"type": "text", "text": f"Wrote {len(content)} bytes to {file_path}"}]}

    return safe_write


def _truncate(s: str, max_len: int = 120) -> str:
    return s[:max_len] + "..." if len(s) > max_len else s


async def main() -> None:
    print("=" * 60)
    print("safe_write — sandboxed file creation")
    print("=" * 60)
    print("  Built-in Write/Edit are BLOCKED via disallowed_tools.")
    print("  A custom safe_write MCP tool enforces workspace boundary.")
    print()

    tool_counts: Counter[str] = Counter()

    with tempfile.TemporaryDirectory(prefix="c1_ex02b_") as tmpdir:
        safe_write = make_safe_write_tool(tmpdir)
        server = create_sdk_mcp_server("sandbox", tools=[safe_write])

        print(f"  Workspace: {tmpdir}")

        async for msg in query(
            prompt=(
                "Create a Python calculator project with:\n"
                "1. calc.py — add, subtract, multiply, divide functions\n"
                "2. test_calc.py — pytest tests for each function\n"
                "3. README.md — document the API\n"
                "Track your progress with todos as you go.\n"
                "Use the safe_write tool to create files (not Write)."
            ),
            options=ClaudeAgentOptions(
                model=MODEL,
                max_turns=20,
                cwd=tmpdir,
                disallowed_tools=["Write"],
                mcp_servers={"sandbox": server},
                permission_mode="bypassPermissions",
            ),
        ):
            print(f"  >> {type(msg).__name__}")
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, ToolUseBlock):
                        tool_counts[block.name] += 1
                        if block.name == "mcp__sandbox__safe_write":
                            path = block.input.get("file_path", "?")
                            content_len = len(block.input.get("content", ""))
                            print(f"  [safe_write] {path} ({content_len} chars)")
                        else:
                            print(f"  [{block.name}] {_truncate(str(block.input), 200)}")
                    elif isinstance(block, TextBlock) and block.text.strip():
                        print(f"  [TEXT] {_truncate(block.text.strip())}")

            elif isinstance(msg, ResultMessage):
                cost = f", cost=${msg.total_cost_usd:.4f}" if msg.total_cost_usd else ""
                print(f"\n  Result: {msg.subtype}, turns={msg.num_turns}{cost}")

        # Show what was created
        files = sorted(
            f.relative_to(tmpdir)
            for f in Path(tmpdir).rglob("*")
            if f.is_file()
        )
        print(f"\n  Files created in sandbox:")
        for f in files:
            size = (Path(tmpdir) / f).stat().st_size
            print(f"    {f} ({size} bytes)")

    print(f"\n  Tools used: {dict(tool_counts)}")
    safe_count = tool_counts.get("mcp__sandbox__safe_write", 0)
    print(f"  built-in Write used: {'YES' if 'Write' in tool_counts else 'NO (blocked)'}")
    print(f"  safe_write used: {safe_count} times")

    print("\n" + "=" * 60)
    print("KEY TAKEAWAY")
    print("=" * 60)
    print(f"  • built-in Write blocked: {'YES (not used)' if 'Write' not in tool_counts else 'NO (Write was still used!)'}")
    print(f"  • safe_write invoked: {safe_count} times")
    if safe_count > 0 and "Write" not in tool_counts:
        print("  • pattern works: disallowed_tools + create_sdk_mcp_server = sandboxed tools")
    elif safe_count == 0:
        print("  • safe_write was not used — model may have used Bash or another workaround")


if __name__ == "__main__":
    asyncio.run(main())
