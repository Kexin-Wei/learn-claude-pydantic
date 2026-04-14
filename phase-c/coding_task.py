#!/usr/bin/env python3
"""Shared coding task — run the same prompt on each SDK and compare results.

Task: Create a Python CLI todo app with add, list, complete, delete commands.

Usage:
    uv run python phase-c/coding_task.py claude-sdk
    uv run python phase-c/coding_task.py claude-cli
    uv run python phase-c/coding_task.py openai
    uv run python phase-c/coding_task.py glm
    uv run python phase-c/coding_task.py all
"""
import asyncio
import json
import os
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

TASK_PROMPT = (
    "Create a Python CLI todo app in a single file called todo.py. Requirements:\n"
    "1. Commands: add <text>, list, complete <id>, delete <id>\n"
    "2. Use a JSON file (todos.json) for persistence\n"
    "3. Each todo has: id, text, completed (bool), created_at\n"
    "4. Handle errors (missing file, invalid id, etc.)\n"
    "5. Use argparse for CLI parsing\n"
    "After creating the file, run `python todo.py add 'Buy groceries'` and "
    "`python todo.py list` to verify it works."
)


def print_result(label: str, data: dict) -> None:
    """Print a test result row."""
    print(f"\n{'=' * 60}")
    print(f"RESULT: {label}")
    print("=" * 60)
    for k, v in data.items():
        print(f"  {k:<20} {v}")


# ── Claude Agent SDK ──────────────────────────────────────────

async def run_claude_sdk(workdir: str) -> dict:
    from claude_agent_sdk import (
        AssistantMessage, ClaudeAgentOptions, ResultMessage,
        ToolUseBlock, query,
    )

    model = os.environ.get("CLAUDE_MODEL")
    tool_counts: Counter[str] = Counter()
    start = time.time()

    async for msg in query(
        prompt=TASK_PROMPT,
        options=ClaudeAgentOptions(
            model=model,
            max_turns=20,
            cwd=workdir,
            permission_mode="bypassPermissions",
        ),
    ):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, ToolUseBlock):
                    tool_counts[block.name] += 1

        elif isinstance(msg, ResultMessage):
            elapsed = time.time() - start
            todo_exists = (Path(workdir) / "todo.py").exists()
            return {
                "Completed?": msg.subtype,
                "Turns": msg.num_turns,
                "Files created": len(list(Path(workdir).glob("*.py"))),
                "todo.py exists?": todo_exists,
                "Cost": f"${msg.total_cost_usd:.4f}" if msg.total_cost_usd else "N/A",
                "Duration": f"{elapsed:.1f}s",
                "Tools used": dict(tool_counts),
                "Used TodoWrite?": "TodoWrite" in tool_counts,
                "Used subagents?": any(t in tool_counts for t in ("Agent", "Task")),
            }

    return {"error": "no result message"}


# ── Claude CLI ────────────────────────────────────────────────

def run_claude_cli(workdir: str) -> dict:
    model = os.environ.get("CLAUDE_MODEL")
    cmd = [
        "claude", "-p", TASK_PROMPT,
        "--output-format", "stream-json",
        "--max-turns", "20",
        "--dangerously-skip-permissions",
    ]
    if model:
        cmd += ["--model", model]

    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=workdir)
    elapsed = time.time() - start

    tool_counts: Counter[str] = Counter()
    result_msg = {}
    for line in result.stdout.strip().splitlines():
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if msg.get("type") == "assistant":
            for block in msg.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    tool_counts[block["name"]] += 1
        elif msg.get("type") == "result":
            result_msg = msg

    todo_exists = (Path(workdir) / "todo.py").exists()
    return {
        "Completed?": result_msg.get("subtype", "unknown"),
        "Turns": result_msg.get("num_turns", "?"),
        "Files created": len(list(Path(workdir).glob("*.py"))),
        "todo.py exists?": todo_exists,
        "Cost": f"${result_msg['total_cost_usd']:.4f}" if result_msg.get("total_cost_usd") else "N/A",
        "Duration": f"{elapsed:.1f}s",
        "Tools used": dict(tool_counts),
        "Used TodoWrite?": "TodoWrite" in tool_counts,
        "Used subagents?": any(t in tool_counts for t in ("Agent", "Task")),
    }


# ── OpenAI Agents SDK ────────────────────────────────────────

async def run_openai(workdir: str) -> dict:
    from agents import Agent, Runner, function_tool

    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    @function_tool
    def write_file(path: str, content: str) -> str:
        """Write content to a file."""
        full = Path(workdir) / path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content)
        return f"Wrote {len(content)} chars to {path}"

    @function_tool
    def run_command(command: str) -> str:
        """Run a shell command."""
        r = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            cwd=workdir, timeout=30,
        )
        output = r.stdout + r.stderr
        return output[:2000] if output else "(no output)"

    @function_tool
    def read_file(path: str) -> str:
        """Read a file."""
        try:
            return (Path(workdir) / path).read_text()
        except FileNotFoundError:
            return f"Error: {path} not found"

    agent = Agent(
        name="coder",
        instructions="You are a coding assistant. Use tools to create files and run commands. Be thorough.",
        tools=[write_file, run_command, read_file],
        model=model,
    )

    tool_counts: Counter[str] = Counter()
    start = time.time()
    result = await Runner.run(agent, input=TASK_PROMPT, max_turns=20)
    elapsed = time.time() - start

    for item in result.new_items:
        name = type(item).__name__
        if "ToolCall" in name:
            # Extract tool name from the item
            raw = str(item)
            tool_counts[name] += 1

    todo_exists = (Path(workdir) / "todo.py").exists()
    return {
        "Completed?": "success" if todo_exists else "no todo.py",
        "Turns": len(result.raw_responses),
        "Files created": len(list(Path(workdir).glob("*.py"))),
        "todo.py exists?": todo_exists,
        "Cost": "N/A (check OpenAI dashboard)",
        "Duration": f"{elapsed:.1f}s",
        "Tools used": dict(tool_counts),
        "Used TodoWrite?": False,
        "Used subagents?": False,
    }


