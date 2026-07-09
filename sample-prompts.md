# Sample prompts

Example natural-language queries for each tool exposed by `mcp-gateway-admin`.

---

## `list_registrations`

> List all registered MCP servers.

> What MCP servers are registered in the mcp-servers namespace?

> Are all registrations enabled?

> Which servers are currently disabled?

---

## `get_registration`

> Show me the full details for the `assisted-service-mcp` registration.

> What is the status of `insights-mcp`? Is it ready?

> Show conditions for `assisted-service-mcp` — is there any error?

> What prefix and credential ref does `insights-mcp` use?

---

## `update_registration_state`

> Disable the `insights-mcp` registration.

> Re-enable `assisted-service-mcp`.

> Take `insights-mcp` offline without deleting it.

> Enable all registrations that are currently disabled.

---

## `list_virtual_servers`

> List all virtual MCP servers.

> How many virtual servers are configured, and how many tools does each expose?

> What virtual servers are available in mcp-servers?

---

## `get_virtual_server`

> Show me the tools exposed by the `default` virtual server.

> What prompts are configured on the `ops` virtual server?

> Give me the full spec for virtual server `assisted-ops`.

---

## `get_gateway_status`

> Is the MCP gateway healthy?

> Show me the live broker status — which upstream servers are reachable?

> How many tools does the broker see right now?

> Are there any tool name conflicts between registered servers?

> Which upstream MCP servers are currently unreachable?

---

## `render_tool_catalog`

> Show me the tool catalog.

> Open the interactive catalog of all federated tools.

> Give me a catalog of all tools grouped by server so I can browse them.

> Refresh the tool catalog.
