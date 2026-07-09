import requests
from fastmcp import FastMCP


def register(mcp: FastMCP, srv) -> None:
    @mcp.tool()
    def get_gateway_status() -> str:
        """Get the live status of the MCP gateway broker (upstream connectivity, tool counts, conflicts)"""
        try:
            resp = srv.http.get(srv.broker_url + "/status", timeout=10)
        except requests.RequestException as e:
            return f"error: broker unreachable: {e}"
        if resp.status_code >= 400:
            return f"error: broker returned {resp.status_code}: {resp.text}"
        return resp.text
