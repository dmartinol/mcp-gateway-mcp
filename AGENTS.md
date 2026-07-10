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
server.py                   # entry point: args, k8s client, FastMCP wiring
tools/
  __init__.py
  registrations.py          # list_registrations, get_registration, update_registration_state
  virtual_servers.py        # list_virtual_servers, get_virtual_server
  gateway_status.py         # get_gateway_status
  tool_catalog.py           # render_tool_catalog + ui://catalog/mcp-app.html resource
pyproject.toml              # dependencies (fastmcp, kubernetes, uvicorn)
Makefile
```

## Dependencies

- `fastmcp` — MCP server and tool/resource primitives
- `kubernetes` — Python Kubernetes client for CRD access
- `uvicorn` — ASGI server for HTTP transport
- `requests` — HTTP client for broker status calls

## Configuration

| Flag | Env var | Default | Notes |
|---|---|---|---|
| `--kubeconfig` | `KUBECONFIG` | `~/.kube/config` | Falls back to in-cluster config |
| `--namespace` | `MCP_ADMIN_NAMESPACE` | `mcp-servers` | Namespace where CRDs live |
| `--broker-url` | `MCP_BROKER_URL` | `http://localhost:8080` | Broker status endpoint |
| `--transport` | `MCP_ADMIN_TRANSPORT` | `stdio` | `stdio` or `http` |
| `--addr` | `MCP_ADMIN_ADDR` | `:8899` | HTTP bind address |

## Running locally against the hosted cluster

```bash
# Forward the broker port
kubectl port-forward svc/mcp-gateway -n mcp-gateway-system 8080:8080 &

# Install dependencies and run (stdio for Claude Desktop)
uv sync
uv run server.py --namespace mcp-servers --broker-url http://localhost:8080

# Or HTTP transport for MCP Inspector
uv run server.py --transport http --namespace mcp-servers
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

## Hosted cluster details

- Gateway namespace: `gateway-system`
- Gateway public URL: `https://mcp.apps.hosted-services.ai5.appeng.rhecoeng.com`
- Broker service: `svc/mcp-gateway` in `mcp-gateway-system` (ClusterIP, port 8080)
- CRD namespace: `mcp-servers`
- Registered servers: `assisted-service-mcp` (prefix `assisted_`, 20 tools), `insights-mcp` (prefix `insights_`, 15 tools)

## Code conventions

- All tool handlers registered via `tools/<module>.register(mcp, admin)` — no module-level state
- Return `ToolResult(content=..., structured_content=...)` from handlers
- Raise exceptions for errors — FastMCP converts them to MCP error responses
- MCP App UI resources use MIME `text/html;profile=mcp-app` and URI scheme `ui://`
- `meta={"ui": {"resourceUri": RESOURCE_URI}}` on every `ToolResult` to link tool output to the UI
- UI HTML must use DOM methods (`textContent`, `createElement`) — no `innerHTML` with untrusted data
- MCP Apps protocol: app sends `ui/initialize`, receives `ui/notifications/tool-result` with tool JSON

## UI development — PatternFly and Red Hat UX

All UI surfaces in this project (MCP App HTML, any future dashboards) must follow Red Hat's
design system. Before writing any UI code:

1. **Query the `patternfly-docs` MCP** (available in `.mcp.json`) for component APIs, usage
   guidelines, and accessibility requirements. Prefer PatternFly components over custom HTML
   whenever an equivalent exists.

2. **Consult [ux.redhat.com](https://ux.redhat.com)** for Red Hat-specific design tokens,
   brand guidelines, iconography, and patterns that extend PatternFly for Red Hat products.

3. **Key principles**:
   - Use PatternFly CSS custom properties (`--pf-*`) for colors, spacing, and typography — never
     hardcode hex values or pixel sizes that diverge from the design system.
   - Follow PatternFly's accessibility standards (WCAG 2.1 AA): semantic HTML, ARIA roles where
     needed, keyboard navigation for all interactive elements.
   - The MCP App HTML (`ui://catalog/mcp-app.html`) runs in a sandboxed iframe — load PatternFly
     from a CDN (e.g., `unpkg.com`) and keep the bundle minimal (CSS + relevant JS only).
   - Match the visual language of the Red Hat Hybrid Cloud Console where the gateway is deployed.
