#!/usr/bin/env python3
"""Probe GLM (ZhipuAI) features via z.ai proxy and write a row to phase-c/c01_comparison.csv.

Checks if z.ai proxy is configured (Claude SDK/CLI pointed at z.ai → GLM models).

Run: uv run python phase-c/glm/c01_feature_probe.py
"""
import csv
import importlib
import json
import shutil
from pathlib import Path

CSV_PATH = Path(__file__).parent.parent / "c01_comparison.csv"
SDK_NAME = "GLM (Zhipu)"

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


def check_zai_proxy() -> dict[str, bool]:
    """Check if z.ai proxy is configured (enables Claude SDK/CLI with GLM models)."""
    settings_path = Path(__file__).parent / ".claude" / "settings.local.json"
    has_settings = settings_path.exists()
    has_token = False
    if has_settings:
        try:
            settings = json.loads(settings_path.read_text())
            token = settings.get("env", {}).get("ANTHROPIC_AUTH_TOKEN", "")
            has_token = bool(token) and token != "your-zai-api-key-here"
        except (json.JSONDecodeError, KeyError):
            pass

    has_claude_sdk = check("claude_agent_sdk", "query")
    has_claude_cli = shutil.which("claude") is not None

    return {
        "settings_exist": has_settings,
        "token_configured": has_token,
        "claude_sdk_available": has_claude_sdk,
        "claude_cli_available": has_claude_cli,
        "proxy_ready": has_token and (has_claude_sdk or has_claude_cli),
    }


def probe() -> dict[str, str]:
    zai = check_zai_proxy()
    proxy = zai["proxy_ready"]
    has_sdk = zai["claude_sdk_available"]
    has_cli = zai["claude_cli_available"]

    def via(desc: str) -> str:
        return f"Yes (via z.ai: {desc})" if proxy else "No (z.ai proxy not configured)"

    return {
        "Agent loop": via("Claude SDK query()") if has_sdk else via("Claude CLI"),
        "Custom tools": via("Claude @tool + MCP"),
        "Web search": via("Claude WebSearch tool"),
        "File tools": via("Claude Read/Write/Glob/Grep"),
        "Code execution": via("Claude Bash tool"),
        "Structured output": via("Claude output_format"),
        "Multi-agent": via("Claude subagents"),
        "Guardrails": via("Claude hooks"),
        "Hooks / lifecycle": via("Claude PreToolUse/Stop/..."),
        "Tracing dashboard": f"{yn(False)} (not available via z.ai)",
        "Permission system": via("Claude permission modes"),
        "Plan mode": via("Claude permission_mode=plan"),
        "TodoWrite / tasks": via("Claude TodoWrite"),
        "MCP support": via("Claude MCP servers"),
        "Streaming": via("Claude stream-json"),
        "Session resume": via("Claude --resume"),
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

    zai = check_zai_proxy()
    print(f"  z.ai proxy: {'ready' if zai['proxy_ready'] else 'not configured'}")
    if not zai["proxy_ready"]:
        if not zai["settings_exist"]:
            print(f"    (no .claude/settings.local.json found)")
        elif not zai["token_configured"]:
            print(f"    (ANTHROPIC_AUTH_TOKEN not set or placeholder)")
    print()

    row = probe()
    for feat, val in row.items():
        print(f"  {feat:<22} {val}")
    upsert_csv(SDK_NAME, row)
    print(f"\nWrote to {CSV_PATH}")


if __name__ == "__main__":
    main()