# ── GLM (Zhipu) ──────────────────────────────────────────────

def run_glm(workdir: str) -> dict:
    from zhipuai import ZhipuAI

    api_key = os.environ.get("ZHIPUAI_API_KEY")
    model = os.environ.get("GLM_MODEL", "glm-4-flash")

    if not api_key:
        return {"error": "Set ZHIPUAI_API_KEY in .env"}

    client = ZhipuAI(api_key=api_key)

    tools = [
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write content to a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                    },
                    "required": ["path", "content"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_command",
                "description": "Run a shell command",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string"},
                    },
                    "required": ["command"],
                },
            },
        },
    ]

    def execute_tool(name: str, args: dict) -> str:
        if name == "write_file":
            full = Path(workdir) / args["path"]
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(args["content"])
            return f"Wrote {len(args['content'])} chars to {args['path']}"
        elif name == "run_command":
            r = subprocess.run(
                args["command"], shell=True, capture_output=True, text=True,
                cwd=workdir, timeout=30,
            )
            output = r.stdout + r.stderr
            return output[:2000] if output else "(no output)"
        return f"Unknown tool: {name}"

    messages: list[dict] = [
        {"role": "system", "content": "You are a coding assistant. Use tools to create files and run commands."},
        {"role": "user", "content": TASK_PROMPT},
    ]

    tool_counts: Counter[str] = Counter()
    start = time.time()
    max_turns = 15

    for turn in range(max_turns):
        response = client.chat.completions.create(model=model, messages=messages, tools=tools)
        choice = response.choices[0]

        if choice.message.tool_calls:
            messages.append(choice.message.model_dump())
            for tc in choice.message.tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments)
                tool_counts[name] += 1
                result = execute_tool(name, args)
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
        else:
            break

    elapsed = time.time() - start
    todo_exists = (Path(workdir) / "todo.py").exists()
    return {
        "Completed?": "success" if todo_exists else "no todo.py",
        "Turns": turn + 1,
        "Files created": len(list(Path(workdir).glob("*.py"))),
        "todo.py exists?": todo_exists,
        "Cost": "N/A",
        "Duration": f"{elapsed:.1f}s",
        "Tools used": dict(tool_counts),
        "Used TodoWrite?": False,
        "Used subagents?": False,
    }


# ── Main ──────────────────────────────────────────────────────

RUNNERS = {
    "claude-sdk": ("Claude Agent SDK", lambda d: asyncio.run(run_claude_sdk(d))),
    "claude-cli": ("Claude CLI", run_claude_cli),
    "openai": ("OpenAI Agents SDK", lambda d: asyncio.run(run_openai(d))),
    "glm": ("GLM (Zhipu)", run_glm),
}


def main() -> None:
    targets = sys.argv[1:] if len(sys.argv) > 1 else ["all"]
    if "all" in targets:
        targets = list(RUNNERS.keys())

    results = {}
    for target in targets:
        if target not in RUNNERS:
            print(f"Unknown target: {target}")
            print(f"Available: {', '.join(RUNNERS.keys())}, all")
            return

        label, runner = RUNNERS[target]
        print(f"\n{'#' * 60}")
        print(f"# Running: {label}")
        print(f"# Task: Create a CLI todo app")
        print(f"{'#' * 60}")

        with tempfile.TemporaryDirectory(prefix=f"c1_task_{target}_") as tmpdir:
            data = runner(tmpdir)
            results[target] = data
            print_result(label, data)

            # Verify the todo app works
            todo_py = Path(tmpdir) / "todo.py"
            if todo_py.exists():
                print(f"\n  Verification:")
                for cmd in ["python todo.py add 'Test item'", "python todo.py list"]:
                    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=tmpdir)
                    status = "OK" if r.returncode == 0 else f"FAIL (exit {r.returncode})"
                    output = (r.stdout + r.stderr).strip()[:100]
                    print(f"    $ {cmd}")
                    print(f"      {status}: {output}")

    # Print summary table
    if len(results) > 1:
        print(f"\n{'=' * 60}")
        print("SUMMARY TABLE")
        print("=" * 60)
        headers = ["Metric"] + [RUNNERS[t][0] for t in results]
        metrics = ["Completed?", "Turns", "todo.py exists?", "Cost", "Duration", "Used TodoWrite?"]

        print(f"  {'Metric':<20}", end="")
        for t in results:
            print(f" {RUNNERS[t][0]:<20}", end="")
        print()
        print(f"  {'-'*20}", end="")
        for _ in results:
            print(f" {'-'*20}", end="")
        print()
        for metric in metrics:
            print(f"  {metric:<20}", end="")
            for t in results:
                val = str(results[t].get(metric, "N/A"))
                print(f" {val:<20}", end="")
            print()


if __name__ == "__main__":
    main()
