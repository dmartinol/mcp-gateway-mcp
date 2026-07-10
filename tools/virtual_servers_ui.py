import json
import logging
from datetime import datetime

log = logging.getLogger(__name__)
from fastmcp import FastMCP, Context
from fastmcp.apps import UI_EXTENSION_ID, AppConfig, ResourceCSP
from fastmcp.tools import ToolResult

VSRV_RESOURCE_URI = "ui://mcp-gateway-virtual-servers"

VSRV_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Virtual Server Viewer</title>
<style>
:root {
  --pf-t--global--background--color--primary--default: #ffffff;
  --pf-t--global--background--color--secondary--default: #f8f9fa;
  --pf-t--global--border--color--default: #dee2e6;
  --pf-t--global--text--color--regular: #212529;
  --pf-t--global--text--color--subtle: #6c757d;
  --pf-t--global--icon--color--status--success--default: #198754;
  --pf-t--global--icon--color--status--danger--default: #dc3545;
  --pf-t--global--color--brand--default: #0d6efd;
  --header-bg: #1a1d21;
  --header-text: #f0f0f0;
}
@media (prefers-color-scheme: dark) {
  :root {
    --pf-t--global--background--color--primary--default: #25282c;
    --pf-t--global--background--color--secondary--default: #1a1d21;
    --pf-t--global--border--color--default: #373b3e;
    --pf-t--global--text--color--regular: #e9ecef;
    --pf-t--global--text--color--subtle: #868e96;
    --pf-t--global--icon--color--status--success--default: #40c97a;
    --pf-t--global--icon--color--status--danger--default: #f06a6a;
    --pf-t--global--color--brand--default: #4da3ff;
  }
}
.pf-v6-theme-dark {
  --pf-t--global--background--color--primary--default: #25282c;
  --pf-t--global--background--color--secondary--default: #1a1d21;
  --pf-t--global--border--color--default: #373b3e;
  --pf-t--global--text--color--regular: #e9ecef;
  --pf-t--global--text--color--subtle: #868e96;
  --pf-t--global--icon--color--status--success--default: #40c97a;
  --pf-t--global--icon--color--status--danger--default: #f06a6a;
  --pf-t--global--color--brand--default: #4da3ff;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: system-ui, sans-serif; background: transparent; color: var(--pf-t--global--text--color--regular); font-size: 14px; }
header {
  height: 44px; background: var(--header-bg); color: var(--header-text);
  display: flex; align-items: center; gap: 12px; padding: 0 16px;
  border-bottom: 1px solid var(--pf-t--global--border--color--default);
  flex-shrink: 0;
}
header h1 { font-size: 15px; font-weight: 600; letter-spacing: .01em; }
.meta { font-size: 12px; color: #adb5bd; margin-left: 8px; }
.btn {
  margin-left: auto; padding: 5px 12px; border: 1px solid #495057;
  border-radius: 6px; background: #2c3035; color: #e9ecef;
  font-size: 12px; cursor: pointer;
}
.btn:hover { background: #373b3e; }
.content-wrap { padding: 10px 12px; }
.accordion-item {
  border: 1px solid var(--pf-t--global--border--color--default);
  border-radius: 6px; margin-bottom: 8px; overflow: hidden;
  background: var(--pf-t--global--background--color--primary--default);
}
.accordion-header {
  display: flex; align-items: center; gap: 8px; padding: 8px 12px;
  cursor: pointer; font-size: 13px; font-weight: 600;
  border-bottom: 1px solid transparent;
}
.accordion-header:hover { background: var(--pf-t--global--background--color--secondary--default); }
.accordion-header.open { border-bottom-color: var(--pf-t--global--border--color--default); }
.accordion-chevron { font-size: 10px; color: var(--pf-t--global--text--color--subtle); }
.accordion-body { padding: 10px 12px; font-size: 13px; }
.accordion-body.hidden { display: none; }
.section-label {
  font-size: 11px; text-transform: uppercase; letter-spacing: .05em;
  color: var(--pf-t--global--text--color--subtle); font-weight: 600;
  margin-bottom: 6px; margin-top: 10px;
}
.section-label:first-child { margin-top: 0; }
.kv-grid {
  display: grid; grid-template-columns: 160px 1fr;
  gap: 3px 12px; font-size: 12px;
}
.kv-key { color: var(--pf-t--global--text--color--subtle); font-weight: 600; }
.kv-val { color: var(--pf-t--global--text--color--regular); word-break: break-word; }
.cond-row {
  display: flex; align-items: flex-start; gap: 8px; padding: 4px 0;
  border-bottom: 1px solid var(--pf-t--global--border--color--default); font-size: 12px;
}
.cond-row:last-child { border-bottom: none; }
.cond-type { font-weight: 600; min-width: 100px; }
.cond-status-true { color: var(--pf-t--global--icon--color--status--success--default); font-weight: bold; }
.cond-status-false { color: var(--pf-t--global--icon--color--status--danger--default); font-weight: bold; }
.cond-reason { color: var(--pf-t--global--text--color--subtle); min-width: 100px; }
.cond-msg { color: var(--pf-t--global--text--color--subtle); font-style: italic; }
.no-vsrv {
  padding: 32px; text-align: center; font-size: 13px;
  color: var(--pf-t--global--text--color--subtle);
}
.upstream-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.upstream-table th {
  text-align: left; padding: 4px 8px; font-size: 11px; text-transform: uppercase;
  letter-spacing: .05em; color: var(--pf-t--global--text--color--subtle); font-weight: 600;
  border-bottom: 1px solid var(--pf-t--global--border--color--default);
}
.upstream-table td {
  padding: 4px 8px;
  border-bottom: 1px solid var(--pf-t--global--border--color--default);
  color: var(--pf-t--global--text--color--regular);
  word-break: break-all;
}
.upstream-table tr:last-child td { border-bottom: none; }
.loading { padding: 32px; text-align: center; color: var(--pf-t--global--text--color--subtle); font-size: 13px; }
</style>
</head>
<body>
<header>
  <h1>Virtual Server Viewer</h1>
  <span class="meta" id="meta">Connecting…</span>
  <button class="btn" onclick="refresh()">Refresh</button>
</header>
<div class="content-wrap" id="main">
  <div class="loading">Loading virtual servers…</div>
</div>
<script type="module">
import("https://unpkg.com/@modelcontextprotocol/ext-apps@0.4.0/app-with-deps").then(module => {
  const App = module.App || module.default?.App || module.default;
  const app = new (App.App || App)({ name: "MCP Gateway Virtual Servers", version: "1.0.0" });

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
  document.getElementById("main").textContent = "";
  document.getElementById("main").appendChild(errDiv);
});

function refresh() {
  if (!window.mcpApp) return;
  window.mcpApp.callServerTool({ name: "render_virtual_servers", arguments: {} })
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

function renderConditions(conditions) {
  if (!conditions || !conditions.length) {
    return el("div", "kv-val", "No conditions reported.");
  }
  const wrap = document.createElement("div");
  conditions.forEach(cond => {
    const row = el("div", "cond-row");
    row.appendChild(el("span", "cond-type", cond.type || ""));
    const statusCls = String(cond.status).toLowerCase() === "true"
      ? "cond-status-true" : "cond-status-false";
    row.appendChild(el("span", statusCls, cond.status || ""));
    row.appendChild(el("span", "cond-reason", cond.reason || ""));
    row.appendChild(el("span", "cond-msg", cond.message || ""));
    wrap.appendChild(row);
  });
  return wrap;
}

function renderUpstreams(upstreams) {
  if (!upstreams || !upstreams.length) {
    return el("div", "kv-val", "No upstreams defined.");
  }
  const tbl = el("table", "upstream-table");
  const thead = document.createElement("thead");
  const hr = document.createElement("tr");
  ["Name", "Namespace", "Kind"].forEach(h => hr.appendChild(el("th", null, h)));
  thead.appendChild(hr);
  tbl.appendChild(thead);
  const tbody = document.createElement("tbody");
  upstreams.forEach(u => {
    const tr = document.createElement("tr");
    const name = typeof u === "string" ? u : (u.name || u.server || JSON.stringify(u));
    const ns = typeof u === "object" ? (u.namespace || "") : "";
    const kind = typeof u === "object" ? (u.kind || "") : "";
    tr.appendChild(el("td", null, name));
    tr.appendChild(el("td", null, ns));
    tr.appendChild(el("td", null, kind));
    tbody.appendChild(tr);
  });
  tbl.appendChild(tbody);
  return tbl;
}

function renderKV(obj) {
  const grid = el("div", "kv-grid");
  Object.entries(obj).forEach(([k, v]) => {
    grid.appendChild(el("span", "kv-key", k));
    const val = typeof v === "object" ? JSON.stringify(v) : String(v ?? "");
    grid.appendChild(el("span", "kv-val", val));
  });
  return grid;
}

function toggleAccordion(header, body) {
  const open = header.classList.toggle("open");
  body.classList.toggle("hidden", !open);
  const chevron = header.querySelector(".accordion-chevron");
  if (chevron) chevron.textContent = open ? "▼" : "▶";
}

function render(data) {
  const count = data.virtualServers?.length || 0;
  document.getElementById("meta").textContent =
    count + " virtual server" + (count !== 1 ? "s" : "") + " · " + (data.generatedAt || "");

  const main = document.getElementById("main");
  main.textContent = "";

  if (!count) {
    main.appendChild(el("div", "no-vsrv", "No MCPVirtualServer resources found."));
    return;
  }

  data.virtualServers.forEach(vsrv => {
    const item = el("div", "accordion-item");

    const header = el("div", "accordion-header");
    const chevron = el("span", "accordion-chevron", "▶");
    header.appendChild(chevron);
    header.appendChild(el("span", null, vsrv.name));
    if (vsrv.namespace) {
      const ns = el("span", "kv-key");
      ns.textContent = " (" + vsrv.namespace + ")";
      ns.style.fontWeight = "normal";
      ns.style.fontSize = "11px";
      header.appendChild(ns);
    }
    item.appendChild(header);

    const body = el("div", "accordion-body hidden");

    // Upstreams section
    body.appendChild(el("div", "section-label", "Upstreams"));
    body.appendChild(renderUpstreams(vsrv.upstreams));

    // Status conditions
    body.appendChild(el("div", "section-label", "Status Conditions"));
    body.appendChild(renderConditions(vsrv.status_conditions));

    // Spec fields
    if (vsrv.spec_extra && Object.keys(vsrv.spec_extra).length) {
      body.appendChild(el("div", "section-label", "Spec"));
      body.appendChild(renderKV(vsrv.spec_extra));
    }

    item.appendChild(body);

    header.addEventListener("click", () => toggleAccordion(header, body));

    main.appendChild(item);
  });
}
window.render = render;
</script>
</body>
</html>"""


def register(mcp: FastMCP, srv) -> None:
    @mcp.resource(
        VSRV_RESOURCE_URI,
        name="MCP Gateway Virtual Server Viewer",
        description="Interactive viewer for MCPVirtualServer CRs with routing rules and status",
        app=AppConfig(csp=ResourceCSP(resource_domains=["https://unpkg.com"])),
    )
    def virtual_servers_ui() -> str:
        return VSRV_HTML

    @mcp.tool(
        description="Show interactive virtual server viewer",
        app=AppConfig(resource_uri=VSRV_RESOURCE_URI),
    )
    async def render_virtual_servers(ctx: Context) -> ToolResult:
        # Fetch all MCPVirtualServer CRs from Kubernetes
        try:
            resource = srv.dyn_client.resources.get(
                api_version="mcp.kuadrant.io/v1alpha1",
                kind="MCPVirtualServer",
            )
            items = resource.get(namespace=srv.namespace).items
        except Exception:
            items = []

        virtual_servers = []
        for item in items:
            spec = item.spec or {}

            # Upstreams: try common field names for upstream server references
            upstreams = (
                list(getattr(spec, "upstreams", None) or [])
                or list(getattr(spec, "servers", None) or [])
                or list(getattr(spec, "backends", None) or [])
            )

            # Status conditions
            status = getattr(item, "status", None)
            raw_conditions = list(getattr(status, "conditions", None) or [])
            status_conditions = []
            for cond in raw_conditions:
                if hasattr(cond, "type"):
                    status_conditions.append({
                        "type": str(getattr(cond, "type", "")),
                        "status": str(getattr(cond, "status", "")),
                        "reason": str(getattr(cond, "reason", "") or ""),
                        "message": str(getattr(cond, "message", "") or ""),
                    })
                elif isinstance(cond, dict):
                    status_conditions.append({
                        "type": str(cond.get("type", "")),
                        "status": str(cond.get("status", "")),
                        "reason": str(cond.get("reason", "") or ""),
                        "message": str(cond.get("message", "") or ""),
                    })

            # Build spec_extra with remaining top-level spec fields (excluding upstreams/servers/backends)
            spec_extra = {}
            skip_keys = {"upstreams", "servers", "backends"}
            if hasattr(spec, "__dict__"):
                raw_spec = {k: v for k, v in vars(spec).items() if not k.startswith("_")}
            elif isinstance(spec, dict):
                raw_spec = dict(spec)
            else:
                raw_spec = {}
            for k, v in raw_spec.items():
                if k in skip_keys:
                    continue
                try:
                    json.dumps(v)
                    spec_extra[k] = v
                except (TypeError, ValueError):
                    spec_extra[k] = str(v)

            vsrv_dict = {
                "name": item.metadata.name,
                "namespace": item.metadata.namespace or "",
                "upstreams": upstreams,
                "status_conditions": status_conditions,
                "spec_extra": spec_extra,
            }
            virtual_servers.append(vsrv_dict)

        data = {
            "virtualServers": virtual_servers,
            "generatedAt": datetime.now().strftime("%H:%M:%S"),
        }
        ui_meta = {"ui": {"resourceUri": VSRV_RESOURCE_URI}}
        ui_supported = ctx.client_supports_extension(UI_EXTENSION_ID)
        if ui_supported:
            return ToolResult(
                content=f"Virtual server viewer: {len(virtual_servers)} MCPVirtualServer(s) found.",
                structured_content=data,
                meta=ui_meta,
            )
        return ToolResult(
            content=json.dumps(data),
            structured_content=data,
            meta=ui_meta,
        )


# To activate: in server.py, add:
#   from tools import virtual_servers_ui
#   virtual_servers_ui.register(mcp, admin)
