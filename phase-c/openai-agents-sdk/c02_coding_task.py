#!/usr/bin/env python3
"""Coding task — Build expense tracker CLI using OpenAI Agents SDK.

Run: uv run python phase-c/openai-agents-sdk/coding_task.py

Results saved to phase-c/openai-agents-sdk/results/
"""
import asyncio
import os
import shutil
import subprocess
import time
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

RESULTS_DIR = Path(__file__).parent / "results"

EXPECTED_FILES = [
    "expense_tracker/models.py",
    "expense_tracker/storage.py",
    "expense_tracker/cli.py",
    "expense_tracker/test_tracker.py",
]

TASK_PROMPT_TEMPLATE = (
    "Build a multi-file Python expense tracker CLI.\n"
    "IMPORTANT: All files MUST be created under the directory {workdir}.\n"
    "Use absolute paths when writing files.\n"
    "\n"
    "Structure (all paths under {workdir}):\n"
    "\n"
    "  {workdir}/expense_tracker/models.py      — Expense dataclass (id, amount, category, description, date)\n"
    "  {workdir}/expense_tracker/storage.py     — ExpenseStore class: load/save JSON, CRUD operations\n"
    "  {workdir}/expense_tracker/cli.py         — argparse entry point\n"
    "  {workdir}/expense_tracker/test_tracker.py — at least 3 unit tests using unittest\n"
    "\n"
    "Requirements:\n"
    "1. Commands: add --amount 12.50 --category food --desc 'Lunch'\n"
    "             list [--category food] [--since 2025-01-01]\n"
    "             summary  (total per category)\n"
    "             delete <id>\n"
    "2. storage.py must use a JSON file (expenses.json) for persistence\n"
    "3. summary command prints a table of category totals\n"
    "4. Handle errors gracefully (missing file, invalid amount, unknown category)\n"
    "5. cli.py should be runnable as `uv run python {workdir}/expense_tracker/cli.py <command>`\n"
    "\n"
    "After creating all files:\n"
    "  1. Run the tests: cd {workdir} && uv run python -m pytest expense_tracker/test_tracker.py -v || uv run python -m unittest expense_tracker/test_tracker.py -v\n"
    "  2. Run: cd {workdir} && uv run python expense_tracker/cli.py add --amount 12.50 --category food --desc 'Lunch'\n"
    "  3. Run: cd {workdir} && uv run python expense_tracker/cli.py add --amount 45.00 --category transport --desc 'Taxi'\n"
    "  4. Run: cd {workdir} && uv run python expense_tracker/cli.py list\n"
    "  5. Run: cd {workdir} && uv run python expense_tracker/cli.py summary\n"
    "All commands must succeed."
)


def check_output(workdir: str) -> dict:
    found = [f for f in EXPECTED_FILES if (Path(workdir) / f).exists()]
    return {
        "expected_found": found,
        "all_files": len(list(Path(workdir).rglob("*.py"))),
        "cli_exists": (Path(workdir) / "expense_tracker" / "cli.py").exists(),
    }


async def run(workdir: str) -> dict:
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
    task_prompt = TASK_PROMPT_TEMPLATE.format(workdir=workdir)
    result = await Runner.run(agent, input=task_prompt, max_turns=20)
    elapsed = time.time() - start

    for item in result.new_items:
        name = type(item).__name__
        if "ToolCall" in name:
            tool_counts[name] += 1

    out = check_output(workdir)
    return {
        "SDK": "OpenAI Agents SDK",
        "Completed": "success" if out["cli_exists"] else "missing cli.py",
        "Turns": len(result.raw_responses),
        "Files created": out["all_files"],
        "Expected files": f"{len(out['expected_found'])}/{len(EXPECTED_FILES)}",
        "Cost": "N/A (check OpenAI dashboard)",
        "Duration": f"{elapsed:.1f}s",
        "Tools used": dict(tool_counts),
        "TodoWrite": False,
        "Subagents": False,
    }


def verify(workdir: str) -> None:
    cli_py = Path(workdir) / "expense_tracker" / "cli.py"
    if not cli_py.exists():
        print("  cli.py not found, skipping verification")
        return
    print("\n  Verification:")
    for cmd in [
        "uv run python expense_tracker/cli.py add --amount 9.99 --category test --desc 'Verify'",
        "uv run python expense_tracker/cli.py list",
        "uv run python expense_tracker/cli.py summary",
    ]:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=workdir)
        status = "OK" if r.returncode == 0 else f"FAIL (exit {r.returncode})"
        output = (r.stdout + r.stderr).strip()[:100]
        print(f"    $ {cmd}")
        print(f"      {status}: {output}")


def main() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: Set OPENAI_API_KEY in .env")
        return

    if RESULTS_DIR.exists():
        shutil.rmtree(RESULTS_DIR)
    RESULTS_DIR.mkdir(parents=True)

    print("=" * 60)
    print("Coding Task: OpenAI Agents SDK")
    print(f"Output: {RESULTS_DIR}")
    print("=" * 60)

    result = asyncio.run(run(str(RESULTS_DIR)))
    for k, v in result.items():
        print(f"  {k:<20} {v}")
    verify(str(RESULTS_DIR))


if __name__ == "__main__":
    main()
