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
/* ── PF v6 design-token fallbacks ──────────────────────────────────────────
   Defined here so the page looks correct even if patternfly.css can't load.
   The fetched patternfly.css is injected BEFORE this block, so it takes
   precedence for any token it defines; our shims fill the rest.           */
:root {
  --pf-t--global--text--color--regular: #151515;
  --pf-t--global--text--color--subtle: #6a6e73;
  --pf-t--global--text--color--on-dark--regular: #e0e0e0;
  --pf-t--global--text--color--on-dark--subtle: #8a8d90;
  --pf-t--global--background--color--primary--default: #ffffff;
  --pf-t--global--background--color--secondary--default: #f0f0f0;
  --pf-t--global--border--color--default: #d2d2d2;
  --pf-t--global--border--radius--small: 3px;
  --pf-t--global--color--blue--40: #0066cc;
  --pf-t--global--icon--color--status--success--default: #3e8635;
  --pf-t--global--icon--color--status--danger--default: #c9190b;
  --pf-t--global--spacer--xs: 0.25rem;
  --pf-t--global--spacer--sm: 0.5rem;
  --pf-t--global--spacer--md: 1rem;
  --pf-t--global--spacer--lg: 1.5rem;
  --pf-t--global--spacer--3xl: 4rem;
  --pf-t--global--font--family--body: "RedHatDisplay","Red Hat Display",Helvetica,Arial,sans-serif;
  --pf-t--global--font--family--mono: "Red Hat Mono","Courier New",Courier,monospace;
  --pf-t--global--font--size--xs: 0.75rem;
  --pf-t--global--font--size--sm: 0.875rem;
  --pf-t--global--font--size--md: 1rem;
  --pf-t--global--font--size--lg: 1.125rem;
  --pf-t--global--font--weight--bold: 700;
  --pf-v6-c-page__header--MinHeight: 4.375rem;
}
.pf-v6-theme-dark {
  --pf-t--global--text--color--regular: #e0e0e0;
  --pf-t--global--text--color--subtle: #8a8d90;
  --pf-t--global--background--color--primary--default: #1b1d21;
  --pf-t--global--background--color--secondary--default: #212427;
  --pf-t--global--border--color--default: #444749;
  --pf-t--global--color--blue--40: #73bcf7;
}

/* ── PF v6 component shims ─────────────────────────────────────────────────
   Minimal structural CSS for every PF class we use.  The injected
   patternfly.css enhances these with full PF styling.                     */
*, *::before, *::after { box-sizing: border-box; }
body {
  font-family: var(--pf-t--global--font--family--body);
  font-size: var(--pf-t--global--font--size--md);
  color: var(--pf-t--global--text--color--regular);
  background: transparent;
  margin: 0; padding: 0;
}

.pf-v6-c-masthead {
  display: flex; align-items: center; flex-shrink: 0;
  background-color: #212427;
  padding: 0 12px;
  min-height: 44px;
}
.pf-v6-c-masthead__main { display: flex; align-items: center; margin-right: 12px; }
.pf-v6-c-masthead__content { display: flex; align-items: center; flex: 1; }

/* ── Tabs shim ── */
.pf-v6-c-tabs {
  padding: 0 12px;
  border-bottom: 1px solid var(--pf-t--global--border--color--default);
}
.pf-v6-c-tabs__list {
  display: flex; list-style: none; margin: 0; padding: 0; overflow-x: auto;
}
.pf-v6-c-tabs__item { display: flex; }
.pf-v6-c-tabs__link {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 7px 12px;
  border: none; background: transparent; cursor: pointer;
  font-size: 13px; font-family: inherit;
  color: var(--pf-t--global--text--color--subtle);
  border-bottom: 3px solid transparent; margin-bottom: -1px; white-space: nowrap;
}
.pf-v6-c-tabs__item.pf-m-current .pf-v6-c-tabs__link {
  color: var(--pf-t--global--color--blue--40);
  border-bottom-color: var(--pf-t--global--color--blue--40);
  font-weight: var(--pf-t--global--font--weight--bold);
}
.pf-v6-c-tabs__link:hover { color: var(--pf-t--global--text--color--regular); }

