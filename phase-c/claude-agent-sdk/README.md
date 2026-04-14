# Track C1 — Claude Agent SDK

Test what the [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) (`claude_agent_sdk` v0.1.50) provides out of the box.

## 4 Questions

1. **TodoWrite / task management?** — No. Not an SDK-documented feature.
2. **Auto-spawn subagents?** — Yes. First-class SDK feature with `AgentDefinition` + built-in general-purpose agent.
3. **Planner mode?** — No. `permission_mode='plan'` blocks all tools, not a plan-then-execute workflow.
4. **Built-in vs Claude Code additions?** — SDK documents 10 tools. TodoWrite, auto memory, agent teams are CLI-only.

## Setup

```bash
# From repo root
uv sync                        # install dependencies
cp .env.example .env           # add ANTHROPIC_API_KEY and CLAUDE_MODEL
```

Edit `.env`:

```env
# OAuth (default): no API key needed if you're logged in via `claude`
# API key auth: uncomment below
# ANTHROPIC_API_KEY=sk-ant-...

CLAUDE_MODEL=claude-opus-4-5-20250514
```

The SDK spawns Claude Code as a subprocess, so it inherits CLI auth. If you're logged in via OAuth (`claude auth status`), no API key is needed. All exercises read `CLAUDE_MODEL` from `.env` via `dotenv`. If unset, the SDK uses its default model.

## Run

```bash
# Run one exercise
uv run python phase-c/claude-agent-sdk/ex01_sdk_basics.py

# Run all (sequential — each calls the API)
for f in phase-c/claude-agent-sdk/ex0*.py; do uv run python "$f"; done
```

## Exercises

| # | File | Tests | API Cost |
|---|------|-------|----------|
| 1 | `ex01_sdk_basics.py` | `query()`, default tool inventory | ~$0.09 |
| 2 | `ex02_todo_and_tasks.py` | TodoWrite presence in multi-step tasks | ~$0.50 |
| 3 | `ex03_subagents.py` | `AgentDefinition`, auto-spawn, Task lifecycle | ~$0.30 |
| 4 | `ex04_plan_mode.py` | `permission_mode='plan'`, thinking, effort | ~$0.30 |
| 5 | `ex05_custom_tools_and_hooks.py` | `@tool`, structured output, `disallowed_tools` | ~$0.20 |
| 6 | `ex06_comparison_table.py` | All probes combined, prints findings table | ~$1.00 |

Start with **ex01** (cheapest, confirms SDK works). Run **ex06** last for the full summary.

## Recommended order

```
ex01 (basics) → ex02 (todos) ─┐
                ex03 (agents)  ├→ ex05 (SDK primitives) → ex06 (summary)
                ex04 (plan)   ─┘
```

## SDK-Documented Built-in Tools (10)

Read, Write, Edit, Bash, Monitor, Glob, Grep, WebSearch, WebFetch, AskUserQuestion

## CLI-Only Features (NOT in SDK)

- TodoWrite (leaks through subprocess but undocumented)
- Auto memory (`~/.claude/projects/.../memory/`)
- Agent teams (multi-instance coordination)
- EnterPlanMode / ExitPlanMode (CLI interactive features)

## Source

- [SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)
- [Claude Code features in SDK](https://code.claude.com/docs/en/agent-sdk/claude-code-features)
- [Subagents](https://code.claude.com/docs/en/agent-sdk/subagents)
- [Permissions](https://code.claude.com/docs/en/agent-sdk/permissions)
