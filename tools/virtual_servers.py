import json
from fastmcp import FastMCP


def register(mcp: FastMCP, srv) -> None:
    @mcp.tool()
    def list_virtual_servers(namespace: str = "") -> str:
        """List all MCPVirtualServer resources"""
        ns = namespace or srv.namespace
        try:
            resource = srv.dyn_client.resources.get(
                api_version="mcp.kuadrant.io/v1alpha1", kind="MCPVirtualServer"
            )
            items = resource.get(namespace=ns)
        except Exception:
            return json.dumps([])
        summaries = [
            {
                "name": item.metadata.name,
                "namespace": item.metadata.namespace,
                "toolCount": len(getattr(item.spec, "tools", None) or []),
                "tools": list(getattr(item.spec, "tools", None) or []),
            }
            for item in items.items
        ]
        return json.dumps(summaries)

    @mcp.tool()
    def get_virtual_server(name: str, namespace: str = "") -> str:
        """Get details of a specific MCPVirtualServer"""
        ns = namespace or srv.namespace
        try:
            resource = srv.dyn_client.resources.get(
                api_version="mcp.kuadrant.io/v1alpha1", kind="MCPVirtualServer"
            )
            item = resource.get(name=name, namespace=ns)
        except Exception as e:
            return json.dumps({"error": str(e), "name": name})
        detail = {
            "name": item.metadata.name,
            "namespace": item.metadata.namespace,
            "toolCount": len(getattr(item.spec, "tools", None) or []),
            "tools": list(getattr(item.spec, "tools", None) or []),
            "description": str(getattr(item.spec, "description", "") or ""),
            "prompts": list(getattr(item.spec, "prompts", None) or []),
        }
        return json.dumps(detail)
