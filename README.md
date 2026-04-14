# Python Files Summary

A catalog of all Python files in this repository (112 total, excluding `.venv`).

## Phase A: Teaching Exercises

### Core Teaching Sessions (`phase-a/exercises/agents/`)

| # | File | Description |
|---|------|-------------|
| 1 | `s01_agent_loop.py` | Basic LLM loop: feed tool results back until model stops |
| 2 | `s02_tool_use.py` | Tool dispatch system routing tool calls to implementations |
| 3 | `s03_todo_write.py` | Progress tracking with TodoManager and nag reminders |
| 4 | `s04_subagent.py` | Child agents with isolated context |
| 5 | `s05_skill_loading.py` | Two-layer skill injection (metadata + on-demand bodies) |
| 6 | `s06_context_compact.py` | Three-layer compression pipeline for memory management |
| 7 | `s07_task_system.py` | Persistent tasks with JSON files and dependency graphs |
| 8 | `s08_background_tasks.py` | Parallel command execution with result queue |
| 9 | `s09_agent_teams.py` | Multiple teammates with file-based JSONL inboxes |
| 10 | `s10_team_protocols.py` | Shutdown and approval FSMs with correlation IDs |
| 11 | `s11_autonomous_agents.py` | Idle cycle with task polling and auto-claiming |
| 12 | `s12_worktree_task_isolation.py` | Directory-level isolation for parallel tasks |
| 13 | `s_full.py` | Capstone reference combining all mechanisms |

### Student Exercises (`phase-a/exercises/exercises/`)

Mirrored exercise files (ex01–ex12) corresponding to each core teaching session above.

## Phase A: Quickstarts

### Agents Framework (`phase-a/quickstarts/agents/`)

- `agent.py` — Claude API agent with MCP integration
- 6 tool modules: `base.py`, `code_execution.py`, `file_tools.py`, `mcp_tool.py`, `web_search.py`, `calculator_mcp.py`
- 3 utility modules: `connections.py`, `tool_util.py`, `history_util.py`

### Browser Automation (`phase-a/quickstarts/browser-use-demo/`)

17 files implementing browser control with Claude.

### Computer Automation (`phase-a/quickstarts/computer-use-demo/`)

13 files for desktop automation via Claude.

### Autonomous Coding (`phase-a/quickstarts/autonomous-coding/`)

7 files for autonomous code generation.

## Phase C: SDK Comparisons

### Claude Agent SDK (`phase-c/claude-agent-sdk/`)

| File | Description |
|------|-------------|
| `ex01_sdk_basics.py` | Built-in query() capabilities |
| `ex02_todo_and_tasks.py` | Task management support |
| `ex02b_safe_write.py` | Sandboxed file writing with path validation |
| `ex03_subagents.py` | Subagent spawning |
| `ex04_plan_mode.py` | Plan-then-execute workflow |
| `ex05_custom_tools_and_hooks.py` | Custom tools and hooks |
| `ex06_comparison_table.py` | Empirical feature matrix |

### Claude Code CLI (`phase-c/claude-code-cli/`)

6 files (`ex01`–`ex06`) — Parallel CLI exploration with comparison table.

### GLM / Zhipu (`phase-c/glm/`)

| File | Description |
|------|-------------|
| `ex01_glm_basics.py` | Chat completion baseline |
| `ex02_build_agent_loop.py` | DIY agent loop implementation |

### OpenAI Agents SDK (`phase-c/openai-agents-sdk/`)

4 files (`ex01`–`ex04`) — Three-way comparison with handoffs, guardrails, and hooks.

### Shared Benchmark (`phase-c/`)

- `coding_task.py` — Todo CLI app benchmark used across all SDKs.

## Key Patterns

- **Learning progression**: From basic agent loops → complex multi-agent orchestration
- **Comparison focus**: Claude Agent SDK vs Claude Code CLI vs OpenAI Agents SDK vs GLM
- **Core concepts**: Agent loops, tools, subagents, teams, tasks, compression, protocols, skills
- **Hands-on demos**: Browser automation and computer-use implementations
