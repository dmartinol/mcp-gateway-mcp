import json
import logging
from datetime import datetime

log = logging.getLogger(__name__)
from fastmcp import FastMCP, Context
from fastmcp.apps import UI_EXTENSION_ID, AppConfig, ResourceCSP
from fastmcp.tools import ToolResult

REGISTRATION_RESOURCE_URI = "ui://mcp-gateway-registrations"

REGISTRATION_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Registration Manager</title>
<style>
/* PF token fallbacks — overridden once PF CSS loads */
:root {
  --pf-t--global--background--color--primary--default: #ffffff;
  --pf-t--global--background--color--secondary--default: #f4f4f5;
  --pf-t--global--border--color--default: #d2d2d2;
  --pf-t--global--text--color--default: #151515;
  --pf-t--global--text--color--subtle: #6a6e73;
  --pf-t--global--color--blue--40: #0066cc;
  --pf-t--global--font--family--mono: 'SF Mono','Consolas','Menlo',monospace;
}
.pf-v6-theme-dark {
  --pf-t--global--background--color--primary--default: #1b1d21;
  --pf-t--global--background--color--secondary--default: #25282c;
  --pf-t--global--border--color--default: #3c3f42;
  --pf-t--global--text--color--default: #e0e0e0;
  --pf-t--global--text--color--subtle: #8a8d90;
  --pf-t--global--color--blue--40: #4da3ff;
  --pf-t--global--font--family--mono: 'SF Mono','Consolas','Menlo',monospace;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: system-ui, sans-serif;
  background: transparent;
  color: var(--pf-t--global--text--color--default);
  font-size: 14px;
}
.masthead {
  height: 44px;
  background: #212427;
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 12px;
  border-bottom: 1px solid #000;
}
.masthead h1 {
  font-size: 14px;
  font-weight: 600;
  color: #e0e0e0;
  white-space: nowrap;
}
.masthead .meta {
  font-size: 11px;
  color: #8a8d90;
}
.masthead .spacer { flex: 1; }
.loading { padding: 32px; text-align: center; color: var(--pf-t--global--text--color--subtle); }
/* PF v6 switch shim (overridden once PF CSS loads) */
.pf-v6-c-switch { display: inline-flex; align-items: center; gap: 8px; cursor: pointer; }
.pf-v6-c-switch__input { position: absolute; opacity: 0; width: 0; height: 0; }
.pf-v6-c-switch__toggle {
  width: 36px; height: 20px; border-radius: 10px;
  background: var(--pf-t--global--border--color--default);
  position: relative; transition: background 0.2s; flex-shrink: 0;
}
.pf-v6-c-switch__toggle::after {
  content: ""; position: absolute; top: 2px; left: 2px;
  width: 16px; height: 16px; border-radius: 50%;
  background: #fff; transition: left 0.2s;
}
.pf-v6-c-switch__input:checked + .pf-v6-c-switch__toggle { background: var(--pf-t--global--color--blue--40); }
.pf-v6-c-switch__input:checked + .pf-v6-c-switch__toggle::after { left: 18px; }
.pf-v6-c-switch__label { font-size: 12px; color: var(--pf-t--global--text--color--subtle); }
.pf-v6-c-switch__label.pf-m-on { display: none; }
.pf-v6-c-switch__label.pf-m-off { display: inline; }
.pf-v6-c-switch__input:checked ~ .pf-v6-c-switch__label.pf-m-on { display: inline; }
.pf-v6-c-switch__input:checked ~ .pf-v6-c-switch__label.pf-m-off { display: none; }
.pf-v6-c-switch__input:disabled + .pf-v6-c-switch__toggle { opacity: 0.5; cursor: not-allowed; }
/* Table */
.table-wrapper {
  background: var(--pf-t--global--background--color--primary--default);
  border: 1px solid var(--pf-t--global--border--color--default);
  border-radius: 6px;
  overflow: hidden;
  margin: 10px 12px;
}
.reg-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.reg-table th {
  padding: 6px 12px;
  text-align: left;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: .05em;
  color: var(--pf-t--global--text--color--subtle);
  border-bottom: 2px solid var(--pf-t--global--border--color--default);
  background: var(--pf-t--global--background--color--secondary--default);
}
.reg-table td { padding: 8px 12px; border-bottom: 1px solid var(--pf-t--global--border--color--default); vertical-align: middle; }
.reg-table tr:last-child td { border-bottom: none; }
.reg-name { font-family: var(--pf-t--global--font--family--mono); font-size: 13px; color: var(--pf-t--global--color--blue--40); }
.reg-prefix {
  font-family: var(--pf-t--global--font--family--mono);
  font-size: 11px;
  color: var(--pf-t--global--text--color--subtle);
  background: var(--pf-t--global--background--color--secondary--default);
  padding: 1px 4px; border-radius: 3px;
  border: 1px solid var(--pf-t--global--border--color--default);
}
.reg-hint { font-size: 12px; color: var(--pf-t--global--text--color--subtle); font-style: italic; }
.reg-cats { display: flex; gap: 4px; flex-wrap: wrap; }
.reg-cat {
  display: inline-block; padding: 1px 6px; border-radius: 10px; font-size: 11px;
  background: var(--pf-t--global--background--color--secondary--default);
  border: 1px solid var(--pf-t--global--border--color--default);
}
.empty { padding: 24px; text-align: center; color: var(--pf-t--global--text--color--subtle); font-size: 13px; }
</style>
</head>
<body>
<div class="masthead">
  <h1>Registration Manager</h1>
  <span class="meta" id="meta">Connecting…</span>
  <span class="spacer"></span>
