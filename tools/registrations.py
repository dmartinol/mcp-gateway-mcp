import json
from typing import Literal
from fastmcp import FastMCP
from kubernetes.dynamic.exceptions import ResourceNotFoundError


def register(mcp: FastMCP, srv) -> None:
    @mcp.tool(description="List all MCPServerRegistration resources")
    def list_registrations(namespace: str = "") -> str:
        ns = namespace or srv.namespace
        try:
            resource = srv.dyn_client.resources.get(
                api_version="mcp.kuadrant.io/v1alpha1",
                kind="MCPServerRegistration",
            )
            items = resource.list(namespace=ns).items
            summaries = [
                {
                    "name": item.metadata.name,
                    "namespace": item.metadata.namespace,
                    "prefix": getattr(item.spec, "prefix", "") or "",
                    "state": str(getattr(item.spec, "state", "") or ""),
                    "discoveredTools": int(getattr(item.status, "discoveredTools", 0) or 0),
                    "ready": any(
                        c.type == "Ready" and c.status == "True"
                        for c in (getattr(item.status, "conditions", None) or [])
                    ),
                    "categories": list(getattr(item.spec, "category", None) or []),
                    "targetRef": getattr(getattr(item.spec, "targetRef", None), "name", "") or "",
                }
                for item in items
            ]
            return json.dumps(summaries)
        except Exception as e:
            return f"error: {e}"

    @mcp.tool(description="Get details of a specific MCPServerRegistration")
    def get_registration(name: str, namespace: str = "") -> str:
        ns = namespace or srv.namespace
        try:
            resource = srv.dyn_client.resources.get(
                api_version="mcp.kuadrant.io/v1alpha1",
                kind="MCPServerRegistration",
            )
            item = resource.get(name=name, namespace=ns)
            detail = {
                "name": item.metadata.name,
                "namespace": item.metadata.namespace,
                "prefix": getattr(item.spec, "prefix", "") or "",
                "state": str(getattr(item.spec, "state", "") or ""),
                "discoveredTools": int(getattr(item.status, "discoveredTools", 0) or 0),
                "ready": any(
                    c.type == "Ready" and c.status == "True"
                    for c in (getattr(item.status, "conditions", None) or [])
                ),
                "categories": list(getattr(item.spec, "category", None) or []),
                "targetRef": getattr(getattr(item.spec, "targetRef", None), "name", "") or "",
                "path": getattr(item.spec, "path", "") or "",
                "hint": getattr(item.spec, "hint", "") or "",
                "tags": list(getattr(item.spec, "tags", None) or []),
                "credentialRef": getattr(getattr(item.spec, "credentialRef", None), "name", "") or "",
                "userSpecificList": str(getattr(item.spec, "userSpecificList", "") or ""),
                "conditions": [
                    {
                        "type": c.type,
                        "status": c.status,
                        "reason": getattr(c, "reason", ""),
                        "message": getattr(c, "message", ""),
                    }
                    for c in (getattr(item.status, "conditions", None) or [])
                ],
            }
            return json.dumps(detail)
        except Exception as e:
            return f"error: {e}"

    @mcp.tool(description="Enable or disable an MCPServerRegistration")
    def update_registration_state(name: str, state: Literal["Enabled", "Disabled"], namespace: str = "") -> str:
        ns = namespace or srv.namespace
        try:
            resource = srv.dyn_client.resources.get(
                api_version="mcp.kuadrant.io/v1alpha1",
                kind="MCPServerRegistration",
            )
            resource.patch(
                body={"spec": {"state": state}},
                name=name,
                namespace=ns,
                content_type="application/merge-patch+json",
            )
            return json.dumps({
                "name": name,
                "state": state,
                "message": f"registration '{name}' state set to {state}",
            })
        except Exception as e:
            return f"error: {e}"
