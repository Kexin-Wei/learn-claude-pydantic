# Track C3 — GLM (Zhipu AI)

Compare a raw LLM API (GLM) against Claude Code's agent harness.

## TL;DR

GLM SDK = raw chat completion API. No agent loop, no built-in tools, no TodoWrite, no hooks, no subagents. You build everything yourself. This is comparable to using the raw Anthropic SDK (`client.messages.create`), not the Claude Agent SDK.

## Setup

### For Python exercises (ex01, ex02)

```bash
# Add to .env
ZHIPUAI_API_KEY=your-key-from-open.bigmodel.cn
GLM_MODEL=glm-4-flash    # or glm-5.1, glm-4.7, glm-4.5-air
```

### For Claude Code via Z.AI proxy

Z.AI provides an Anthropic-compatible API proxy so you can run Claude Code against GLM models.

1. Edit [.claude/settings.local.json](.claude/settings.local.json) — put your Z.AI API key
2. Run `claude` from this directory — it picks up local settings automatically

Model mapping (in [.claude/settings.json](.claude/settings.json)):
- `opus` → glm-5.1
- `sonnet` → glm-4.7
- `haiku` → glm-4.5-air

```bash
cd phase-c/glm
claude -p "hello, what model are you?"
```

## Exercises

### Raw GLM SDK (what the API gives you)

| # | File | What it tests |
|---|------|---------------|
| 1 | `ex01_glm_basics.py` | Chat, multi-turn, function calling, streaming |
| 2 | `ex02_build_agent_loop.py` | DIY agent loop — shows what Claude Code gives for free |

### Claude Agent SDK on GLM (via Z.AI proxy)

Runs the **same** `phase-c/claude-agent-sdk/ex01-06` exercises but routed through Z.AI so GLM handles everything. This tests: can GLM do TodoWrite? subagents? plan mode? — through the Claude Code harness.

```bash
cd phase-c/glm

# Run all SDK exercises on GLM
bash run_sdk_on_glm.sh

# Run just one
bash run_sdk_on_glm.sh ex01
```

Requires your Z.AI key in `.claude/settings.local.json`.

## GLM vs Claude Code

| Capability | GLM SDK | Claude Agent SDK |
|---|---|---|
| Chat completion | Yes | Yes (underneath) |
| Function calling | Yes (you define + execute) | Yes (10 built-in + custom) |
| Streaming | Yes | Yes |
| Agent loop | **No** (DIY) | Yes (automatic) |
| Built-in tools | **No** | 10 tools (Read, Write, Bash, ...) |
| TodoWrite | **No** | CLI only (leaks in SDK) |
| Hooks | **No** | Yes (programmatic callbacks) |
| Subagents | **No** | Yes (AgentDefinition) |
| Permissions | **No** | Yes (modes + callbacks) |
| Sessions | **No** | Yes (resume, fork) |

The gap = the harness. Phase A built that harness from scratch. The Claude Agent SDK ships it ready-made.
