# mcp-gateway-mcp

Admin MCP server for the [mcp-gateway](../mcp-gateway) platform. Exposes Kubernetes CRD state and live broker status as MCP tools and a browser-renderable UI resource — no `kubectl` required.

Target audience: platform engineers operating a running gateway.

## Tools

| Tool | Description |
|---|---|
| `list_registrations` | List all `MCPServerRegistration` CRs |
| `get_registration` | Get a single registration with status conditions |
| `update_registration_state` | Enable or disable a registration |
| `list_virtual_servers` | List all `MCPVirtualServer` CRs |
| `get_virtual_server` | Get a single virtual server |
| `get_gateway_status` | Call the broker `/status` endpoint |
| `render_tool_catalog` | Return live catalog data; MCP Apps hosts render an interactive UI |

## Resource

| URI | Description |
|---|---|
| `ui://mcp-gateway-catalog` | Interactive tool catalog rendered as a sandboxed iframe by MCP Apps-compatible hosts (Claude, Cursor, VS Code Copilot, …) |

See [sample-prompts.md](sample-prompts.md) for example queries for each tool.

## Requirements

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) for dependency management
- Kubeconfig pointing to a cluster running `mcp-gateway` CRDs
- (Optional) Port-forward to the broker for live status

## Configuration

| Flag | Env var | Default | Notes |
|---|---|---|---|
| `--kubeconfig` | `KUBECONFIG` | `~/.kube/config` | Falls back to in-cluster config |
| `--namespace` | `MCP_ADMIN_NAMESPACE` | `mcp-servers` | Namespace where `MCPServerRegistration` / `MCPVirtualServer` CRDs live |
| `--broker-url` | `MCP_BROKER_URL` | `http://localhost:8080` | Broker `/status` endpoint |
| `--transport` | `MCP_ADMIN_TRANSPORT` | `stdio` | `stdio` or `http` |
| `--addr` | `MCP_ADMIN_ADDR` | `:8899` | HTTP bind address (used when `--transport http`) |

## Quick start (hosted cluster)

```bash
# Forward the broker port
kubectl port-forward svc/mcp-gateway -n mcp-gateway-system 8080:8080 &

# Install dependencies
uv sync

# Run (stdio — for Claude Desktop / Cursor)
uv run server.py --namespace mcp-servers --broker-url http://localhost:8080

# Run (HTTP — for MCP Inspector)
uv run server.py --transport http --namespace mcp-servers --broker-url http://localhost:8080
```

## Claude Desktop config

```json
{
  "mcpServers": {
    "mcp-admin": {
      "command": "uv",
      "args": ["run", "/path/to/mcp-gateway-mcp/server.py",
               "--namespace", "mcp-servers",
               "--broker-url", "http://localhost:8080"]
    }
  }
}
```

## Cursor config (`~/.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "gateway-admin": {
      "command": "uv",
      "args": ["run", "/path/to/mcp-gateway-mcp/server.py",
               "--namespace", "mcp-servers",
               "--broker-url", "http://localhost:8080"]
    }
  }
}
```

## Hosted cluster details

| Item | Value |
|---|---|
| Gateway public URL | `https://mcp.apps.hosted-services.ai5.appeng.rhecoeng.com` |
| CRD namespace | `mcp-servers` |
| Broker service | `svc/mcp-gateway` in `mcp-gateway-system` (port 8080) |
| Registered servers | `assisted-service-mcp` (24 tools, prefix `assisted_`), `insights-mcp` (16 tools, prefix `insights_`) |
