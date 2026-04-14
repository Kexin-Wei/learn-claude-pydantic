#!/usr/bin/env python3
"""Probe OpenAI Agents SDK features and write a row to phase-c/c01_comparison.csv.

Run: uv run python phase-c/openai-agents-sdk/comparison_probe.py
"""
import csv
import importlib
from pathlib import Path

CSV_PATH = Path(__file__).parent.parent / "c01_comparison.csv"
SDK_NAME = "OpenAI Agents SDK"

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


def ag(attr: str) -> bool:
    return check("agents", attr)


def probe() -> dict[str, str]:
    has_runner = ag("Runner")
    has_func_tool = ag("function_tool")
    has_web = ag("WebSearchTool")
    has_file = ag("FileSearchTool")
    has_code = ag("CodeInterpreterTool")
    has_agent = ag("Agent")
    has_handoff = ag("handoff")
    has_input_guard = ag("InputGuardrail")
    has_output_guard = ag("OutputGuardrail")
    has_run_hooks = ag("RunHooks")
    has_agent_hooks = ag("AgentHooks")
    has_tracing = ag("set_tracing_disabled")
    has_trace_proc = ag("set_trace_processors")
    has_mcp_stdio = ag("MCPServerStdio")
    has_mcp_sse = ag("MCPServerSse")

    return {
        "Agent loop": f"{yn(has_runner)} (Runner.run)",
        "Custom tools": f"{yn(has_func_tool)} (@function_tool)",
        "Web search": f"{yn(has_web)} (WebSearchTool)",
        "File tools": f"{yn(has_file)} (FileSearchTool)",
        "Code execution": f"{yn(has_code)} (CodeInterpreterTool)",
        "Structured output": f"{yn(has_agent)} (output_type / Pydantic)",
        "Multi-agent": f"{yn(has_handoff)} (handoffs)",
        "Guardrails": f"{yn(has_input_guard and has_output_guard)} (Input/OutputGuardrail)",
        "Hooks / lifecycle": f"{yn(has_run_hooks and has_agent_hooks)} (RunHooks / AgentHooks)",
        "Tracing dashboard": f"{yn(has_tracing)} (OpenAI dashboard)",
        "Permission system": f"{yn(False)} (not in SDK)",
        "Plan mode": f"{yn(False)} (not in SDK)",
        "TodoWrite / tasks": f"{yn(False)} (not in SDK)",
        "MCP support": f"{yn(has_mcp_stdio or has_mcp_sse)} (MCPServer*)",
        "Streaming": f"{yn(has_runner)} (run_streamed)",
        "Session resume": f"{yn(has_runner)} (previous_response)",
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