</div>
<div id="content"><div class="loading">Loading registrations…</div></div>
<script type="module">
import("https://unpkg.com/@modelcontextprotocol/ext-apps@0.4.0/app-with-deps").then(module => {
  const App = module.App || module.default?.App || module.default;
  const app = new (App.App || App)({ name: "MCP Gateway Registration Manager", version: "1.0.0" });

  // Load PF CSS via fetch to avoid CSP <link> restriction
  fetch("https://unpkg.com/@patternfly/patternfly@6/patternfly.min.css")
    .then(r => r.text())
    .then(css => {
      const s = document.createElement("style");
      s.textContent = css;
      document.head.insertBefore(s, document.head.querySelector("style"));
    })
    .catch(() => {}); // fallback shim CSS already in <style>

  app.ontoolresult = (result) => {
    const sc = result?.structuredContent;
    if (sc) { render(sc); return; }
    const text = result?.content?.find(c => c.type === "text")?.text;
    if (text) { try { render(JSON.parse(text)); } catch(e) {} }
  };

  app.onhostcontextchanged = (ctx) => {
    if (ctx?.theme === "dark") {
      document.documentElement.classList.add("pf-v6-theme-dark");
    } else {
      document.documentElement.classList.remove("pf-v6-theme-dark");
    }
  };

  window.mcpApp = app;
  app.connect();
}).catch(err => {
  const d = document.createElement("div");
  d.className = "loading";
  d.textContent = "Failed to load MCP Apps SDK: " + err.message;
  const content = document.getElementById("content");
  content.textContent = "";
  content.appendChild(d);
});

async function toggleRegistration(name, enabled, checkboxEl) {
  checkboxEl.disabled = true;
  const newState = enabled ? "Enabled" : "Disabled";
  try {
    await window.mcpApp.callServerTool({
      name: "update_registration_state",
      arguments: { name, state: newState }
    });
  } catch(e) {
    // revert on error
    checkboxEl.checked = !enabled;
  } finally {
    checkboxEl.disabled = false;
  }
}
window.toggleRegistration = toggleRegistration;

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  return e;
}

