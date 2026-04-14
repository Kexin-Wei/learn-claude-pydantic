# Track C2 — OpenAI Agents SDK

Test the same questions as Track C1, but with the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) (`openai-agents`).

## Setup

```bash
# Add to .env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini   # or gpt-4o, o3, o4-mini
```

## Run

```bash
uv run python phase-c/openai-agents-sdk/ex01_sdk_basics.py
```

## Exercises

| # | File | Tests |
|---|------|-------|
| 1 | `ex01_sdk_basics.py` | Agent, Runner.run, @function_tool, WebSearchTool, output_type |
| 2 | `ex02_handoffs_and_guardrails.py` | Multi-agent handoffs, InputGuardrail |
| 3 | `ex03_hooks_and_tracing.py` | RunHooks, AgentHooks, built-in tracing |
| 4 | `ex04_comparison_table.py` | Three-way comparison table (no API calls) |

## Quick Comparison

| | Claude Agent SDK | OpenAI Agents SDK | GLM |
|---|---|---|---|
| Agent loop | `query()` / `ClaudeSDKClient` | `Runner.run()` | DIY |
| Custom tools | `@tool` + MCP server | `@function_tool` | function calling |
| Multi-agent | Subagents (AgentDefinition) | Handoffs | DIY |
| Guardrails | Hooks (PreToolUse) | InputGuardrail / OutputGuardrail | No |
| Structured output | output_format (JSON schema) | output_type (Pydantic) | No |
| Tracing | No dashboard | OpenAI dashboard | No |
| TodoWrite | CLI only | No | No |
