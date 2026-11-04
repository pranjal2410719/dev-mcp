import sys
from pathlib import Path
project_root = Path("/home/dev/Desktop/projects/mcp/dev-mcp")
sys.path.insert(0, str(project_root))

import asyncio
import json
import server
from app import mcp

async def main():
    tools = await mcp.list_tools()
    out = {
        "server_name": mcp.name,
        "tool_count": len(tools),
        "tools": {},
        "resource_count": 0,
        "resources": {},
        "prompt_count": 0,
        "prompts": {}
    }
    for t in tools:
        props = t.parameters.get("properties", {}) if hasattr(t, "parameters") and t.parameters else {}
        required = t.parameters.get("required", []) if hasattr(t, "parameters") and t.parameters else []
        param_details = {}
        for p_name, p_info in props.items():
            param_details[p_name] = {
                "type": p_info.get("type", "any"),
                "description": p_info.get("description", ""),
                "default": p_info.get("default", None),
                "required": p_name in required
            }
        out["tools"][t.name] = {
            "description": t.description or "",
            "parameters": param_details
        }

    resources = await mcp.list_resources()
    out["resource_count"] = len(resources)
    for res in resources:
        out["resources"][str(res.uri)] = {
            "name": res.name,
            "description": res.description or "",
            "mimeType": getattr(res, "mimeType", None)
        }

    prompts = await mcp.list_prompts()
    out["prompt_count"] = len(prompts)
    for pr in prompts:
        out["prompts"][pr.name] = {
            "description": pr.description or "",
            "arguments": [
                {"name": a.name, "description": a.description, "required": a.required}
                for a in (pr.arguments or [])
            ]
        }

    with open("/home/dev/Desktop/projects/mcp/dev-mcp/.agents/teamwork_preview_spec_miner_survey_1_resumed/mcp_catalog.json", "w") as f:
        json.dump(out, f, indent=2)

    print(f"Dumped {len(tools)} tools, {len(resources)} resources, {len(prompts)} prompts to mcp_catalog.json")

if __name__ == "__main__":
    asyncio.run(main())
