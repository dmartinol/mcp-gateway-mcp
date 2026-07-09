# mcp-gateway-mcp

MCP server that exposes management tools for the [mcp-gateway](../mcp-gateway) project.
Targets platform engineers who need to inspect and operate a running gateway without kubectl.

## What it does

Seven MCP tools and one MCP resource:

| Tool | Description |
|---|---|
| `list_registrations` | List MCPServerRegistration CRs |
| `get_registration` | Get a single registration with conditions |
| `update_registration_state` | Enable or disable a registration |
| `list_virtual_servers` | List MCPVirtualServer CRs |
| `get_virtual_server` | Get a single virtual server |
| `get_gateway_status` | Call the broker `/status` endpoint |
| `render_tool_catalog` | Return JSON catalog data; MCP Apps-aware hosts render the interactive UI |

| Resource | Description |
|---|---|
| `ui://catalog/mcp-app.html` | MCP App UI (MIME `text/html;profile=mcp-app`): interactive catalog rendered in a sandboxed iframe by MCP Apps-compatible hosts (Claude, Cursor, VS Code Copilot, etc.) |

## Project layout

```
main.go                     # entry point: flags, k8s client, MCP server wiring
internal/admin/
  server.go                 # Server struct, RegisterTools
  registrations.go          # list_registrations, get_registration, update_registration_state
  virtualservers.go         # list_virtual_servers, get_virtual_server
  gateway_status.go         # get_gateway_status
  tool_catalog.go           # render_tool_catalog (self-contained HTML)
Makefile
```

## Dependencies

- `github.com/Kuadrant/mcp-gateway` — CRD types (`api/v1alpha1`), referenced via `replace` directive in `go.mod` pointing to `../mcp-gateway`
- `github.com/mark3labs/mcp-go` — MCP server and tool primitives
- `sigs.k8s.io/controller-runtime` — Kubernetes client

## Configuration

| Flag | Env var | Default | Notes |
|---|---|---|---|
| `--kubeconfig` | `KUBECONFIG` | `~/.kube/config` | Falls back to in-cluster config |
| `--namespace` | `MCP_ADMIN_NAMESPACE` | `mcp-system` | Namespace where CRDs live — use `mcp-servers` on the hosted cluster |
| `--broker-url` | `MCP_BROKER_URL` | `http://localhost:8080` | Broker status endpoint |
| `--transport` | `MCP_ADMIN_TRANSPORT` | `stdio` | `stdio` or `sse` |
| `--sse-addr` | `MCP_ADMIN_SSE_ADDR` | `:8899` | SSE bind address |

## Running locally against the hosted cluster

```bash
# Forward the broker port
kubectl port-forward svc/mcp-gateway -n mcp-gateway-system 8080:8080 &

# Build and run (stdio for Claude Desktop)
make build
./bin/mcp-gateway-admin --namespace mcp-servers --broker-url http://localhost:8080

# Or SSE for MCP Inspector
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

## Hosted cluster details

- Gateway namespace: `gateway-system`
- Gateway public URL: `https://mcp.apps.hosted-services.ai5.appeng.rhecoeng.com`
- Broker service: `svc/mcp-gateway` in `mcp-gateway-system` (ClusterIP, port 8080)
- CRD namespace: `mcp-servers`
- Registered servers: `assisted-service-mcp` (prefix `assisted_`, 20 tools), `insights-mcp` (prefix `insights_`, 15 tools)

## Code conventions

- Match the style of `../mcp-gateway`: terse lowercase comments, idiomatic Go, no emojis
- All tool handlers on `*Server` — no package-level state
- Return JSON via `mcp.NewToolResultText(jsonString)` for text tools
- `mcp.NewToolResultError(msg)` for errors — never return a Go error from a handler
- Logger injected on `Server`, never package-level slog
- MCP App UI resources use MIME `text/html;profile=mcp-app` and URI scheme `ui://`
- Tool `_meta.ui.resourceUri` is set via `tool.Meta.AdditionalFields` after `mcp.NewTool()`
- UI HTML must use DOM methods (`textContent`, `createElement`) — no `innerHTML` with data
- MCP Apps protocol: app sends `ui/initialize`, receives `ui/notifications/tool-result` with tool JSON, can call back via `tools/call`

## Build

```bash
make build       # outputs bin/mcp-gateway-admin
go vet ./...
```
