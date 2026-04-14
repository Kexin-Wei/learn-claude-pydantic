# Module 2: Pydantic AI Framework

**Goal:** Build agents using Pydantic AI — typed tools, dependency injection, structured results

> You've built agent loops from scratch and used the Agent SDK's `query()`. Pydantic AI gives you the same patterns (tools, system prompts, multi-turn) with type safety and less boilerplate — similar to how FastAPI wraps raw ASGI.

## Learning Checklist

### Core Concepts

- [ ] Install: `pip install pydantic-ai`
- [ ] Create a basic `Agent` with a system prompt
- [ ] Return structured results using `result_type` (Pydantic models)
- [ ] Understand `RunResult` vs `StreamedRunResult`

### Tools & Dependencies

- [ ] Define typed tool functions with `@agent.tool`
- [ ] Use `RunContext[DepsType]` for dependency injection
- [ ] Compare with raw tool dispatch (learn-claude-code s02) and Agent SDK's built-in tools

### Conversation & Context

- [ ] Multi-turn conversations with `message_history`
- [ ] Dynamic system prompts with `@agent.system_prompt`
- [ ] Model selection and fallback (`model` parameter)

### Testing

- [ ] Use `TestModel` and `FunctionModel` for unit tests
- [ ] Test tools independently from the LLM

## Resources

- [pydantic/pydantic-ai](https://github.com/pydantic/pydantic-ai)
- [Pydantic AI Docs](https://ai.pydantic.dev/)
- [daveebbelaar/pydantic-ai-tutorial](https://github.com/daveebbelaar/pydantic-ai-tutorial)

## Practice

`exercises/02_pydantic_ai/`
