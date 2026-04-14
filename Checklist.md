# Claude Agent SDK & Pydantic AI Learning Path

Python 3.11+ | async/await | type hints | `uv sync` to install

## Submodules

| Submodule | Path | Purpose |
|-----------|------|---------|
| [quickstarts](phase-a/quickstarts/) | `phase-a/quickstarts/` | Official Anthropic API examples and cookbook |
| [exercises](phase-a/exercises/) | `phase-a/exercises/` | Reverse-engineer Claude Code internals (agent loop → multi-agent) |
| [claude-code](phase-a/claude-code/) | `phase-a/claude-code/` | Claude Code source — read-only reference for Steps 0.5–0.6 |

## The Path

```
Phase A — Understand how Claude Code works
──────────────────────────────────────────────────────────────────────────
Step -1   claude-quickstarts         Official Anthropic API examples
   ↓
Step 0    learn-claude-code          Agent loops, tools, subagents, multi-agent
   ↓
Step 0.5  Production Patterns        Permission, memory, error recovery, prompt pipeline
   ↓
Step 0.6  Extensibility              Hooks, plugins, cron scheduling

Phase B — Build your own agents
──────────────────────────────────────────────────────────────────────────
Step 1    Pydantic + Structured Out  Type-safe validated responses from Claude
   ↓
Step 2    Pydantic AI Framework      Agents with DI, typed tools, test harness
   ↓
Step 3    MCP                        Connect agents to external services
   ↓
Step 4    Capstone                   Build a real project combining it all

Phase C — SDK & Provider Comparison  (parallel with A/B)
──────────────────────────────────────────────────────────────────────────
Track C1  Claude Agent SDK           Todo, planner, subagents — what's built-in vs DIY?
Track C2  OpenAI Agents SDK          Agent primitives, tool use, orchestration
Track C3  GLM (Zhipu AI)             Chinese LLM agent capabilities
```

## Progress

### Phase A — Understand Claude Code

- [ ] **Step -1** — [quickstarts](phase-a/quickstarts/) (submodule)
  - [ ] Study official Anthropic API examples and cookbook patterns
