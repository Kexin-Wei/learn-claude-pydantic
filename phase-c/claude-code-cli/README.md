# Track C1 (CLI) — Claude Code CLI

Test the same 4 questions as the [SDK version](../claude-agent-sdk/), but using `claude -p` (non-interactive CLI).

## 4 Questions

1. **TodoWrite / task management?** — Yes. First-class CLI tool, always available.
2. **Auto-spawn subagents?** — Yes. Built-in general-purpose agent + `--agents` + `.claude/agents/`.
3. **Planner mode?** — Partial. `--permission-mode plan` blocks all tools. No plan-then-execute.
4. **CLI vs SDK?** — CLI has TodoWrite, auto memory, agent teams, worktree. SDK has programmatic hooks, `@tool`, `can_use_tool`.

## Setup

```bash
# Ensure you're logged in
claude auth status

# Copy and edit .env (model selection)
cp .env.example .env
```

## Run

```bash
# Run one exercise
uv run python phase-c/claude-code-cli/ex01_cli_basics.py

# Run all
for f in phase-c/claude-code-cli/ex0*.py; do uv run python "$f"; done
```

## Exercises

| # | File | Tests | API Cost |
|---|------|-------|----------|
| 1 | `ex01_cli_basics.py` | `claude -p`, tool inventory | ~$0.09 |
| 2 | `ex02_todo_and_tasks.py` | TodoWrite in multi-step tasks | ~$0.50 |
| 3 | `ex03_subagents.py` | Auto-spawn, `--agents` flag | ~$0.30 |
| 4 | `ex04_plan_mode.py` | `--permission-mode plan`, `--effort` | ~$0.20 |
| 5 | `ex05_cli_features.py` | `--tools`, `--json-schema`, `--system-prompt` | ~$0.20 |
| 6 | `ex06_comparison_table.py` | All probes + CLI vs SDK comparison table | ~$1.00 |

## Key CLI Flags Used

| Flag | What it does |
|------|-------------|
| `-p` | Non-interactive (print and exit) |
| `--output-format stream-json` | Structured JSON output per message |
| `--model opus` | Model selection (alias or full ID) |
| `--max-turns N` | Limit agent loop iterations |
| `--dangerously-skip-permissions` | Bypass permission prompts |
| `--permission-mode plan` | No tool execution |
| `--effort low\|high\|max` | Thinking depth |
| `--agents '{...}'` | Custom agent definitions as JSON |
| `--tools "Read,Glob"` | Restrict available tools |
| `--json-schema '{...}'` | Structured output with schema |
| `--system-prompt "..."` | Override system prompt |
| `--allowed-tools "..."` | Pre-approve specific tools |
