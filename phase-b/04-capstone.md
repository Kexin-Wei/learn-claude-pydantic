# Module 4: Capstone Project

**Goal:** Build a complete project combining Agent SDK, Pydantic AI, structured outputs, and MCP

Pick one (or propose your own):

## Project Options

### 1. Code Review Agent
An Agent SDK agent that reviews code via MCP (GitHub server), returns structured feedback (severity, category, suggestion) as validated Pydantic models.

### 2. Research Assistant
A Pydantic AI agent that searches the web via MCP, extracts structured data from results, and produces a typed summary report with sources and confidence scores.

### 3. Data Pipeline Agent
An agent that connects to databases/APIs via MCP, extracts data, validates it through Pydantic models, and outputs clean structured datasets.

### 4. CLI Task Manager
An Agent SDK agent with MCP filesystem access that manages a local task system — bridging what you built in learn-claude-code s07 with Pydantic AI's typed tools and structured results.

## Requirements (any project)

- [ ] Uses either Agent SDK `query()` or Pydantic AI `Agent` (or both)
- [ ] At least 2 custom tools (via `@agent.tool`, `@tool` decorator, or MCP)
- [ ] Structured output validated by Pydantic models
- [ ] At least 1 MCP server integration
- [ ] Tests (using `TestModel` for Pydantic AI, or mocked `query()` for Agent SDK)

## Practice

`exercises/04_capstone/`