/* ── Badge shim ── */
.pf-v6-c-badge {
  display: inline-flex; align-items: center; justify-content: center;
  background: var(--pf-t--global--color--blue--40); color: #fff;
  border-radius: 30px; font-size: 11px;
  font-weight: var(--pf-t--global--font--weight--bold);
  padding: 1px 5px; min-width: 1.3em;
}

.pf-v6-c-label {
  display: inline-flex; align-items: center; border-radius: 30px;
  padding: 1px 8px;
  font-size: 11px; font-weight: var(--pf-t--global--font--weight--bold);
  border: 1px solid #d2d2d2; background: #f0f0f0; color: #3c3f42; white-space: nowrap;
}
.pf-v6-c-label.pf-m-green { background: #bde5b8; border-color: #6ec664; color: #1e4f18; }
.pf-v6-theme-dark .pf-v6-c-label.pf-m-green { background: #1e4f18; border-color: #3e8635; color: #bde5b8; }
.pf-v6-c-label__content { display: flex; align-items: center; }

.pf-v6-c-button {
  display: inline-flex; align-items: center; justify-content: center;
  padding: 3px 10px;
  border-radius: 3px; font-size: 12px;
  font-weight: var(--pf-t--global--font--weight--bold); font-family: inherit;
  cursor: pointer; line-height: 1.5; white-space: nowrap; border: 1px solid transparent;
}
.pf-v6-c-button.pf-m-secondary { background: transparent; border-color: rgba(255,255,255,0.4); color: #e0e0e0; }
.pf-v6-c-button.pf-m-secondary:hover { background: rgba(255,255,255,0.1); }

.pf-v6-c-alert {
  display: flex; align-items: flex-start; gap: var(--pf-t--global--spacer--sm);
  padding: var(--pf-t--global--spacer--sm) var(--pf-t--global--spacer--md);
  border-radius: 3px; border: 1px solid;
}
.pf-v6-c-alert.pf-m-warning.pf-m-inline { background: #fdf7e7; border-color: #f0ab00; color: #795600; }
.pf-v6-theme-dark .pf-v6-c-alert.pf-m-warning.pf-m-inline { background: #3d2c00; border-color: #f0ab00; color: #f0ab00; }
.pf-v6-c-alert__icon { font-weight: bold; flex-shrink: 0; line-height: 1.5; }
.pf-v6-c-alert__title { font-weight: var(--pf-t--global--font--weight--bold); font-size: var(--pf-t--global--font--size--sm); margin: 0; }

.pf-v6-c-text-input-group {
  display: flex; align-items: center;
  background: var(--pf-t--global--background--color--primary--default);
  border: 1px solid var(--pf-t--global--border--color--default); border-radius: 3px;
}
.pf-v6-c-text-input-group__main { display: flex; flex: 1; }
.pf-v6-c-text-input-group__text { display: flex; flex: 1; align-items: center; }
.pf-v6-c-text-input-group__text-input {
  flex: 1; border: none; outline: none; background: transparent;
  padding: 3px 8px; font-size: 12px;
  color: var(--pf-t--global--text--color--regular); min-width: 140px;
}

.pf-v6-screen-reader {
  position: absolute; width: 1px; height: 1px; padding: 0;
  overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0;
}

/* ── Layout ── */
.masthead-meta { font-size: 12px; color: var(--pf-t--global--text--color--on-dark--subtle); }
.masthead-end {
  display: flex; align-items: center; gap: 8px;
  justify-content: flex-end; width: 100%;
}
.warn-wrapper { padding: 6px 12px 0; }
.warn-wrapper + .warn-wrapper { padding-top: 2px; }

/* Compact server info bar below tabs */
.server-info-bar {
  display: flex; align-items: center; gap: 8px;
  padding: 4px 12px;
  background: var(--pf-t--global--background--color--secondary--default);
  border-bottom: 1px solid var(--pf-t--global--border--color--default);
  min-height: 28px; flex-wrap: wrap;
}
.server-hint { font-size: 12px; color: var(--pf-t--global--text--color--subtle); font-style: italic; }
.server-meta-info { font-size: 12px; color: var(--pf-t--global--text--color--subtle); margin-left: auto; }
.catalog-main { padding: 10px 12px; }

/* Scrollable tool list — fixed px cap so only one scrollbar exists */
.tool-list-container {
  background: var(--pf-t--global--background--color--primary--default);
  border: 1px solid var(--pf-t--global--border--color--default);
  border-radius: 6px;
  max-height: 300px;
  overflow-y: auto;
  overflow-x: hidden;
}

/* Server/tool row elements */
.server-prefix {
  font-family: var(--pf-t--global--font--family--mono);
  font-size: 11px; color: var(--pf-t--global--text--color--subtle);
  background: var(--pf-t--global--background--color--primary--default);
  padding: 1px 4px; border-radius: 3px;
  border: 1px solid var(--pf-t--global--border--color--default);
}
.status-dot {
  width: 7px; height: 7px; border-radius: 50%;
  flex-shrink: 0; display: inline-block;
}
.status-dot--success { background: var(--pf-t--global--icon--color--status--success--default); }
.status-dot--danger  { background: var(--pf-t--global--icon--color--status--danger--default); }
.status-dot--unknown { background: var(--pf-t--global--text--color--subtle); }
.tool-row {
  display: flex; align-items: baseline; gap: 12px;
  padding: 5px 12px; position: relative; cursor: pointer;
  border-bottom: 1px solid var(--pf-t--global--border--color--default);
}
.tool-row:last-child { border-bottom: none; }
.tool-row.hidden { display: none; }
.tool-row.is-expanded { background: var(--pf-t--global--background--color--secondary--default); }
.tool-chevron { font-size: 10px; color: var(--pf-t--global--text--color--subtle); width: 12px; flex-shrink: 0; }
.tool-name {
  font-family: var(--pf-t--global--font--family--mono);
  font-size: 13px; color: var(--pf-t--global--color--blue--40);
  min-width: 200px; flex-shrink: 0;
}
.tool-desc { font-size: 12px; color: var(--pf-t--global--text--color--subtle); flex: 1; }
.copy-btn {
  opacity: 0; border: none; background: transparent; cursor: pointer;
  font-size: 11px; padding: 1px 4px; border-radius: 3px;
  color: var(--pf-t--global--text--color--subtle);
  transition: opacity 0.15s; flex-shrink: 0;
}
.copy-btn.copied { color: var(--pf-t--global--icon--color--status--success--default); }
.tool-row:hover .copy-btn { opacity: 1; }
.tool-detail {
  padding: 8px 12px 8px 36px;
  border-bottom: 1px solid var(--pf-t--global--border--color--default);
  background: var(--pf-t--global--background--color--secondary--default);
  font-size: 12px;
}
.tool-detail.hidden { display: none; }
.detail-desc { color: var(--pf-t--global--text--color--subtle); margin-bottom: 6px; }
.detail-params { display: flex; flex-direction: column; gap: 3px; }
.detail-param { display: flex; gap: 8px; align-items: baseline; }
.param-name { font-family: var(--pf-t--global--font--family--mono); font-size: 12px; color: var(--pf-t--global--color--blue--40); }
.param-type { font-size: 11px; color: var(--pf-t--global--text--color--subtle); }
.param-required { font-size: 10px; font-weight: bold; color: #c9190b; }
.param-desc { font-size: 11px; color: var(--pf-t--global--text--color--subtle); }
.category-chips {
  display: flex; flex-wrap: wrap; gap: 6px;
  padding: 6px 12px;
  border-bottom: 1px solid var(--pf-t--global--border--color--default);
}
.category-chips:empty { display: none; }
.chip {
  display: inline-flex; align-items: center;
  padding: 2px 10px; border-radius: 30px;
  font-size: 11px; font-weight: 600; cursor: pointer;
  border: 1px solid var(--pf-t--global--border--color--default);
  background: transparent; color: var(--pf-t--global--text--color--subtle);
  transition: all 0.1s;
}
.chip.active {
  background: var(--pf-t--global--color--blue--40);
  border-color: var(--pf-t--global--color--blue--40); color: #fff;
}
.no-tools {
  padding: 8px 12px; font-size: 12px;
  color: var(--pf-t--global--text--color--subtle); font-style: italic;
}
.catalog-loading { padding: 32px; text-align: center; color: var(--pf-t--global--text--color--subtle); font-size: 13px; }
</style>
</head>
<body>
<header class="pf-v6-c-masthead" role="banner">
  <div class="pf-v6-c-masthead__main">
    <div class="pf-v6-c-masthead__brand">
      <span style="font-size:var(--pf-t--global--font--size--lg);font-weight:var(--pf-t--global--font--weight--bold);color:var(--pf-t--global--text--color--on-dark--regular);">MCP Gateway Tool Catalog</span>
    </div>
  </div>
  <div class="pf-v6-c-masthead__content">
    <div class="masthead-end">
      <span id="meta" class="masthead-meta" aria-live="polite">Connecting…</span>
      <div class="pf-v6-c-text-input-group" role="search">
        <div class="pf-v6-c-text-input-group__main">
          <span class="pf-v6-c-text-input-group__text">
            <input class="pf-v6-c-text-input-group__text-input"
                   type="search"
                   placeholder="Search tools…"
                   aria-label="Search tools"
                   oninput="filterTools(this.value)">
          </span>
        </div>
      </div>
      <button class="pf-v6-c-button pf-m-secondary" type="button" onclick="refresh()">Refresh</button>
    </div>
  </div>
</header>
<div id="warn" aria-live="polite"></div>
<div class="pf-v6-c-tabs" id="server-tabs"></div>
<div class="server-info-bar" id="server-info" aria-live="polite"></div>
<div id="category-chips" class="category-chips"></div>
<main class="catalog-main" id="main" role="tabpanel" aria-label="Tool list">
  <div class="tool-list-container" id="tool-list">
    <div class="catalog-loading">Loading catalog…</div>
  </div>
</main>
<script type="module">
fetch("https://unpkg.com/@patternfly/patternfly@6/patternfly.min.css")
  .then(r => r.ok ? r.text() : Promise.reject(r.status))
  .then(css => {
    const s = document.createElement("style");
    s.textContent = css;
    const firstStyle = document.head.querySelector("style");
    document.head.insertBefore(s, firstStyle);
  })
  .catch(() => {});

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
    if (ctx?.theme === "dark") document.documentElement.classList.add("pf-v6-theme-dark");
    else document.documentElement.classList.remove("pf-v6-theme-dark");
  };

  window.mcpApp = app;
  app.connect();
}).catch(err => {
  const listEl = document.getElementById("tool-list");
  listEl.textContent = "";
  const d = document.createElement("div");
  d.className = "catalog-loading";
  d.textContent = "Failed to load MCP Apps SDK: " + err.message;
  listEl.appendChild(d);
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

function makeAlert(message) {
  const wrapper = el("div", "warn-wrapper");
  const alert = el("div", "pf-v6-c-alert pf-m-warning pf-m-inline");
  alert.setAttribute("role", "alert");
  const icon = el("div", "pf-v6-c-alert__icon");
  icon.setAttribute("aria-hidden", "true");
  icon.textContent = "!";
  const title = el("p", "pf-v6-c-alert__title");
  const srText = el("span", "pf-v6-screen-reader", "Warning: ");
  title.appendChild(srText);
  title.appendChild(document.createTextNode(message));
  alert.appendChild(icon);
  alert.appendChild(title);
  wrapper.appendChild(alert);
  return wrapper;
}

let allServers = [], catalogData = {}, currentIdx = 0, activeChip = null;

function buildTabs() {
  const tabsEl = document.getElementById("server-tabs");
  tabsEl.textContent = "";
  if (!allServers.length) return;

  const ul = el("ul", "pf-v6-c-tabs__list");
  ul.setAttribute("role", "tablist");
  ul.setAttribute("aria-label", "MCP servers");

  allServers.forEach((srv, i) => {
    const li = el("li", "pf-v6-c-tabs__item");
    li.setAttribute("role", "presentation");
    const btn = el("button", "pf-v6-c-tabs__link");
    btn.setAttribute("role", "tab");
    btn.setAttribute("id", "tab-" + i);
    btn.setAttribute("aria-selected", "false");
    btn.setAttribute("aria-controls", "main");
    btn.setAttribute("tabindex", "-1");
    btn.onclick = () => switchServer(i);
    btn.appendChild(el("span", "pf-v6-c-tabs__item-text", srv.name));
    if (srv.toolCount) {
      const badge = el("span", "pf-v6-c-badge", String(srv.toolCount));
      badge.setAttribute("aria-label", srv.toolCount + " tools");
      btn.appendChild(badge);
    }
    li.appendChild(btn);
    ul.appendChild(li);
  });

  tabsEl.appendChild(ul);
}

function switchServer(idx) {
  currentIdx = idx;
  const srv = allServers[idx];
  if (!srv) return;

  document.querySelectorAll(".pf-v6-c-tabs__item").forEach((li, i) => {
    li.classList.toggle("pf-m-current", i === idx);
  });
  document.querySelectorAll(".pf-v6-c-tabs__link").forEach((btn, i) => {
    btn.setAttribute("aria-selected", i === idx ? "true" : "false");
    btn.setAttribute("tabindex", i === idx ? "0" : "-1");
  });

  const infoEl = document.getElementById("server-info");
  infoEl.textContent = "";

  const isDisabled = srv.state === "Disabled";
  if (srv.state) {
    const lbl = el("span", "pf-v6-c-label" + (!isDisabled ? " pf-m-green" : ""));
    const lc = el("span", "pf-v6-c-label__content");
    lc.appendChild(el("span", "pf-v6-c-label__text", srv.state));
    lbl.appendChild(lc);
    infoEl.appendChild(lbl);
  }

  const dotCls = !catalogData.brokerOK ? "status-dot status-dot--unknown"
               : srv.isReachable ? "status-dot status-dot--success"
               : "status-dot status-dot--danger";
  const dot = el("span", dotCls);
  dot.title = !catalogData.brokerOK ? "Status unknown" : srv.isReachable ? "Connected" : "Unreachable";
  dot.setAttribute("aria-hidden", "true");
  infoEl.appendChild(dot);

  if (srv.prefix) infoEl.appendChild(el("span", "server-prefix", srv.prefix));
  if (srv.hint)   infoEl.appendChild(el("span", "server-hint", srv.hint));

  const srvCats = srv.categories || [];
  infoEl.appendChild(el("span", "server-meta-info",
    (srv.toolCount || 0) + " tools" + (srvCats.length ? " · " + srvCats.join(", ") : "")));

  // Category chips
  const chipsEl = document.getElementById("category-chips");
  chipsEl.textContent = "";
  activeChip = null;
  const cats = srvCats;
  if (cats.length > 0) {
    cats.forEach(cat => {
      const chip = el("button", "chip", cat);
      chip.onclick = () => {
        if (activeChip === cat) {
          activeChip = null;
          chip.classList.remove("active");
          filterByCategory(null);
        } else {
          chipsEl.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
          activeChip = cat;
          chip.classList.add("active");
          filterByCategory(cat);
        }
      };
      chipsEl.appendChild(chip);
    });
  }

  const listEl = document.getElementById("tool-list");
  listEl.textContent = "";

  if (srv.tools && srv.tools.length) {
    srv.tools.forEach(t => {
      const row = el("div", "tool-row");
      row.dataset.tool = "";

      const chevron = el("span", "tool-chevron", "▶");
      row.appendChild(chevron);
      row.appendChild(el("span", "tool-name", t.federatedName));

      const copyBtn = el("button", "copy-btn", "⎘");
      copyBtn.title = "Copy tool name";
      copyBtn.onclick = (e) => {
        e.stopPropagation();
        navigator.clipboard.writeText(t.federatedName).then(() => {
          copyBtn.textContent = "✓";
          copyBtn.classList.add("copied");
          setTimeout(() => { copyBtn.textContent = "⎘"; copyBtn.classList.remove("copied"); }, 1500);
        }).catch(() => {});
      };
      row.appendChild(copyBtn);

      const detail = el("div", "tool-detail hidden");
      const schema = t.inputSchema || {};
      const props = schema.properties || {};
      const required = schema.required || [];
      const propKeys = Object.keys(props);
      if (t.description) detail.appendChild(el("div", "detail-desc", t.description));
      if (propKeys.length) {
        const params = el("div", "detail-params");
        propKeys.forEach(k => {
          const p = props[k];
          const prow = el("div", "detail-param");
          prow.appendChild(el("span", "param-name", k));
          prow.appendChild(el("span", "param-type", p.type || "any"));
          if (required.includes(k)) prow.appendChild(el("span", "param-required", "required"));
          if (p.description) prow.appendChild(el("span", "param-desc", p.description));
          params.appendChild(prow);
        });
        detail.appendChild(params);
      }
      if (!t.description && !propKeys.length) detail.appendChild(el("div", "detail-desc", "No description available."));

      row.onclick = () => {
        const open = detail.classList.toggle("hidden") === false;
        row.classList.toggle("is-expanded", open);
        chevron.textContent = open ? "▼" : "▶";
      };

      listEl.appendChild(row);
      listEl.appendChild(detail);
    });
  } else {
    listEl.appendChild(el("div", "no-tools",
      "No tools available" + (!catalogData.brokerOK ? " (broker offline)" : "")));
  }

  const search = document.querySelector(".pf-v6-c-text-input-group__text-input");
  if (search?.value) filterTools(search.value);
}
window.switchServer = switchServer;

function render(data) {
  catalogData = data;
  allServers = data.servers || [];
  currentIdx = 0;

  document.getElementById("meta").textContent =
    (allServers.length || 0) + " servers · " + (data.totalTools || 0) + " tools · " + (data.generatedAt || "");

  const warnEl = document.getElementById("warn");
  warnEl.textContent = "";
  if (!data.brokerOK) warnEl.appendChild(makeAlert("Broker unreachable — showing Kubernetes data only."));
  if (data.noK8sData) warnEl.appendChild(makeAlert("No MCPServerRegistrations found — showing broker data only."));

  buildTabs();

  if (!allServers.length) {
    document.getElementById("server-info").textContent = "";
    const listEl = document.getElementById("tool-list");
    listEl.textContent = "";
    listEl.appendChild(el("div", "catalog-loading", "No servers found."));
  } else {
    switchServer(0);
  }
}
window.render = render;

function filterTools(query) {
  const q = query.toLowerCase();
  // Reset category chip when search is active
  if (q) {
    activeChip = null;
    document.querySelectorAll("#category-chips .chip").forEach(c => c.classList.remove("active"));
  }
  document.querySelectorAll("#tool-list .tool-row").forEach(row => {
    const hide = q !== "" && !row.textContent.toLowerCase().includes(q);
    row.classList.toggle("hidden", hide);
    const next = row.nextElementSibling;
    if (next && next.classList.contains("tool-detail") && hide) next.classList.add("hidden");
  });
}
window.filterTools = filterTools;

function filterByCategory(cat) {
  document.querySelectorAll("#tool-list .tool-row").forEach(row => {
    if (!cat) { row.classList.remove("hidden"); return; }
    row.classList.toggle("hidden", row.textContent.toLowerCase().indexOf(cat.toLowerCase()) === -1);
  });
}
window.filterByCategory = filterByCategory;
</script>
</body>
</html>"""


def _fetch_broker_tools(broker_url: str, http) -> list:
    """Returns flat list of all federated tools with descriptions + inputSchema.

    Tries tools/list first (standard MCP); falls back to the broker's
    discover_tools custom tool if tools/list returns nothing (older brokers
    that don't expose federated tools via the standard method).
    """
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
            return []
        sh = {**hdrs, "Mcp-Session-Id": session_id}
        http.post(base, json={"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
                  timeout=5, headers=sh)

        # Try tools/list (standard MCP — works when broker exposes federated tools)
        all_tools = []
        cursor = None
        req_id = 2
        while True:
            params = {"cursor": cursor} if cursor else {}
            r2 = http.post(base, json={
                "jsonrpc": "2.0", "id": req_id, "method": "tools/list",
                "params": params,
            }, timeout=10, headers=sh)
            r2.raise_for_status()
            result = r2.json().get("result", {})
            for t in result.get("tools", []):
                all_tools.append({
                    "federatedName": t["name"],
                    "description": t.get("description", ""),
                    "inputSchema": t.get("inputSchema", {}),
                })
            cursor = result.get("nextCursor")
            if not cursor:
                break
            req_id += 1

        if all_tools:
            return all_tools

        # Fallback: broker's discover_tools (returns grouped-by-server tool names)
        r3 = http.post(base, json={
            "jsonrpc": "2.0", "id": req_id + 1, "method": "tools/call",
            "params": {"name": "discover_tools", "arguments": {}},
        }, timeout=10, headers=sh)
        r3.raise_for_status()
        text = r3.json().get("result", {}).get("content", [{}])[0].get("text", "{}")
        for srv in json.loads(text).get("servers", []):
            for t in srv.get("tools", []):
                all_tools.append({"federatedName": t, "description": "", "inputSchema": {}})
        return all_tools
    except Exception:
        return []


def register(mcp: FastMCP, srv) -> None:
    @mcp.resource(
        CATALOG_RESOURCE_URI,
        name="MCP Gateway Tool Catalog",
        description="Interactive catalog UI for all federated MCP tools",
        app=AppConfig(csp=ResourceCSP(
            resource_domains=["https://unpkg.com"],
            connect_domains=["https://unpkg.com"],
        )),
    )
    def catalog_ui() -> str:
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

        # 3. Fetch per-server tool lists from broker (tools/list with descriptions + inputSchema)
        broker_tools = _fetch_broker_tools(srv.broker_url, srv.http) if broker_ok else []

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
            prefix = getattr(spec, "prefix", "") or name
            server_tools = [t for t in broker_tools if t["federatedName"].startswith(prefix)]
            cs = {
                "name": name,
                "prefix": getattr(spec, "prefix", "") or "",
                "state": str(getattr(spec, "state", "") or ""),
                "categories": list(getattr(spec, "category", None) or []),
                "hint": getattr(spec, "hint", "") or "",
                "isReachable": is_reachable,
                "toolCount": tool_count,
                "tools": server_tools,
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
                server_tools = [t for t in broker_tools if t["federatedName"].startswith(short)]
                servers.append({
                    "name": short,
                    "prefix": "", "state": "", "categories": [], "hint": "",
                    "isReachable": bool(bs.get("ready", False)),
                    "toolCount": tool_count,
                    "tools": server_tools,
                })
                total_tools += tool_count

        data = {
            "servers": servers,
            "totalTools": total_tools,
            "generatedAt": datetime.now().strftime("%H:%M:%S"),
            "brokerOK": broker_ok,
            "noK8sData": no_k8s_data,
        }
        ui_meta = {"ui": {"resourceUri": CATALOG_RESOURCE_URI}}
        ui_supported = ctx.client_supports_extension(UI_EXTENSION_ID)
        if ui_supported:
            return ToolResult(
                content=f"Tool catalog rendered: {len(servers)} servers, {total_tools} tools.",
                structured_content=data,
                meta=ui_meta,
            )
        return ToolResult(
            content=json.dumps(data),
            structured_content=data,
            meta=ui_meta,
        )