- [ ] **Step 0** — [exercises](phase-a/exercises/) (submodule)
  - [x] s01 — The Agent Loop: one tool + one `while True` = an agent
    - [x] Read: [docs/en/s01](phase-a/exercises/docs/en/s01-the-agent-loop.md)
    - [x] **Code: [`ex01_agent_loop.py`](phase-a/exercises/exercises/ex01_agent_loop.py)** — implement `agent_loop()` from scratch
  - [x] s02 — Tool Use: dispatch map, the loop never changes
    - [x] Read: [docs/en/s02](phase-a/exercises/docs/en/s02-tool-use.md)
    - [x] **Code: [`ex02_tool_use.py`](phase-a/exercises/exercises/ex02_tool_use.py)** — implement file tools, dispatch map, JSON schemas
  - [x] s03 — TodoWrite: planning with a nag reminder
    - [x] Read: [docs/en/s03](phase-a/exercises/docs/en/s03-todo-write.md)
    - [x] **Code: [`ex03_todo_write.py`](phase-a/exercises/exercises/ex03_todo_write.py)** — `TodoManager` class + nag reminder injection
  - [ ] s04 — Subagents: fresh context, summary-only return
    - [ ] Read: [docs/en/s04](phase-a/exercises/docs/en/s04-subagent.md)
    - [ ] **Code: [`ex04_subagent.py`](phase-a/exercises/exercises/ex04_subagent.py)** — `run_subagent()` with isolated context + parent dispatch
  - [ ] s05 — Skills: on-demand knowledge loading
    - [ ] Read: [docs/en/s05](phase-a/exercises/docs/en/s05-skill-loading.md)
    - [ ] **Code: [`ex05_skill_loading.py`](phase-a/exercises/exercises/ex05_skill_loading.py)** — `SkillLoader` with frontmatter parsing + two-layer injection
  - [ ] s06 — Context Compact: three-layer compression
    - [ ] Read: [docs/en/s06](phase-a/exercises/docs/en/s06-context-compact.md)
    - [ ] **Code: [`ex06_context_compact.py`](phase-a/exercises/exercises/ex06_context_compact.py)** — `micro_compact`, `auto_compact`, three-layer loop
  - [ ] s07 — Task System: file-based task graph with dependencies
    - [ ] Read: [docs/en/s07](phase-a/exercises/docs/en/s07-task-system.md)
    - [ ] **Code: [`ex07_task_system.py`](phase-a/exercises/exercises/ex07_task_system.py)** — `TaskManager` with CRUD, dependency graph, JSON persistence
  - [ ] s08 — Background Tasks: daemon threads for slow ops
    - [ ] Read: [docs/en/s08](phase-a/exercises/docs/en/s08-background-tasks.md)
    - [ ] **Code: [`ex08_background_tasks.py`](phase-a/exercises/exercises/ex08_background_tasks.py)** — `BackgroundManager` with threads, notification queue, drain loop
  - [ ] s09 — Agent Teams: persistent teammates via JSONL mailboxes
    - [ ] Read: [docs/en/s09](phase-a/exercises/docs/en/s09-agent-teams.md)
    - [ ] **Code: [`ex09_agent_teams.py`](phase-a/exercises/exercises/ex09_agent_teams.py)** — `MessageBus` + `TeammateManager` with threaded agent loops
  - [ ] s10 — Team Protocols: shutdown + plan approval FSMs
    - [ ] Read: [docs/en/s10](phase-a/exercises/docs/en/s10-team-protocols.md)
    - [ ] **Code: [`ex10_team_protocols.py`](phase-a/exercises/exercises/ex10_team_protocols.py)** — request-response correlation, shutdown/plan FSMs
  - [ ] s11 — Autonomous Agents: idle cycle + task board auto-claim
    - [ ] Read: [docs/en/s11](phase-a/exercises/docs/en/s11-autonomous-agents.md)
    - [ ] **Code: [`ex11_autonomous_agents.py`](phase-a/exercises/exercises/ex11_autonomous_agents.py)** — idle polling, `scan_unclaimed_tasks`, `claim_task`, identity re-injection
  - [ ] s12 — Worktree Isolation: each agent in its own git worktree
    - [ ] Read: [docs/en/s12](phase-a/exercises/docs/en/s12-worktree-task-isolation.md)
    - [ ] **Code: [`ex12_worktree_isolation.py`](phase-a/exercises/exercises/ex12_worktree_isolation.py)** — `WorktreeManager` + `EventBus`, task-worktree binding lifecycle
- [ ] **Step 0.5** — Production Patterns (study from [claude-code](phase-a/claude-code/src/) source) ~3 days
  - [ ] Permission System: `allow → deny → ask` pipeline, classifier auto-approval, interactive prompts
    - [ ] Read: [`useCanUseTool.tsx`](phase-a/claude-code/src/hooks/useCanUseTool.tsx) — the main permission pipeline
    - [ ] Read: [`toolPermission/`](phase-a/claude-code/src/hooks/toolPermission/) — handlers for interactive, coordinator, swarm modes
  - [ ] Memory System: file-based `MEMORY.md` index + topic files, 4 memory types, cross-session persistence
    - [ ] Read: [`memdir.ts`](phase-a/claude-code/src/memdir/memdir.ts) — core memory system
    - [ ] Read: [`memoryTypes.ts`](phase-a/claude-code/src/memdir/memoryTypes.ts) — the 4-type taxonomy (user, feedback, project, reference)
  - [ ] Error Recovery: retry with backoff, circuit breakers, reactive compaction on `prompt_too_long`
    - [ ] Read: [`autoCompact.ts`](phase-a/claude-code/src/services/compact/autoCompact.ts) — circuit breakers + reactive compaction
    - [ ] Read: [`api/errors.ts`](phase-a/claude-code/src/services/api/) — error categorization
  - [ ] System Prompt Pipeline: dynamically assembled from base + tools + memory + user context
    - [ ] Read: [`QueryEngine.ts`](phase-a/claude-code/src/QueryEngine.ts) (lines 286-325) — prompt assembly
