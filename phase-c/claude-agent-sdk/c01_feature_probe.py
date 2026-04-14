#!/usr/bin/env python3
"""Probe Claude Agent SDK features and write a row to phase-c/c01_comparison.csv.

Run: uv run python phase-c/claude-agent-sdk/comparison_probe.py
"""
import csv
import importlib
from pathlib import Path

CSV_PATH = Path(__file__).parent.parent / "c01_comparison.csv"
SDK_NAME = "Claude Agent SDK"

FEATURES = [
    "Agent loop", "Custom tools", "Web search", "File tools", "Code execution",
    "Structured output", "Multi-agent", "Guardrails", "Hooks / lifecycle",
    "Tracing dashboard", "Permission system", "Plan mode", "TodoWrite / tasks",
    "MCP support", "Streaming", "Session resume",
]


def check(module: str, attr: str) -> bool:
    try:
        return hasattr(importlib.import_module(module), attr)
    except ImportError:
        return False


def yn(val: bool) -> str:
    return "Yes" if val else "No"


def sdk(attr: str) -> bool:
    return check("claude_agent_sdk", attr)


def probe() -> dict[str, str]:
    has_query = sdk("query")
    has_tool = sdk("tool")
    has_mcp = sdk("McpServerConfig")
    has_subagent = sdk("TaskStartedMessage")
    has_hooks_pre = sdk("PreToolUseHookInput")
    has_hooks_stop = sdk("StopHookInput")
    has_hooks_sub = sdk("SubagentStartHookInput")
    has_perm = sdk("PermissionMode")
    has_session = sdk("list_sessions")
    has_stream = sdk("StreamEvent")
    has_thinking = sdk("ThinkingConfig")
    has_options = sdk("ClaudeAgentOptions")
    has_sandbox = sdk("SandboxSettings")
    has_can_use = sdk("CanUseTool")

    return {
        "Agent loop": f"{yn(has_query)} (query())",
        "Custom tools": f"{yn(has_tool and has_mcp)} (@tool + MCP)",
        "Web search": f"{yn(has_query)} (built-in WebSearch tool)",
        "File tools": f"{yn(has_query)} (built-in Read/Write/Glob/Grep)",
        "Code execution": f"{yn(has_query)} (built-in Bash tool)",
        "Structured output": f"{yn(has_options)} (output_format)",
        "Multi-agent": f"{yn(has_subagent)} (subagents via TaskStartedMessage)",
        "Guardrails": f"{yn(has_can_use)} (CanUseTool + hooks)",
        "Hooks / lifecycle": f"{yn(has_hooks_pre and has_hooks_stop)} (PreToolUse / Stop / SubagentStart)",
        "Tracing dashboard": f"{yn(False)} (not in SDK)",
        "Permission system": f"{yn(has_perm)} (PermissionMode)",
        "Plan mode": f"{yn(has_perm)} (permission_mode=plan)",
        "TodoWrite / tasks": f"{yn(has_query)} (leaks through, undocumented)",
        "MCP support": f"{yn(has_mcp)} (McpServerConfig)",
        "Streaming": f"{yn(has_stream)} (StreamEvent async iter)",
        "Session resume": f"{yn(has_session)} (list_sessions / get_session_info)",
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
