import json
import logging
from datetime import datetime

log = logging.getLogger(__name__)
from fastmcp import FastMCP, Context
from fastmcp.apps import UI_EXTENSION_ID, AppConfig, ResourceCSP
from fastmcp.tools import ToolResult

HEALTH_RESOURCE_URI = "ui://mcp-gateway-health"

HEALTH_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MCP Gateway Health Dashboard</title>
<style>
:root {
  /* Fallbacks for PF v6 design tokens */
  --pf-t--global--border--color--default: #d2d2d2;
  --pf-t--global--background--color--primary--default: #ffffff;
  --pf-t--global--background--color--secondary--default: #f0f0f0;
  --pf-t--global--text--color--subtle: #6a6e73;
  --pf-t--global--text--color--regular: #151515;
  --pf-t--global--icon--color--status--success--default: #3e8635;
  /* Local palette */
  --bg: #f8f9fa; --surface: #ffffff; --border: #dee2e6; --text: #212529;
  --muted: #6c757d; --accent: #0d6efd; --green: #198754; --red: #dc3545;
}
.pf-v6-theme-dark {
  --pf-t--global--border--color--default: #444649;
  --pf-t--global--background--color--primary--default: #212427;
  --pf-t--global--background--color--secondary--default: #2d3439;
  --pf-t--global--text--color--subtle: #868686;
  --pf-t--global--text--color--regular: #e0e0e0;
  --pf-t--global--icon--color--status--success--default: #5ba352;
  --bg: #1a1d21; --surface: #25282c; --border: #373b3e; --text: #e9ecef;
  --muted: #868e96; --accent: #4da3ff; --green: #40c97a; --red: #f06a6a;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: system-ui,sans-serif; background: transparent; color: var(--text); font-size: 14px; }
header { padding: 12px 16px; border-bottom: 1px solid var(--border); background: var(--surface); display: flex; align-items: center; gap: 12px; }
header h1 { font-size: 16px; font-weight: 600; }
.meta { color: var(--muted); font-size: 12px; margin-left: auto; }
.btn { padding: 5px 12px; border: 1px solid var(--border); border-radius: 6px; background: var(--surface); color: var(--text); font-size: 12px; cursor: pointer; }
.btn:hover { background: var(--bg); }
.loading { padding: 48px; text-align: center; color: var(--muted); }

/* Broker status banner */
.health-banner { padding: 8px 12px; border-radius: 6px; margin: 10px 12px 0; font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 8px; }
.health-banner.ok { background: #bde5b8; color: #1e4f18; border: 1px solid #6ec664; }
.health-banner.fail { background: #fce3e3; color: #a60000; border: 1px solid #c9190b; }
.pf-v6-theme-dark .health-banner.ok { background: #1e4f18; color: #bde5b8; border-color: #3e8635; }
.pf-v6-theme-dark .health-banner.fail { background: #3d0000; color: #fce3e3; border-color: #c9190b; }

/* Summary stats */
.stats-row { display: flex; gap: 10px; padding: 10px 12px; }
.stat-box { flex: 1; border: 1px solid var(--pf-t--global--border--color--default); border-radius: 6px; padding: 8px 12px; background: var(--pf-t--global--background--color--primary--default); }
.stat-label { font-size: 11px; text-transform: uppercase; color: var(--pf-t--global--text--color--subtle); letter-spacing: .05em; }
.stat-value { font-size: 22px; font-weight: 700; color: var(--pf-t--global--text--color--regular); }
.stat-value.ok { color: var(--pf-t--global--icon--color--status--success--default); }

/* Server status table */
.health-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.health-table th { padding: 6px 12px; text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: .05em; color: var(--pf-t--global--text--color--subtle); border-bottom: 2px solid var(--pf-t--global--border--color--default); background: var(--pf-t--global--background--color--secondary--default); }
.health-table td { padding: 7px 12px; border-bottom: 1px solid var(--pf-t--global--border--color--default); vertical-align: middle; }
.health-table tr:last-child td { border-bottom: none; }
.table-wrapper { background: var(--pf-t--global--background--color--primary--default); border: 1px solid var(--pf-t--global--border--color--default); border-radius: 6px; overflow: hidden; margin: 0 12px 12px; }

/* Dots and badges */
.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
.dot-green { background: var(--green); }
.dot-red { background: var(--red); }
.dot-grey { background: var(--muted); }
.badge { font-size: 11px; padding: 2px 7px; border-radius: 10px; font-weight: 500; }
.badge-enabled { background: #d1fae5; color: #065f46; }
.badge-disabled { background: #f3f4f6; color: var(--muted); }
.badge-unknown { background: #f3f4f6; color: var(--muted); }
.pf-v6-theme-dark .badge-enabled { background: #064e3b; color: #6ee7b7; }
.pf-v6-theme-dark .badge-disabled { background: #374151; color: #9ca3af; }
.pf-v6-theme-dark .badge-unknown { background: #374151; color: #9ca3af; }
</style>
</head>
<body>
<header>
  <h1>MCP Gateway Health</h1>
  <span class="meta" id="meta">Connecting…</span>
  <button class="btn" onclick="refresh()">Refresh</button>
</header>
<div id="banner"></div>
<div id="stats"></div>
<div id="table-area"><div class="loading">Loading health data…</div></div>

<script type="module">
import("https://unpkg.com/@modelcontextprotocol/ext-apps@0.4.0/app-with-deps").then(module => {
  const App = module.App || module.default?.App || module.default;
  const app = new (App.App || App)({ name: "MCP Gateway Health", version: "1.0.0" });

  app.ontoolresult = (result) => {
    const sc = result?.structuredContent;
    if (sc) { render(sc); return; }
    const text = result?.content?.find(c => c.type === "text")?.text;
    if (text) { try { render(JSON.parse(text)); } catch(e) {} }
  };

  app.onhostcontextchanged = (ctx) => {
    if (ctx?.theme === "dark") document.documentElement.classList.add("pf-v6-theme-dark");
    else document.documentElement.classList.remove("pf-v6-theme-dark");
  };

  window.mcpApp = app;
  app.connect();
}).catch(err => {
  const errDiv = document.createElement("div");
  errDiv.className = "loading";
  errDiv.textContent = "Failed to load MCP Apps SDK: " + err.message;
  document.getElementById("table-area").replaceChildren(errDiv);
});

function refresh() {
  if (!window.mcpApp) return;
  window.mcpApp.callServerTool({ name: "render_gateway_health", arguments: {} })
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
  // Update meta
  document.getElementById("meta").textContent =
    (data.totalServers || 0) + " servers · " + (data.totalTools || 0) + " tools · " + (data.generatedAt || "");

  // Broker banner
  const bannerEl = document.getElementById("banner");
  bannerEl.textContent = "";
  const banner = el("div", "health-banner " + (data.brokerOK ? "ok" : "fail"));
  banner.appendChild(el("span", "dot " + (data.brokerOK ? "dot-green" : "dot-red")));
  banner.appendChild(document.createTextNode(
    data.brokerOK
      ? "Broker connected — " + (data.brokerUrl || "")
      : "Broker unreachable — " + (data.brokerUrl || "")
  ));
  bannerEl.appendChild(banner);

  // Stats row
  const statsEl = document.getElementById("stats");
  statsEl.textContent = "";
  const row = el("div", "stats-row");

  const mkStat = (label, value, ok) => {
    const box = el("div", "stat-box");
    box.appendChild(el("div", "stat-label", label));
    box.appendChild(el("div", "stat-value" + (ok ? " ok" : ""), String(value)));
    return box;
  };
  row.appendChild(mkStat("Total Servers", data.totalServers || 0, false));
  row.appendChild(mkStat("Reachable", data.reachableServers || 0, (data.reachableServers || 0) > 0));
  row.appendChild(mkStat("Total Tools", data.totalTools || 0, false));
  statsEl.appendChild(row);

  // Server table
  const tableArea = document.getElementById("table-area");
  tableArea.textContent = "";

  if (!data.servers || data.servers.length === 0) {
    tableArea.appendChild(el("div", "loading", "No servers found."));
    return;
  }

  const wrapper = el("div", "table-wrapper");
  const table = el("table", "health-table");

  const thead = document.createElement("thead");
  const hrow = document.createElement("tr");
  ["", "Server", "State", "Tools", "Categories"].forEach(h => {
    hrow.appendChild(el("th", null, h));
  });
  thead.appendChild(hrow);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  (data.servers || []).forEach(srv => {
    const tr = document.createElement("tr");

    // Status dot
    const dotTd = document.createElement("td");
    const dot = el("span", "dot " + (!data.brokerOK ? "dot-grey" : srv.isReachable ? "dot-green" : "dot-red"));
    dot.title = !data.brokerOK ? "Status unknown" : srv.isReachable ? "Connected" : "Unreachable";
    dotTd.appendChild(dot);
    tr.appendChild(dotTd);

    // Server name
    tr.appendChild(el("td", null, srv.name));

    // State badge
    const stateTd = document.createElement("td");
    const state = (srv.state || "").toLowerCase();
    const badgeCls = state === "enabled" ? "badge badge-enabled"
                   : state === "disabled" ? "badge badge-disabled"
                   : "badge badge-unknown";
    stateTd.appendChild(el("span", badgeCls, srv.state || "—"));
    tr.appendChild(stateTd);

    // Tool count
    tr.appendChild(el("td", null, String(srv.toolCount || 0)));

    // Categories
    tr.appendChild(el("td", null, (srv.categories || []).join(", ") || "—"));

    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  wrapper.appendChild(table);
  tableArea.appendChild(wrapper);
}
window.render = render;
</script>
</body>
</html>"""


def register(mcp: FastMCP, srv) -> None:
    @mcp.resource(
        HEALTH_RESOURCE_URI,
        name="MCP Gateway Health Dashboard",
        description="Live broker and server connectivity status dashboard",
        app=AppConfig(csp=ResourceCSP(resource_domains=["https://unpkg.com"])),
    )
    def health_ui() -> str:
        return HEALTH_HTML

    @mcp.tool(
        description="Show live gateway health dashboard",
        app=AppConfig(resource_uri=HEALTH_RESOURCE_URI),
    )
    async def render_gateway_health(ctx: Context) -> ToolResult:
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

        # 3. Build broker_by_name lookup keyed by short name (after last '/')
        broker_by_name = {}
        for bs in broker_servers:
            raw = bs.get("name", "")
            short = raw.rsplit("/", 1)[-1] if "/" in raw else raw
            broker_by_name[short] = {
                "reachable": bool(bs.get("ready", False)),
                "toolCount": int(bs.get("totalTools", 0)),
            }

        # 4. Build servers list from k8s registrations
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
            servers.append({
                "name": name,
                "state": str(getattr(spec, "state", "") or ""),
                "categories": list(getattr(spec, "category", None) or []),
                "isReachable": is_reachable,
                "toolCount": tool_count,
            })
            total_tools += tool_count

        # 5. Fallback to broker data if no k8s registrations
        if not servers and broker_ok and broker_servers:
            for bs in broker_servers:
                raw = bs.get("name", "")
                short = raw.rsplit("/", 1)[-1] if "/" in raw else raw
                tool_count = int(bs.get("totalTools", 0))
                servers.append({
                    "name": short,
                    "state": "",
                    "categories": [],
                    "isReachable": bool(bs.get("ready", False)),
                    "toolCount": tool_count,
                })
                total_tools += tool_count

        reachable_count = sum(1 for s in servers if s["isReachable"])

        data = {
            "brokerOK": broker_ok,
            "brokerUrl": srv.broker_url,
            "generatedAt": datetime.now().strftime("%H:%M:%S"),
            "servers": servers,
            "totalTools": total_tools,
            "totalServers": len(servers),
            "reachableServers": reachable_count,
        }
        ui_meta = {"ui": {"resourceUri": HEALTH_RESOURCE_URI}}
        ui_supported = ctx.client_supports_extension(UI_EXTENSION_ID)
        if ui_supported:
            return ToolResult(
                content=f"Gateway health: {reachable_count}/{len(servers)} servers reachable, {total_tools} tools.",
                structured_content=data,
                meta=ui_meta,
            )
        return ToolResult(
            content=json.dumps(data),
            structured_content=data,
            meta=ui_meta,
        )


# To activate: in server.py, add:
#   from tools import gateway_health_ui
#   gateway_health_ui.register(mcp, admin)
