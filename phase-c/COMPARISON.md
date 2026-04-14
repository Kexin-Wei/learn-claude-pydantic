# Phase C — SDK & Provider Comparison

## Built-in Tools

| Tool | Claude Agent SDK | Claude CLI | OpenAI Agents SDK | GLM (Zhipu) |
|------|-----------------|------------|-------------------|-------------|
| Web search | WebSearch | WebSearch | WebSearchTool | No |
| File search | Grep/Glob | Grep/Glob | FileSearchTool | No |
| Code execution | Bash | Bash | CodeInterpreterTool | No |
| Shell | Bash | Bash | ShellTool | No |
| File read | Read | Read | No (DIY) | No |
| File write | Write | Write | No (DIY) | No |
| File edit | Edit | Edit | ApplyPatchTool | No |
| Image generation | No | No | ImageGenerationTool | No |
| MCP | mcp_servers | MCP config | HostedMCPTool | No |
| Tool search | ToolSearch | ToolSearch | ToolSearchTool | No |
| **TodoWrite** | **No (leaks)** | **Yes** | **No** | **No** |

## Agent Features

| Feature | Claude Agent SDK | Claude CLI | OpenAI Agents SDK | GLM (Zhipu) |
|---------|-----------------|------------|-------------------|-------------|
| Agent loop | query() / ClaudeSDKClient | Interactive + `-p` | Runner.run() | No (DIY) |
| Custom tools | @tool + MCP server | MCP servers | @function_tool | function calling |
| Structured output | output_format (JSON schema) | --json-schema | output_type (Pydantic) | No |
| Multi-agent | Subagents (AgentDefinition) | Subagents + Agent teams | Handoffs | No (DIY) |
| Agent nesting | No (1 level) | No (1 level) | Handoff chains | N/A |
| Guardrails | Hooks (Pre/PostToolUse) | Hooks (shell/http) | Input/OutputGuardrail | No |
| Hooks | PreToolUse, PostToolUse, Stop | Shell/http/prompt/agent | RunHooks, AgentHooks | No |
| Permission system | 5 modes + can_use_tool | 6 modes (incl. auto) | needs_approval per tool | No |
| Tracing / dashboard | No dashboard | No dashboard | Yes (OpenAI dashboard) | No |
| Plan mode | No-tools permission | /plan toggle | No | No |
| Session resume | resume param | --continue / --resume | previous_response_id | No |
| Streaming | AsyncIterator | --output-format stream | Runner.run_streamed | SSE chunks |
| Context management | Auto compaction | Auto compaction | Manual | Manual |
| Auto memory | No (CLI-only) | Yes | No | No |
| Skills (on-demand) | Yes (via settingSources) | Yes | No | No |
| CLAUDE.md / rules | Yes (via settingSources) | Yes | No | No |

## Coding Task Test Results

> Task: "Build a multi-file Python expense tracker CLI (models.py, storage.py, cli.py, test_tracker.py).
> Commands: add, list (with filters), summary (category totals), delete. JSON persistence. Unit tests."
>
> Results saved to `phase-c/results/<target>/` — run `uv run python phase-c/coding_task.py <target>`.

| Metric | Claude Agent SDK | Claude CLI | OpenAI Agents SDK | GLM (Zhipu) |
|--------|-----------------|------------|-------------------|-------------|
| Completed? | Yes (async cleanup error) | Yes | Files only (import bug) | Yes |
| Turns used | 21 | 22 | 12 | 17 |
| Expected files (4) | 4/4 | 4/4 | 4/4 | 4/4 |
| Code runs? | Yes | Yes | No | Yes |
| Cost | $0.77 | $0.62 | N/A (check dashboard) | $1.55 |
| Duration | 169s | 134s | 86s | 476s |
| Used TodoWrite? | Yes | Yes | No (not available) | Yes |
| Used subagents? | Yes | Yes | No (not available) | Yes |

## Summary

_To be filled after running all exercises._
