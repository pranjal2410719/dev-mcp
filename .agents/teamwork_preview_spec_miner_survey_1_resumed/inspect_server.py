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
    print(f"=== TOTAL TOOLS: {len(tools)} ===")
    for t in sorted(tools, key=lambda x: x.name):
        props = list(t.parameters.get("properties", {}).keys()) if hasattr(t, "parameters") and t.parameters else []
        required = t.parameters.get("required", []) if hasattr(t, "parameters") and t.parameters else []
        desc = (t.description or "").split("\n")[0]
        print(f"TOOL|{t.name}|{props}|{required}|{desc}")

    resources = await mcp.list_resources()
    print(f"\n=== TOTAL RESOURCES: {len(resources)} ===")
    for res in sorted(resources, key=lambda x: str(x.uri)):
        print(f"RESOURCE|{res.uri}|{res.name}|{res.description or ''}")

    prompts = await mcp.list_prompts()
    print(f"\n=== TOTAL PROMPTS: {len(prompts)} ===")
    for pr in sorted(prompts, key=lambda x: x.name):
        print(f"PROMPT|{pr.name}|{pr.description or ''}")

if __name__ == "__main__":
    asyncio.run(main())
