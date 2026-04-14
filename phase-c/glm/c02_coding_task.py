#!/usr/bin/env python3
"""Coding task — Build expense tracker CLI using GLM via z.ai proxy.

Uses Claude Agent SDK pointed at z.ai so GLM models handle the task
with full Claude tooling (Read/Write/Bash/etc.).

Run: uv run python phase-c/glm/c02_coding_task.py

Results saved to phase-c/glm/results/
"""
import asyncio
import json
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
    "5. cli.py should be runnable as `python {workdir}/expense_tracker/cli.py <command>`\n"
    "\n"
    "Workflow (MANDATORY):\n"
    "- FIRST, use the TodoWrite tool to create a task list breaking down the work into steps.\n"
    "  Update each todo item as you complete it.\n"
    "- Use the Agent tool (subagents) to parallelize independent work. For example,\n"
    "  delegate writing models.py and storage.py to separate subagents simultaneously.\n"
    "\n"
    "After creating all files:\n"
    "  1. Run the tests: cd {workdir} && uv run python -m pytest expense_tracker/test_tracker.py -v || uv run python -m unittest expense_tracker/test_tracker.py -v\n"
    "  2. Run: cd {workdir} && uv run python expense_tracker/cli.py add --amount 12.50 --category food --desc 'Lunch'\n"
    "  3. Run: cd {workdir} && uv run python expense_tracker/cli.py add --amount 45.00 --category transport --desc 'Taxi'\n"
    "  4. Run: cd {workdir} && uv run python expense_tracker/cli.py list\n"
    "  5. Run: cd {workdir} && uv run python expense_tracker/cli.py summary\n"
    "All commands must succeed."
)


def load_zai_env() -> bool:
    """Load z.ai proxy env vars from .claude/settings.local.json."""
    settings_path = Path(__file__).parent / ".claude" / "settings.local.json"
    if not settings_path.exists():
        print(f"ERROR: {settings_path} not found")
        print("Create it with your z.ai API key:")
        print('  {"env": {"ANTHROPIC_AUTH_TOKEN": "your-key"}}')
        return False
    try:
        settings = json.loads(settings_path.read_text())
        env = settings.get("env", {})
        token = env.get("ANTHROPIC_AUTH_TOKEN", "")
        if not token or token == "your-zai-api-key-here":
            print("ERROR: Replace placeholder in settings.local.json with your real z.ai API key")
            return False
        os.environ["ANTHROPIC_AUTH_TOKEN"] = token
        os.environ.setdefault("ANTHROPIC_BASE_URL", "https://api.z.ai/api/anthropic")
        os.environ.setdefault("API_TIMEOUT_MS", "3000000")
        os.environ.setdefault("CLAUDE_MODEL", env.get("CLAUDE_MODEL", "sonnet"))
        return True
    except (json.JSONDecodeError, KeyError) as e:
        print(f"ERROR: Failed to parse settings.local.json: {e}")
        return False


def check_output(workdir: str) -> dict:
    found = [f for f in EXPECTED_FILES if (Path(workdir) / f).exists()]
    return {
        "expected_found": found,
        "all_files": len(list(Path(workdir).rglob("*.py"))),
        "cli_exists": (Path(workdir) / "expense_tracker" / "cli.py").exists(),
    }


async def run(workdir: str) -> dict:
    from claude_agent_sdk import (
        AssistantMessage, ClaudeAgentOptions, ResultMessage,
        TextBlock, ToolUseBlock, query,
    )

    model = os.environ.get("CLAUDE_MODEL", "sonnet")
    tool_counts: Counter[str] = Counter()
    start = time.time()

    task_prompt = TASK_PROMPT_TEMPLATE.format(workdir=workdir)

    async for msg in query(
        prompt=task_prompt,
        options=ClaudeAgentOptions(
            model=model,
            max_turns=20,
            cwd=workdir,
            permission_mode="bypassPermissions",
        ),
    ):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"\n  {block.text[:200]}", flush=True)
                elif isinstance(block, ToolUseBlock):
                    tool_counts[block.name] += 1
                    print(f"  [{block.name}]", end="", flush=True)
        elif isinstance(msg, ResultMessage):
            print()
            elapsed = time.time() - start
            out = check_output(workdir)
            return {
                "SDK": "GLM via z.ai (Claude Agent SDK)",
                "Completed": "success" if msg.subtype == "success" and len(out["expected_found"]) == len(EXPECTED_FILES) else "fail",
                "Turns": msg.num_turns,
                "Files created": out["all_files"],
                "Expected files": f"{len(out['expected_found'])}/{len(EXPECTED_FILES)}",
                "Cost": f"${msg.total_cost_usd:.4f}" if msg.total_cost_usd else "N/A",
                "Duration": f"{elapsed:.1f}s",
                "Tools used": dict(tool_counts),
                "TodoWrite": "TodoWrite" in tool_counts,
                "Subagents": any(t in tool_counts for t in ("Agent", "Task")),
            }

    return {"error": "no result message"}


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
    if not load_zai_env():
        return

    if RESULTS_DIR.exists():
        shutil.rmtree(RESULTS_DIR)
    RESULTS_DIR.mkdir(parents=True)

    model = os.environ.get("CLAUDE_MODEL", "sonnet")
    print("=" * 60)
    print("Coding Task: GLM via z.ai proxy")
    print(f"  Model:  {model} (mapped by z.ai)")
    print(f"  Proxy:  {os.environ.get('ANTHROPIC_BASE_URL')}")
    print(f"  Output: {RESULTS_DIR}")
    print("=" * 60)

    result = asyncio.run(run(str(RESULTS_DIR)))
    for k, v in result.items():
        print(f"  {k:<20} {v}")
    verify(str(RESULTS_DIR))


if __name__ == "__main__":
    main()
