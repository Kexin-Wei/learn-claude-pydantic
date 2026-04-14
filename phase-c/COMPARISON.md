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

> Task: "Create a Python CLI todo app with add, list, complete, and delete commands.
> Use a JSON file for storage. Include error handling."

| Metric | Claude Agent SDK | Claude CLI | OpenAI Agents SDK | GLM (Zhipu) |
|--------|-----------------|------------|-------------------|-------------|
| Completed? | | | | |
| Turns used | | | | |
| Files created | | | | |
| Code runs? | | | | |
| Cost | | | | |
| Duration | | | | |
| Used TodoWrite? | | | | |
| Used subagents? | | | | |

_Run the coding task exercises to fill in results._

## Summary

_To be filled after running all exercises._
