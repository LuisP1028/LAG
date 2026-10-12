# Sandcastle Host MCP Registry

This project utilizes Host-Level MCP (Model Context Protocol) servers executed via `agy`. The agents are authorized to interact with external environments according to their strict role boundaries.

## Active MCP Servers
- `google-colab`: Provision and execute remote notebook cells.
- `google-drive`: Manage and read remote files.
- `blender-mcp`: Execute 3D/rendering workflows.

## Schema Discovery
Because `agy` lazy-loads tools, do NOT guess parameters. You must read the exact JSON schema for the tool before calling it:
`!cat /Users/diesel/.gemini/antigravity-ide/mcp/<serverName>/<toolName>.json`

## Role-Based Access Boundaries
1. **Planner (`plan.md`)**: You may prescribe MCP tool calls as acceptance criteria in decision tickets.
2. **Implementer (`implementer.md`)**: You are **authorized** to execute mutating actions via `call_mcp_tool` (e.g., creating files, running remote code) to fulfill ticket requirements. You must log created resource IDs/URLs in your handoff manifest.
3. **Reviewer (`reviewer.md`)**: STRICTLY READ-ONLY. You may use read-only MCP commands to verify schema contracts against the code. You must NEVER alter remote state.
4. **Tester (`tester.md`)**: You may define verification oracles that poll remote state or verify remote execution via MCP instead of relying solely on local `pytest`.