function render(data) {
  const count = data.registrations?.length || 0;
  document.getElementById("meta").textContent =
    count + " registration" + (count !== 1 ? "s" : "") + " · " + (data.generatedAt || "");

  const content = document.getElementById("content");
  if (!count) {
    content.innerHTML = '<div class="empty">No MCPServerRegistrations found.</div>';
    return;
  }

  const wrapper = el("div", "table-wrapper");
  const table = el("table", "reg-table");
  const thead = document.createElement("thead");
  const hrow = document.createElement("tr");
  ["Name", "State", "Prefix", "Categories", "Hint"].forEach(h => {
    hrow.appendChild(el("th", null, h));
  });
  thead.appendChild(hrow);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  (data.registrations || []).forEach(reg => {
    const tr = document.createElement("tr");

    // Name
    const tdName = el("td");
    tdName.appendChild(el("span", "reg-name", reg.name));
    tr.appendChild(tdName);

    // State toggle
    const tdState = el("td");
    const label = el("label", "pf-v6-c-switch");
    const cb = el("input");
    cb.type = "checkbox";
    cb.className = "pf-v6-c-switch__input";
    cb.checked = reg.state === "Enabled";
    cb.onchange = () => toggleRegistration(reg.name, cb.checked, cb);
    const toggle = el("span", "pf-v6-c-switch__toggle");
    toggle.appendChild(el("span", "pf-v6-c-switch__toggle-icon"));
    const labelOn = el("span", "pf-v6-c-switch__label pf-m-on", "Enabled");
    const labelOff = el("span", "pf-v6-c-switch__label pf-m-off", "Disabled");
    label.appendChild(cb);
    label.appendChild(toggle);
    label.appendChild(labelOn);
    label.appendChild(labelOff);
    tdState.appendChild(label);
    tr.appendChild(tdState);

    // Prefix
    const tdPrefix = el("td");
    if (reg.prefix) tdPrefix.appendChild(el("code", "reg-prefix", reg.prefix));
    tr.appendChild(tdPrefix);

    // Categories
    const tdCats = el("td");
    if (reg.categories && reg.categories.length) {
      const cats = el("div", "reg-cats");
      reg.categories.forEach(c => cats.appendChild(el("span", "reg-cat", c)));
      tdCats.appendChild(cats);
    }
    tr.appendChild(tdCats);

    // Hint
    const tdHint = el("td");
    if (reg.hint) tdHint.appendChild(el("span", "reg-hint", reg.hint));
    tr.appendChild(tdHint);

    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  wrapper.appendChild(table);
  content.textContent = "";
  content.appendChild(wrapper);
}
window.render = render;
</script>
</body>
</html>"""


def register(mcp: FastMCP, srv) -> None:
    @mcp.resource(
        REGISTRATION_RESOURCE_URI,
        name="MCP Gateway Registration Manager",
        description="Interactive UI for enabling/disabling MCPServerRegistration CRs",
        app=AppConfig(
            csp=ResourceCSP(
                resource_domains=["https://unpkg.com"],
                connect_domains=["https://unpkg.com"],
            )
        ),
    )
    def registration_ui() -> str:
        return REGISTRATION_HTML

    @mcp.tool(
        description="Show interactive registration manager for all MCP server registrations",
        app=AppConfig(resource_uri=REGISTRATION_RESOURCE_URI),
    )
    async def render_registrations(ctx: Context) -> ToolResult:
        # Fetch all MCPServerRegistration CRs from Kubernetes
        try:
            res = srv.dyn_client.resources.get(
                api_version="mcp.kuadrant.io/v1alpha1",
                kind="MCPServerRegistration",
            )
            items = res.get(namespace=srv.namespace).items
        except Exception:
            items = []

        registrations = []
        for item in items:
            spec = item.spec
            registrations.append({
                "name": item.metadata.name,
                "state": str(getattr(spec, "state", "") or ""),
                "prefix": getattr(spec, "prefix", "") or "",
                "categories": list(getattr(spec, "category", None) or []),
                "hint": getattr(spec, "hint", "") or "",
            })

        data = {
            "registrations": registrations,
            "generatedAt": datetime.now().strftime("%H:%M:%S"),
        }
        ui_meta = {"ui": {"resourceUri": REGISTRATION_RESOURCE_URI}}
        ui_supported = ctx.client_supports_extension(UI_EXTENSION_ID)
        if ui_supported:
            return ToolResult(
                content=f"Registration manager rendered: {len(registrations)} registrations.",
                structured_content=data,
                meta=ui_meta,
            )
        return ToolResult(
            content=json.dumps(data),
            structured_content=data,
            meta=ui_meta,
        )


# To activate: in server.py, add:
#   from tools import registration_ui
#   registration_ui.register(mcp, admin)
