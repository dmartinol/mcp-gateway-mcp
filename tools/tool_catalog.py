import json
import logging
import requests
from datetime import datetime

log = logging.getLogger(__name__)
from fastmcp import FastMCP, Context
from fastmcp.apps import UI_EXTENSION_ID, AppConfig, ResourceCSP
from fastmcp.tools import ToolResult

CATALOG_RESOURCE_URI = "ui://mcp-gateway-catalog"

CATALOG_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MCP Gateway Tool Catalog</title>
<style>
:root {
  --bg: #f8f9fa; --surface: #ffffff; --border: #dee2e6; --text: #212529;
  --muted: #6c757d; --accent: #0d6efd; --green: #198754; --red: #dc3545;
  --warn-bg: #fff3cd; --warn-border: #ffc107; --disabled-bg: #f1f3f5;
  --mono: 'SF Mono','Consolas','Menlo',monospace;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #1a1d21; --surface: #25282c; --border: #373b3e; --text: #e9ecef;
    --muted: #868e96; --accent: #4da3ff; --green: #40c97a; --red: #f06a6a;
    --warn-bg: #3a2e00; --warn-border: #997404; --disabled-bg: #2a2d30;
  }
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: system-ui,sans-serif; background: var(--bg); color: var(--text); font-size: 14px; }
header { padding: 16px 20px; border-bottom: 1px solid var(--border); background: var(--surface); display: flex; align-items: center; gap: 16px; }
header h1 { font-size: 18px; font-weight: 600; }
.meta { color: var(--muted); font-size: 12px; }
.search-box { margin-left: auto; padding: 6px 12px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg); color: var(--text); font-size: 13px; width: 220px; }
.btn { padding: 5px 12px; border: 1px solid var(--border); border-radius: 6px; background: var(--surface); color: var(--text); font-size: 12px; cursor: pointer; }
.btn:hover { background: var(--bg); }
.warn { background: var(--warn-bg); border: 1px solid var(--warn-border); padding: 10px 16px; margin: 12px 20px 0; border-radius: 6px; font-size: 13px; }
.loading { padding: 48px; text-align: center; color: var(--muted); }
.layout { display: flex; height: calc(100vh - 57px); overflow: hidden; }
.sidebar { width: 200px; border-right: 1px solid var(--border); padding: 12px; background: var(--surface); overflow-y: auto; flex-shrink: 0; }
.sidebar h3 { font-size: 11px; text-transform: uppercase; color: var(--muted); letter-spacing: .05em; margin-bottom: 10px; }
.sidebar label { display: flex; align-items: center; gap: 8px; padding: 4px 0; cursor: pointer; font-size: 13px; }
.main { flex: 1; overflow-y: auto; padding: 16px 20px; }
.server-card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; margin-bottom: 16px; overflow: hidden; }
.server-card.disabled { background: var(--disabled-bg); opacity: .75; }
.server-header { padding: 12px 16px; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 10px; }
.server-name { font-weight: 600; font-size: 15px; }
.server-prefix { font-family: var(--mono); font-size: 11px; color: var(--muted); background: var(--bg); padding: 2px 6px; border-radius: 4px; }
.badge { font-size: 11px; padding: 2px 7px; border-radius: 10px; font-weight: 500; }
.badge-enabled { background: #d1fae5; color: #065f46; }
.badge-disabled { background: #f3f4f6; color: var(--muted); }
@media (prefers-color-scheme: dark) {
  .badge-enabled { background: #064e3b; color: #6ee7b7; }
  .badge-disabled { background: #374151; color: #9ca3af; }
}
.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
.dot-green { background: var(--green); }
.dot-red { background: var(--red); }
.dot-grey { background: var(--muted); }
.server-meta { color: var(--muted); font-size: 12px; margin-left: auto; }
.hint { padding: 8px 16px; font-size: 12px; color: var(--muted); border-bottom: 1px solid var(--border); font-style: italic; }
.tool-list { padding: 4px 0; }
.tool-row { display: flex; align-items: baseline; gap: 12px; padding: 7px 16px; border-bottom: 1px solid var(--border); }
.tool-row:last-child { border-bottom: none; }
.tool-row.hidden { display: none; }
.tool-name { font-family: var(--mono); font-size: 12px; color: var(--accent); min-width: 220px; }
.tool-desc { font-size: 12px; color: var(--muted); }
.no-tools { padding: 12px 16px; color: var(--muted); font-size: 12px; font-style: italic; }
.server-card.hidden { display: none; }
</style>
</head>
<body>
<header>
  <h1>MCP Gateway Tool Catalog</h1>
  <span class="meta" id="meta">Connecting…</span>
  <input class="search-box" type="search" placeholder="Search tools…" oninput="filterTools(this.value)" />
  <button class="btn" onclick="refresh()">Refresh</button>
</header>
<div id="warn"></div>
<div class="layout">
  <aside class="sidebar" id="sidebar"><h3>Servers</h3></aside>
  <main class="main" id="main"><div class="loading">Loading catalog…</div></main>
</div>
<script type="module">
import("https://unpkg.com/@modelcontextprotocol/ext-apps@0.4.0/app-with-deps").then(module => {
  const App = module.App || module.default?.App || module.default;
  const app = new (App.App || App)({ name: "MCP Gateway Catalog", version: "1.0.0" });

  app.ontoolresult = (result) => {
    const sc = result?.structuredContent;
    if (sc) { render(sc); return; }
    const text = result?.content?.find(c => c.type === "text")?.text;
    if (text) { try { render(JSON.parse(text)); } catch(e) {} }
  };

  app.onhostcontextchanged = (ctx) => {
    if (ctx?.theme === "dark") document.documentElement.setAttribute("data-theme", "dark");
    else document.documentElement.removeAttribute("data-theme");
  };

  window.mcpApp = app;
  app.connect();
}).catch(err => {
  document.getElementById("main").innerHTML = '<div class="loading">Failed to load MCP Apps SDK: ' + err.message + '</div>';
});

function refresh() {
  if (!window.mcpApp) return;
  window.mcpApp.callServerTool({ name: "render_tool_catalog", arguments: {} })
    .then(result => {
      const sc = result?.structuredContent;
      if (sc) { render(sc); return; }
      const text = result?.content?.find(c => c.type === "text")?.text;
      if (text) { try { render(JSON.parse(text)); } catch(e) {} }
    })
    .catch(err => console.error("refresh failed", err));
}
window.refresh = refresh;

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  return e;
}

function render(data) {
  document.getElementById("meta").textContent =
    (data.servers?.length || 0) + " servers · " + (data.totalTools || 0) + " tools · " + (data.generatedAt || "");

  const warnEl = document.getElementById("warn");
  warnEl.textContent = "";
  if (!data.brokerOK) warnEl.appendChild(el("div", "warn", "⚠ Broker unreachable — showing Kubernetes data only."));
  if (data.noK8sData) warnEl.appendChild(el("div", "warn", "⚠ No MCPServerRegistrations found — showing broker data only."));

  const sidebar = document.getElementById("sidebar");
  sidebar.textContent = "";
  sidebar.appendChild(el("h3", null, "Servers"));
  const main = document.getElementById("main");
  main.textContent = "";

  (data.servers || []).forEach(srv => {
    const label = document.createElement("label");
    const cb = document.createElement("input");
    cb.type = "checkbox"; cb.checked = true;
    cb.onchange = () => toggleServer(srv.name, cb.checked);
    label.appendChild(cb);
    label.appendChild(document.createTextNode(" " + srv.name));
    sidebar.appendChild(label);

    const card = el("div", "server-card" + (srv.state === "Disabled" ? " disabled" : ""));
    card.dataset.server = srv.name;

    const header = el("div", "server-header");
    if (srv.prefix) header.appendChild(el("span", "server-prefix", srv.prefix));
    header.appendChild(el("span", "server-name", srv.name));
    header.appendChild(el("span", "badge " + (srv.state === "Disabled" ? "badge-disabled" : "badge-enabled"), srv.state));

    const dot = el("span", "dot " + (!data.brokerOK ? "dot-grey" : srv.isReachable ? "dot-green" : "dot-red"));
    dot.title = !data.brokerOK ? "Status unknown" : srv.isReachable ? "Connected" : "Unreachable";
    header.appendChild(dot);

    const cats = (srv.categories || []).join(", ");
    header.appendChild(el("span", "server-meta", (srv.toolCount || 0) + " tools" + (cats ? " · " + cats : "")));
    card.appendChild(header);

    if (srv.hint) card.appendChild(el("div", "hint", srv.hint));

    const toolList = el("div", "tool-list");
    if (srv.tools && srv.tools.length) {
      srv.tools.forEach(t => {
        const row = el("div", "tool-row");
        row.dataset.tool = "";
        row.dataset.server = srv.name;
        row.appendChild(el("span", "tool-name", t.federatedName));
        row.appendChild(el("span", "tool-desc", t.description));
        toolList.appendChild(row);
      });
    } else {
      toolList.appendChild(el("div", "no-tools", "No tools available" + (!data.brokerOK ? " (broker offline)" : "")));
    }
    card.appendChild(toolList);
    main.appendChild(card);
  });
}
window.render = render;

function toggleServer(name, visible) {
  document.querySelectorAll("[data-server=\\"" + name + "\\"]").forEach(el => el.classList.toggle("hidden", !visible));
}
window.toggleServer = toggleServer;

function filterTools(query) {
  const q = query.toLowerCase();
  document.querySelectorAll("[data-tool]").forEach(row => {
    row.classList.toggle("hidden", q !== "" && !row.textContent.toLowerCase().includes(q));
  });
}
window.filterTools = filterTools;
</script>
</body>
</html>"""


def _fetch_broker_tools(broker_url: str, http) -> dict:
    """Returns {short_server_name: [tool_name, ...]} via broker discover_tools."""
    base = broker_url + "/mcp"
    hdrs = {"Content-Type": "application/json", "Accept": "application/json"}
    try:
        r = http.post(base, json={
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "mcp-gateway-admin", "version": "0.1.0"},
            },
        }, timeout=10, headers=hdrs)
        r.raise_for_status()
        session_id = r.headers.get("Mcp-Session-Id") or r.headers.get("mcp-session-id", "")
        if not session_id:
            return {}
        sh = {**hdrs, "Mcp-Session-Id": session_id}
        http.post(base, json={"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
                  timeout=5, headers=sh)
        r2 = http.post(base, json={
            "jsonrpc": "2.0", "id": 2, "method": "tools/call",
            "params": {"name": "discover_tools", "arguments": {}},
        }, timeout=10, headers=sh)
        r2.raise_for_status()
        text = r2.json().get("result", {}).get("content", [{}])[0].get("text", "{}")
        out = {}
        for srv in json.loads(text).get("servers", []):
            raw = srv.get("name", "")
            short = raw.rsplit("/", 1)[-1] if "/" in raw else raw
            out[short] = [{"federatedName": t, "description": ""} for t in srv.get("tools", [])]
        return out
    except Exception:
        return {}


def register(mcp: FastMCP, srv) -> None:
    @mcp.resource(
        CATALOG_RESOURCE_URI,
        name="MCP Gateway Tool Catalog",
        description="Interactive catalog UI for all federated MCP tools",
        app=AppConfig(csp=ResourceCSP(resource_domains=["https://unpkg.com"])),
    )
    def catalog_ui() -> str:
        import sys
        print(">>> resources/read called for catalog UI", file=sys.stderr, flush=True)
        return CATALOG_HTML

    @mcp.tool(
        description="Show an interactive catalog of all federated MCP tools grouped by upstream server",
        app=AppConfig(resource_uri=CATALOG_RESOURCE_URI),
    )
    async def render_tool_catalog(ctx: Context) -> ToolResult:
        # 1. Fetch k8s registrations
        try:
            res = srv.dyn_client.resources.get(
                api_version="mcp.kuadrant.io/v1alpha1",
                kind="MCPServerRegistration",
            )
            items = res.get(namespace=srv.namespace).items
        except Exception:
            items = []

        # 2. Fetch broker status
        broker_ok = False
        broker_servers = []
        try:
            resp = srv.http.get(srv.broker_url + "/status", timeout=10)
            resp.raise_for_status()
            broker_servers = resp.json().get("servers", [])
            broker_ok = True
        except Exception:
            pass

        # 3. Fetch per-server tool lists from broker
        broker_tools = _fetch_broker_tools(srv.broker_url, srv.http) if broker_ok else {}

        # 4. Build broker_by_name lookup keyed by short name (after last '/')
        broker_by_name = {}
        for bs in broker_servers:
            raw = bs.get("name", "")
            short = raw.rsplit("/", 1)[-1] if "/" in raw else raw
            broker_by_name[short] = {
                "reachable": bool(bs.get("ready", False)),
                "toolCount": int(bs.get("totalTools", 0)),
            }

        # 5. Build servers list from k8s registrations
        servers = []
        total_tools = 0
        for item in items:
            name = item.metadata.name
            spec = item.spec
            tool_count = int(getattr(item.status, "discoveredTools", 0) or 0)
            is_reachable = False
            if name in broker_by_name:
                bd = broker_by_name[name]
                is_reachable = bd["reachable"]
                tool_count = bd["toolCount"]
            cs = {
                "name": name,
                "prefix": getattr(spec, "prefix", "") or "",
                "state": str(getattr(spec, "state", "") or ""),
                "categories": list(getattr(spec, "category", None) or []),
                "hint": getattr(spec, "hint", "") or "",
                "isReachable": is_reachable,
                "toolCount": tool_count,
                "tools": broker_tools.get(name, []),
            }
            total_tools += tool_count
            servers.append(cs)

        # 6. Fallback to broker data if no k8s registrations
        no_k8s_data = False
        if not servers and broker_ok and broker_servers:
            no_k8s_data = True
            for bs in broker_servers:
                raw = bs.get("name", "")
                short = raw.rsplit("/", 1)[-1] if "/" in raw else raw
                tool_count = int(bs.get("totalTools", 0))
                servers.append({
                    "name": short,
                    "prefix": "", "state": "", "categories": [], "hint": "",
                    "isReachable": bool(bs.get("ready", False)),
                    "toolCount": tool_count,
                    "tools": broker_tools.get(short, []),
                })
                total_tools += tool_count

        data = {
            "servers": servers,
            "totalTools": total_tools,
            "generatedAt": datetime.now().strftime("%H:%M:%S"),
            "brokerOK": broker_ok,
            "noK8sData": no_k8s_data,
        }
        import sys
        print(f">>> render_tool_catalog — returning result", file=sys.stderr, flush=True)
        ui_supported = ctx.client_supports_extension(UI_EXTENSION_ID)
        if ui_supported:
            return ToolResult(
                content=f"Tool catalog rendered: {len(servers)} servers, {total_tools} tools.",
                structured_content=data,
            )
        return ToolResult(
            content=json.dumps(data),
            structured_content=data,
        )
