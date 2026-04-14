#!/usr/bin/env python3
"""Probe Claude Code CLI features and write a row to phase-c/c01_comparison.csv.

Run: uv run python phase-c/claude-code-cli/comparison_probe.py
"""
import csv
import json
import shutil
import subprocess
from pathlib import Path

CSV_PATH = Path(__file__).parent.parent / "c01_comparison.csv"
SDK_NAME = "Claude CLI"

FEATURES = [
    "Agent loop", "Custom tools", "Web search", "File tools", "Code execution",
    "Structured output", "Multi-agent", "Guardrails", "Hooks / lifecycle",
    "Tracing dashboard", "Permission system", "Plan mode", "TodoWrite / tasks",
    "MCP support", "Streaming", "Session resume",
]


def yn(val: bool) -> str:
    return "Yes" if val else "No"


def cli_help() -> str:
    """Get claude --help output for feature detection."""
    try:
        r = subprocess.run(["claude", "--help"], capture_output=True, text=True, timeout=10)
        return r.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""


def probe() -> dict[str, str]:
    has_cli = shutil.which("claude") is not None
    help_text = cli_help() if has_cli else ""

    has_resume = "--resume" in help_text or "-r, --resume" in help_text
    has_perm_mode = "--permission-mode" in help_text
    has_output_fmt = "--output-format" in help_text
    has_stream_json = "stream-json" in help_text
    has_mcp = "--mcp-config" in help_text or "mcp" in help_text
    has_tools_flag = "--tools" in help_text
    has_model = "--model" in help_text
    has_effort = "--effort" in help_text
    has_worktree = "--worktree" in help_text
    has_verbose = "--verbose" in help_text
    has_json_schema = "--json-schema" in help_text
    has_agents = "--agent" in help_text
    has_print = "--print" in help_text

    return {
        "Agent loop": f"{yn(has_cli)} (built-in)",
        "Custom tools": f"{yn(has_mcp)} (--mcp-config)",
        "Web search": f"{yn(has_tools_flag)} (built-in WebSearch tool)",
        "File tools": f"{yn(has_tools_flag)} (built-in Read/Write/Glob/Grep)",
        "Code execution": f"{yn(has_tools_flag)} (built-in Bash tool)",
        "Structured output": f"{yn(has_json_schema)} (--json-schema / --output-format)",
        "Multi-agent": f"{yn(has_agents)} (--agent / Agent tool)",
        "Guardrails": f"{yn(has_perm_mode)} (hooks + permission modes)",
        "Hooks / lifecycle": f"{yn(has_perm_mode)} (PreToolUse / Stop / ...)",
        "Tracing dashboard": f"{yn(False)} (not available)",
        "Permission system": f"{yn(has_perm_mode)} (--permission-mode)",
        "Plan mode": f"{yn(has_perm_mode)} (--permission-mode plan)",
        "TodoWrite / tasks": f"{yn(has_cli)}",
        "MCP support": f"{yn(has_mcp)} (--mcp-config)",
        "Streaming": f"{yn(has_stream_json)} (--output-format stream-json)",
        "Session resume": f"{yn(has_resume)} (--resume / --continue)",
    }


def upsert_csv(sdk_name: str, row: dict[str, str]) -> None:
    """Read existing CSV (features=rows, SDKs=columns), update this SDK's column, write back."""
    data: dict[str, dict[str, str]] = {f: {} for f in FEATURES}
    sdks: list[str] = []
    if CSV_PATH.exists():
        with open(CSV_PATH, newline="") as f:
            reader = csv.DictReader(f)
            sdks = [c for c in (reader.fieldnames or []) if c != "Feature"]
            for r in reader:
                feat = r.get("Feature", "")
                if feat in data:
                    for s in sdks:
                        if s in r:
                            data[feat][s] = r[s]
    if sdk_name not in sdks:
        sdks.append(sdk_name)
    for feat, val in row.items():
        if feat in data:
            data[feat][sdk_name] = val
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Feature"] + sdks)
        writer.writeheader()
        for feat in FEATURES:
            writer.writerow({"Feature": feat, **data[feat]})


def main() -> None:
    print(f"Probing {SDK_NAME}...")
    row = probe()
    for feat, val in row.items():
        print(f"  {feat:<22} {val}")
    upsert_csv(SDK_NAME, row)
    print(f"\nWrote to {CSV_PATH}")


if __name__ == "__main__":
    main()
