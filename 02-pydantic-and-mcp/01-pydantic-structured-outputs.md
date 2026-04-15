# Module 1: Pydantic + Structured Outputs

**Goal:** Use Pydantic models to get validated, typed JSON responses from Claude

> You already know the agent loop and `query()` from the Agent SDK. This module adds type safety and schema enforcement on top of that.

## Learning Checklist

### Pydantic Essentials (skim if familiar)

- [ ] Define BaseModel classes with typed fields
- [ ] Use `Field()` for validation constraints (min/max, regex, etc.)
- [ ] Implement custom validators (`@field_validator`, `@model_validator`)
- [ ] Nested models and `model_json_schema()` output

### Structured Outputs from Claude

- [ ] Use `model_json_schema()` to generate JSON schemas from Pydantic models
- [ ] Enforce structured responses via system prompts + schema constraints
- [ ] Validate Claude's output against Pydantic models and implement retry logic
- [ ] Explore the `instructor` library for automatic schema enforcement and retries

## Resources

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Claude Agent SDK Docs](https://docs.anthropic.com/en/docs/agents-and-tools/claude-agent-sdk)
- [Instructor Library](https://python.useinstructor.com/)

## Practice

`exercises/01_pydantic_structured/`
