# Quick Reference

## Environment Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install anthropic pydantic pydantic-ai
export ANTHROPIC_API_KEY="your-key-here"
```

## Basic Claude Request

```python
import anthropic

client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude!"}]
)
print(message.content[0].text)
```

## Basic Pydantic AI Agent

```python
from pydantic_ai import Agent

agent = Agent(
    'anthropic:claude-sonnet-4-20250514',
    system_prompt='Be concise and helpful.'
)

result = agent.run_sync('What is 2 + 2?')
print(result.data)
```
