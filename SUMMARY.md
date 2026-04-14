# Python Files Summary - learn-claude Project

## Overview

This project provides a comprehensive exploration of agent development patterns, from basic loops to complex multi-agent systems, with practical implementations for browser and computer automation, and SDK comparisons across Claude, GLM, and OpenAI frameworks.

## Phase A: Teaching Exercises (26 files)

### Core Teaching Sessions (`phase-a/exercises/agents/`)

1. **s01_agent_loop.py** - Basic LLM loop with bash tool. Implements the core pattern: feed tool results back to model until it stops. Main function: `agent_loop()` and `run_bash()`.

2. **s02_tool_use.py** - Tool dispatch system. Expands capabilities with read_file, write_file, edit_file tools. Main classes: `TodoManager` and dispatch map `TOOL_HANDLERS`.

3. **s03_todo_write.py** - Progress tracking with TodoManager. Includes nag reminders. Main class: `TodoManager` with `update()` and `render()` methods.

4. **s04_subagent.py** - Child agents with isolated context. Main classes for creating and managing subagents.

5. **s05_skill_loading.py** - Two-layer skill injection (metadata + on-demand bodies). Main functionality for skill management.

6. **s06_context_compact.py** - Three-layer compression pipeline for memory management. Handles context compression.

7. **s07_task_system.py** - Persistent tasks with JSON files and dependency graphs. Main task management system.

8. **s08_background_tasks.py** - Parallel command execution with result queue. Main background task execution.

9. **s09_agent_teams.py** - Multiple teammates with file-based JSONL inboxes. Main team orchestration.

10. **s10_team_protocols.py** - Shutdown and approval FSMs with correlation IDs. Main protocol management.

11. **s11_autonomous_agents.py** - Idle cycle with task polling and auto-claiming. Main autonomous agent loop.

12. **s12_worktree_task_isolation.py** - Directory-level isolation for parallel tasks. Main task isolation.

13. **s_full.py** - Capstone reference combining all mechanisms. Main integration of all features.

### Student Exercises (`phase-a/exercises/exercises/`)

- **ex01_agent_loop.py** through **ex12_worktree_isolation.py** - Mirrored exercise files corresponding to each core teaching session.

### Skills Reference (`phase-a/exercises/skills/agent-builder/`)

- **minimal-agent.py** - Reference implementation of minimal agent.
- **subagent-pattern.py** - Reference for subagent pattern.
- **tool-templates.py** - Reference tool templates.
- **init_agent.py** - Script for initializing agents.

## Phase A: Quickstarts (43 files)

### Agents Framework (`phase-a/quickstarts/agents/`)

- **agent.py** - Claude API agent with MCP integration. Main agent class.
- **tools/base.py** - Base tool implementations.
- **tools/code_execution.py** - Code execution tools.
- **tools/file_tools.py** - File manipulation tools.
- **tools/mcp_tool.py** - MCP integration tools.
- **tools/web_search.py** - Web search tools.
- **tools/calculator_mcp.py** - Calculator MCP tools.
- **utils/connections.py** - Connection utilities.
- **utils/tool_util.py** - Tool utilities.
- **utils/history_util.py** - History management utilities.
- **test_message_params.py** - Message parameter tests.

### Browser Automation (`phase-a/quickstarts/browser-use-demo/`)

