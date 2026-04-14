#!/usr/bin/env python3
"""Exercise 4: Comparison Table — OpenAI Agents SDK vs Claude Agent SDK vs GLM.

Questions answered: All, synthesized.

Run: uv run python phase-c/openai-agents-sdk/ex04_comparison_table.py
"""


def main() -> None:
    print("=" * 75)
    print("TRACK C2 — THREE-WAY COMPARISON")
    print("=" * 75)

    rows = [
        ("Feature",                        "Claude Agent SDK",         "OpenAI Agents SDK",      "GLM (Zhipu)"),
        ("-" * 30,                         "-" * 22,                  "-" * 22,                "-" * 16),
        ("Agent loop",                     "Yes (auto)",              "Yes (Runner.run)",      "No (DIY)"),
        ("Built-in file tools",            "10 tools (Read/Write..)", "FileSearchTool",        "No"),
        ("Built-in shell/bash",            "Yes (Bash tool)",         "ShellTool",             "No"),
        ("Built-in web search",            "Yes (WebSearch)",         "Yes (WebSearchTool)",   "No"),
        ("Code execution",                 "Yes (Bash)",              "CodeInterpreterTool",   "No"),
        ("Custom tools",                   "@tool + MCP server",      "@function_tool",        "function calling"),
        ("Structured output",              "output_format (schema)",  "output_type (Pydantic)","No"),
        ("Multi-agent",                    "Subagents (Agent tool)",  "Handoffs",              "No (DIY)"),
        ("Agent nesting",                  "No (1 level)",            "Handoff chains",        "N/A"),
        ("Guardrails",                     "Hooks (Pre/PostToolUse)", "Input/OutputGuardrail", "No"),
        ("Hooks",                          "PreToolUse, Stop, etc.",  "RunHooks, AgentHooks",  "No"),
        ("Permission system",              "5 modes + can_use_tool",  "needs_approval on tool","No"),
        ("Tracing / dashboard",            "No dashboard",            "Yes (OpenAI dashboard)","No"),
        ("TodoWrite / task tracking",      "CLI only (not in SDK)",   "No",                   "No"),
        ("Plan mode",                      "No-tools permission",     "No",                   "No"),
        ("Session resume",                 "Yes (resume param)",      "Yes (previous_response)","No"),
        ("MCP support",                    "Yes (mcp_servers)",       "Yes (mcp_servers)",     "No"),
        ("Streaming",                      "AsyncIterator",           "Runner.run_streamed",   "SSE chunks"),
        ("Context management",             "Auto compaction",         "Manual",                "Manual"),
    ]

    for row in rows:
        print(f"  {row[0]:<30} {row[1]:<24} {row[2]:<24} {row[3]}")

    print(f"\n{'=' * 75}")
    print("SUMMARY")
    print("=" * 75)

    print("""
  Claude Agent SDK:
    Strengths — Rich built-in tools (10), file operations, permission system,
    auto context compaction, inherits Claude Code ecosystem (skills, CLAUDE.md)
    Gaps — No tracing dashboard, TodoWrite not officially in SDK

  OpenAI Agents SDK:
    Strengths — Clean handoff pattern, built-in tracing dashboard, guardrails
    as first-class concept, Pydantic output_type, CodeInterpreterTool
    Gaps — No TodoWrite, no plan mode, no permission modes

  GLM (Zhipu AI):
    Raw chat API — function calling only. No agent framework.
    Comparable to raw Anthropic SDK, not to agent SDKs.

  Common gaps (none of them have):
    • TodoWrite / task management (Claude CLI only)
    • Plan-then-execute workflow
    • Auto memory across sessions
""")


if __name__ == "__main__":
    main()
