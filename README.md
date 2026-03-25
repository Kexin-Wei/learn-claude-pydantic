# Claude Agent SDK & Pydantic AI Learning Path

Python 3.11+ | async/await | type hints | `uv sync` to install

## The Path

```
Step 0  learn-claude-code          Agent loops, tools, subagents, multi-agent
   ↓
Step 1  Pydantic + Structured Out  Type-safe validated responses from Claude
   ↓
Step 2  Pydantic AI Framework      Agents with DI, typed tools, test harness
   ↓
Step 3  MCP                        Connect agents to external services
   ↓
Step 4  Capstone                   Build a real project combining it all
```

## Progress

- [ ] **Step 0** — [learn-claude-code](learn-claude-code/) (submodule, prerequisite)
  - [x] s01 — The Agent Loop: one tool + one `while True` = an agent
    - [x] Read: [docs/en/s01](learn-claude-code/docs/en/s01-the-agent-loop.md)
    - [ ] **Code: [`ex01_agent_loop.py`](learn-claude-code/exercises/ex01_agent_loop.py)** — implement `agent_loop()` from scratch
  - [x] s02 — Tool Use: dispatch map, the loop never changes
    - [ ] Read: [docs/en/s02](learn-claude-code/docs/en/s02-tool-use.md)
    - [ ] **Code: [`ex02_tool_use.py`](learn-claude-code/exercises/ex02_tool_use.py)** — implement file tools, dispatch map, JSON schemas
  - [ ] s03 — TodoWrite: planning with a nag reminder
    - [ ] Read: [docs/en/s03](learn-claude-code/docs/en/s03-todo-write.md)
    - [ ] **Code: [`ex03_todo_write.py`](learn-claude-code/exercises/ex03_todo_write.py)** — `TodoManager` class + nag reminder injection
  - [ ] s04 — Subagents: fresh context, summary-only return
    - [ ] Read: [docs/en/s04](learn-claude-code/docs/en/s04-subagent.md)
    - [ ] **Code: [`ex04_subagent.py`](learn-claude-code/exercises/ex04_subagent.py)** — `run_subagent()` with isolated context + parent dispatch
  - [ ] s05 — Skills: on-demand knowledge loading
    - [ ] Read: [docs/en/s05](learn-claude-code/docs/en/s05-skill-loading.md)
    - [ ] **Code: [`ex05_skill_loading.py`](learn-claude-code/exercises/ex05_skill_loading.py)** — `SkillLoader` with frontmatter parsing + two-layer injection
  - [ ] s06 — Context Compact: three-layer compression
    - [ ] Read: [docs/en/s06](learn-claude-code/docs/en/s06-context-compact.md)
    - [ ] **Code: [`ex06_context_compact.py`](learn-claude-code/exercises/ex06_context_compact.py)** — `micro_compact`, `auto_compact`, three-layer loop
  - [ ] s07 — Task System: file-based task graph with dependencies
    - [ ] Read: [docs/en/s07](learn-claude-code/docs/en/s07-task-system.md)
    - [ ] **Code: [`ex07_task_system.py`](learn-claude-code/exercises/ex07_task_system.py)** — `TaskManager` with CRUD, dependency graph, JSON persistence
  - [ ] s08 — Background Tasks: daemon threads for slow ops
    - [ ] Read: [docs/en/s08](learn-claude-code/docs/en/s08-background-tasks.md)
    - [ ] **Code: [`ex08_background_tasks.py`](learn-claude-code/exercises/ex08_background_tasks.py)** — `BackgroundManager` with threads, notification queue, drain loop
  - [ ] s09 — Agent Teams: persistent teammates via JSONL mailboxes
    - [ ] Read: [docs/en/s09](learn-claude-code/docs/en/s09-agent-teams.md)
    - [ ] **Code: [`ex09_agent_teams.py`](learn-claude-code/exercises/ex09_agent_teams.py)** — `MessageBus` + `TeammateManager` with threaded agent loops
  - [ ] s10 — Team Protocols: shutdown + plan approval FSMs
    - [ ] Read: [docs/en/s10](learn-claude-code/docs/en/s10-team-protocols.md)
    - [ ] **Code: [`ex10_team_protocols.py`](learn-claude-code/exercises/ex10_team_protocols.py)** — request-response correlation, shutdown/plan FSMs
  - [ ] s11 — Autonomous Agents: idle cycle + task board auto-claim
    - [ ] Read: [docs/en/s11](learn-claude-code/docs/en/s11-autonomous-agents.md)
    - [ ] **Code: [`ex11_autonomous_agents.py`](learn-claude-code/exercises/ex11_autonomous_agents.py)** — idle polling, `scan_unclaimed_tasks`, `claim_task`, identity re-injection
  - [ ] s12 — Worktree Isolation: each agent in its own git worktree
    - [ ] Read: [docs/en/s12](learn-claude-code/docs/en/s12-worktree-task-isolation.md)
    - [ ] **Code: [`ex12_worktree_isolation.py`](learn-claude-code/exercises/ex12_worktree_isolation.py)** — `WorktreeManager` + `EventBus`, task-worktree binding lifecycle
- [ ] **Step 1** — [Pydantic + Structured Outputs](docs/modules/01-pydantic-structured-outputs.md) ~3-4h
  - BaseModel, validators, `model_json_schema()`, enforce typed Claude responses
- [ ] **Step 2** — [Pydantic AI Framework](docs/modules/02-pydantic-ai.md) ~5-6h
  - `Agent`, `result_type`, `@agent.tool`, `RunContext`, `TestModel`
- [ ] **Step 3** — [MCP](docs/modules/03-mcp.md) ~3-4h
  - Connect to MCP servers, build your own, integrate with Agent SDK & Pydantic AI
- [ ] **Step 4** — [Capstone Project](docs/modules/04-capstone.md) ~4-6h
  - Code reviewer, research assistant, data pipeline, or CLI task manager

> [Quick Reference](docs/QUICKSTART.md) — setup + code snippets for each step

## Two SDKs, One Path

| SDK | What it gives you |
|-----|-------------------|
| `claude-agent-sdk` | Claude Code-style automation (Read, Edit, Bash, etc.) |
| `pydantic-ai` | Type-safe agents with dependency injection and structured results |

Both support MCP. The capstone combines them.

## License

MIT