- **browser_use_demo/loop.py** - Sampling loop for browser automation. Main loop function.
- **browser_use_demo/tools/browser.py** - Browser interaction tools.
- **browser_use_demo/tools/base.py** - Base tool classes.
- **browser_use_demo/tools/collection.py** - Tool collection management.
- **browser_use_demo/tools/coordinate_scaling.py** - Coordinate scaling utilities.
- **browser_use_demo/message_handler.py** - Message handling utilities.
- **browser_use_demo/message_renderer.py** - Message rendering utilities.
- **browser_use_demo/streamlit.py** - Streamlit integration.
- **browser_use_demo/display_constants.py** - Display constants.
- **browser_use_demo/browser_tool_utils/browser_key_map.py** - Browser key mapping.
- **setup.py** - Setup script.
- **validate_env.py** - Environment validation.
- **tests/** - Various test files.

### Computer Automation (`phase-a/quickstarts/computer-use-demo/`)

- **computer_use_demo/tools/computer.py** - Computer interaction tools (mouse, keyboard, screen). Main classes: `ComputerTool20241022`, `ComputerTool20250124`, `ComputerTool20251124`.
- **computer_use_demo/tools/bash.py** - Bash execution tools.
- **computer_use_demo/tools/edit.py** - File editing tools.
- **computer_use_demo/tools/groups.py** - Tool grouping utilities.
- **computer_use_demo/tools/run.py** - Process running utilities.
- **computer_use_demo/streamlit.py** - Streamlit integration.
- **computer_use_demo/loop.py** - Main loop for computer automation.
- **tests/** - Various test files.
- **image/http_server.py** - HTTP server for images.

### Autonomous Coding (`phase-a/quickstarts/autonomous-coding/`)

- **agent.py** - Core agent session logic. Main functions: `run_agent_session()` and `run_autonomous_agent()`.
- **autonomous_agent_demo.py** - Main autonomous coding demo.
- **client.py** - Client creation utilities.
- **progress.py** - Progress tracking utilities.
- **prompts.py** - Prompt generation utilities.
- **security.py** - Security utilities.
- **test_security.py** - Security tests.

## Phase C: SDK Comparisons (24 files)

### Claude Agent SDK (`phase-c/claude-agent-sdk/`)

- **ex01_sdk_basics.py** - Built-in query() capabilities. Main function: `probe_default_tools()`.
- **ex02_todo_and_tasks.py** - Task management support.
- **ex02b_safe_write.py** - Sandboxed file writing with path validation.
- **ex03_subagents.py** - Subagent spawning.
- **ex04_plan_mode.py** - Plan-then-execute workflow.
- **ex05_custom_tools_and_hooks.py** - Custom tools and hooks.
- **ex06_comparison_table.py** - Empirical feature matrix.

### Claude Code CLI (`phase-c/claude-code-cli/`)

- **ex01_cli_basics.py** - CLI basics. Main function: `run_claude()`.
- **ex02_todo_and_tasks.py** - Task management with CLI.
- **ex03_subagents.py** - Subagents with CLI.
- **ex04_plan_mode.py** - Plan mode with CLI.
- **ex05_cli_features.py** - CLI features.
- **ex06_comparison_table.py** - CLI comparison table.

### GLM / Zhipu (`phase-c/glm/`)

- **ex01_glm_basics.py** - Chat completion baseline. Main functions: `probe_basic_chat()`, `probe_multi_turn()`, `probe_tool_use()`, `probe_streaming()`.
- **ex02_build_agent_loop.py** - DIY agent loop implementation.

### OpenAI Agents SDK (`phase-c/openai-agents-sdk/`)

- **ex01_sdk_basics.py** - OpenAI SDK basics.
- **ex02_handoffs_and_guardrails.py** - Handoffs and guardrails.
- **ex03_hooks_and_tracing.py** - Hooks and tracing.
- **ex04_comparison_table.py** - OpenAI comparison table.

### Shared Benchmark (`phase-c/`)

- **coding_task.py** - Todo CLI app benchmark used across all SDKs.

## Key Dependencies

1. **Anthropic SDK** - `anthropic` - For Claude API interactions
2. **ZhipuAI** - `zhipuai` - For GLM model integration
3. **HTTPX** - `httpx` - HTTP client for API calls
4. **Pydantic** - `pydantic` - Data validation
5. **Playwright** - `playwright` - Browser automation (in browser-use-demo)
6. **ImageMagick** - `wand` or `convert` - Image processing
7. **Dotenv** - `dotenv` - Environment variable management
8. **JSON** - Built-in - For data serialization
9. **AsyncIO** - Built-in - For asynchronous operations
10. **PathLib** - Built-in - For file path handling

## Main Patterns and Architectures

1. **Agent Loop Pattern** - Common pattern where agents repeatedly call tools until completion
2. **Tool Dispatch System** - Maps tool names to implementations
3. **Context Compression** - Multi-layer approach to manage conversation history
4. **Task Management** - Persistent tasks with JSON storage
5. **Multi-Agent Coordination** - Teams of agents with communication protocols
6. **Browser/Computer Automation** - Integration with system automation tools
7. **SDK Comparison Framework** - Standardized testing across different agent frameworks

## Total File Count: 93 Python Files

This project provides a comprehensive exploration of agent development patterns, from basic loops to complex multi-agent systems, with practical implementations for browser and computer automation, and SDK comparisons across Claude, GLM, and OpenAI frameworks.