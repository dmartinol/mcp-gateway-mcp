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
| `ui://catalog/mcp-app.html` | Interactive tool catalog rendered as a sandboxed iframe by MCP Apps-compatible hosts (Cursor, Claude Desktop, VS Code Copilot, …) |

See [sample-prompts.md](sample-prompts.md) for example queries for each tool.

## Requirements

- Go 1.22+
- Kubeconfig pointing to a cluster running `mcp-gateway` CRDs
- (Optional) Port-forward to the broker for live status

## Configuration

| Flag | Env var | Default | Notes |
|---|---|---|---|
| `--kubeconfig` | `KUBECONFIG` | `~/.kube/config` | Falls back to in-cluster config |
| `--namespace` | `MCP_ADMIN_NAMESPACE` | `mcp-system` | Namespace where `MCPServerRegistration` / `MCPVirtualServer` CRDs live (use `mcp-servers` on the hosted cluster) |
| `--broker-url` | `MCP_BROKER_URL` | `http://localhost:8080` | Broker `/status` endpoint |
| `--transport` | `MCP_ADMIN_TRANSPORT` | `stdio` | `stdio` or `sse` |
| `--sse-addr` | `MCP_ADMIN_SSE_ADDR` | `:8899` | SSE bind address |

## Quick start (hosted cluster)

```bash
# Forward the broker port
kubectl port-forward svc/mcp-gateway -n mcp-gateway-system 8080:8080 &

# Build
make build

# Run (stdio — for Claude Desktop / Cursor)
./bin/mcp-gateway-admin --namespace mcp-servers --broker-url http://localhost:8080

# Run (SSE — for MCP Inspector)
make run-sse
```

## Claude Desktop config

```json
{
  "mcpServers": {
    "mcp-admin": {
      "command": "/path/to/mcp-gateway-mcp/bin/mcp-gateway-admin",
      "args": ["--namespace", "mcp-servers", "--broker-url", "http://localhost:8080"]
    }
  }
}
```

## Cursor config (`~/.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "gateway-admin": {
      "command": "/path/to/mcp-gateway-mcp/bin/mcp-gateway-admin",
      "args": ["--namespace", "mcp-servers", "--broker-url", "http://localhost:8080"]
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
| Registered servers | `assisted-service-mcp` (20 tools, prefix `assisted_`), `insights-mcp` (15 tools, prefix `insights_`) |

## Build

```bash
make build   # outputs bin/mcp-gateway-admin
go vet ./...
```
