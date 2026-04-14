# Module 3: MCP (Model Context Protocol)

**Goal:** Connect agents to external tools and data sources via MCP

> learn-claude-code introduced MCP conceptually but left runtime details out of scope. This module covers the practical side: connecting to servers, building your own, and integrating with both the Agent SDK and Pydantic AI.

## Learning Checklist

### MCP Fundamentals

- [ ] Understand the MCP architecture (client <-> server, transports, capabilities)
- [ ] Install and run an existing MCP server (e.g., filesystem, GitHub)
- [ ] Connect via Agent SDK (`mcp_servers` in `ClaudeAgentOptions`)
- [ ] Connect via Pydantic AI (`MCPServerStdio`)

### Building MCP Servers

- [ ] Create a custom MCP server with `mcp` Python SDK
- [ ] Expose tools, resources, and prompts
- [ ] Test your server with `mcp dev` inspector

### Integration

- [ ] Use MCP tools alongside native tools in the same agent
- [ ] Handle MCP server lifecycle (startup, shutdown, error recovery)
- [ ] Compare Agent SDK vs Pydantic AI approaches to MCP

## Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Pydantic AI MCP Support](https://ai.pydantic.dev/mcp/)
- [Claude Agent SDK MCP Docs](https://docs.anthropic.com/en/docs/agents-and-tools/claude-agent-sdk/mcp)

## Practice

`exercises/03_mcp/`
