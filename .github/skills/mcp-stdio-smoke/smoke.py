"""Spawn mcp_server.py over stdio (run from the repo root) and call its tools; speaks one line."""
import asyncio, os, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(command=sys.executable, args=["mcp_server.py"], env=dict(os.environ), cwd=os.getcwd())
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            print("tools:", sorted(t.name for t in (await s.list_tools()).tools))
            print("voices:", (await s.call_tool("list_voices", {})).content[0].text[:200])
            print("claim:", (await s.call_tool("claim_voice", {"agent": "smoke"})).content[0].text[:200])
            print("speak:", (await s.call_tool("speak", {"text": "Stdio works.", "agent": "smoke"})).content[0].text)
asyncio.run(main())