- [ ] **Step 0.6** — Extensibility (study from [claude-code](phase-a/claude-code/src/) source) ~2 days
  - [ ] Hook/Plugin System: lifecycle observers that block, annotate, or extend tool execution
    - [ ] Read: [`hooks/`](phase-a/claude-code/src/hooks/) — 83 hook files covering every lifecycle event
    - [ ] Read: [`services/plugins/`](phase-a/claude-code/src/services/plugins/) — plugin loading and management
  - [ ] MCP Deep-Dive: production MCP client with OAuth, resource subscriptions, tool discovery
    - [ ] Read: [`services/mcp/`](phase-a/claude-code/src/services/mcp/) — full MCP integration
    - [ ] Read: [`tools/MCPTool/`](phase-a/claude-code/src/tools/MCPTool/) + [`McpAuthTool/`](phase-a/claude-code/src/tools/McpAuthTool/)
  - [ ] Cron Scheduler: agent-initiated scheduled tasks for proactive behavior
    - [ ] Read: [`tools/ScheduleCronTool/`](phase-a/claude-code/src/tools/ScheduleCronTool/) — cron tool
    - [ ] Read: [`hooks/useScheduledTasks.ts`](phase-a/claude-code/src/hooks/useScheduledTasks.ts) — task scheduling
### Phase B — Build Your Own Agents

- [ ] **Step 1** — [Pydantic + Structured Outputs](phase-b/01-pydantic-structured-outputs.md) ~3-4h
  - BaseModel, validators, `model_json_schema()`, enforce typed Claude responses
- [ ] **Step 2** — [Pydantic AI Framework](phase-b/02-pydantic-ai.md) ~5-6h
  - `Agent`, `result_type`, `@agent.tool`, `RunContext`, `TestModel`
- [ ] **Step 3** — [MCP](phase-b/03-mcp.md) ~3-4h
  - Connect to MCP servers, build your own, integrate with Agent SDK & Pydantic AI
- [ ] **Step 4** — [Capstone Project](phase-b/04-capstone.md) ~4-6h
  - Code reviewer, research assistant, data pipeline, or CLI task manager

### Phase C — SDK & Provider Comparison

> Goal: test whether these SDKs/providers give you Claude Code-like capabilities
> (todo manager, auto subagent spawning, planner mode, etc.) out of the box.

- [ ] **Track C1** — Claude Agent SDK
  - [ ] Does it provide TodoWrite / task management?
  - [ ] Does it auto-spawn subagents or require manual orchestration?
  - [ ] Does it have planner mode / plan-then-execute?
  - [ ] What's built-in vs what Claude Code adds on top?
- [ ] **Track C2** — OpenAI Agents SDK
  - [ ] Agent primitives: how does `Agent`, `Runner`, handoffs compare?
  - [ ] Tool use model: function calling, code interpreter, file search
  - [ ] Orchestration: guardrails, tracing, multi-agent patterns
  - [ ] Does it have built-in planning / task tracking?
- [ ] **Track C3** — GLM (Zhipu AI)
  - [ ] Agent capabilities: tool use, multi-turn, code execution
  - [ ] SDK maturity and ecosystem
  - [ ] How does it compare for Chinese-language tasks?

> [Quick Reference](docs/QUICKSTART.md) — setup + code snippets for each step

## Two SDKs, One Path

| SDK | What it gives you |
|-----|-------------------|
| `claude-agent-sdk` | Claude Code-style automation (Read, Edit, Bash, etc.) |
| `pydantic-ai` | Type-safe agents with dependency injection and structured results |

Both support MCP. The capstone combines them.

## License

MIT
