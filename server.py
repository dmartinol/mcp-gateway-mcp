import os
import argparse
import logging
import requests

logging.basicConfig(level=logging.WARNING, format="%(message)s")

import sys
from kubernetes import config as k8s_config, dynamic
from kubernetes.client import api_client
from fastmcp import FastMCP


class AdminServer:
    def __init__(self, dyn_client, namespace: str, broker_url: str):
        self.dyn_client = dyn_client   # kubernetes.dynamic.DynamicClient
        self.namespace = namespace
        self.broker_url = broker_url
        self.http = requests.Session()


def main():
    parser = argparse.ArgumentParser(description="MCP Gateway Admin Server")
    parser.add_argument("--kubeconfig", default=os.environ.get("KUBECONFIG"))
    parser.add_argument("--namespace", default=os.environ.get("MCP_ADMIN_NAMESPACE", "mcp-servers"))
    parser.add_argument("--broker-url", default=os.environ.get("MCP_BROKER_URL", "http://localhost:8080"))
    parser.add_argument("--transport", default=os.environ.get("MCP_ADMIN_TRANSPORT", "stdio"))
    parser.add_argument("--addr", default=os.environ.get("MCP_ADMIN_ADDR", ":8899"))
    args = parser.parse_args()

    if args.kubeconfig:
        k8s_config.load_kube_config(config_file=args.kubeconfig)
    else:
        try:
            k8s_config.load_incluster_config()
        except k8s_config.ConfigException:
            k8s_config.load_kube_config()

    dyn_client = dynamic.DynamicClient(api_client.ApiClient())
    admin = AdminServer(dyn_client, args.namespace, args.broker_url)

    mcp = FastMCP("mcp-gateway-admin")

    # Intercept initialize to log client capabilities
    from mcp.types import InitializeRequest
    _orig_init_handler = mcp._mcp_server.request_handlers.get(InitializeRequest)
    if _orig_init_handler:
        async def _logged_init(req):
            caps = req.params.capabilities
            exts = getattr(caps, "extensions", None) or {}
            print(f"[INIT] client={req.params.clientInfo.name} extensions={list(exts.keys())}", file=sys.stderr, flush=True)
            return await _orig_init_handler(req)
        mcp._mcp_server.request_handlers[InitializeRequest] = _logged_init

    from tools import registrations, virtual_servers, gateway_status, tool_catalog
    registrations.register(mcp, admin)
    virtual_servers.register(mcp, admin)
    gateway_status.register(mcp, admin)
    tool_catalog.register(mcp, admin)

    if args.transport == "http":
        import json as _json
        from starlette.middleware.base import BaseHTTPMiddleware

        class LogRequests(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                if request.method == "POST":
                    body = await request.body()
                    try:
                        msg = _json.loads(body)
                        method = msg.get("method", "?") if isinstance(msg, dict) else [m.get("method") for m in msg]
                        print(f"[MCP] {method}", file=sys.stderr, flush=True)
                    except Exception:
                        pass
                    from starlette.requests import Request
                    request._body = body
                return await call_next(request)

        from starlette.middleware.cors import CORSMiddleware
        app_http = mcp.http_app(transport="http")
        app_http.add_middleware(LogRequests)
        app_http.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["Mcp-Session-Id"],
        )
        import uvicorn
        host = "0.0.0.0"
        port = 8899
        addr = args.addr
        if addr.startswith(":"):
            host = "0.0.0.0"
            port = int(addr[1:])
        else:
            parts = addr.rsplit(":", 1)
            host = parts[0]
            port = int(parts[1])
        uvicorn.run(app_http, host=host, port=port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
