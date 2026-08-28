import httpx2
from mcp import Client
from mcp.client.streamable_http import streamable_http_client
import asyncio


async def run():
    async with httpx2.AsyncClient(
        headers={"Authorization": "Bearer ..."},
        timeout=httpx2.Timeout(30.0, read=300.0),
        follow_redirects=True,
    ) as http_client:
        transport = streamable_http_client(
            "http://localhost:8001/mcp",
            http_client=http_client,
        )
        async with Client(transport) as client:
            tools = await client.list_tools()
            print([tool.name for tool in tools.tools])


if __name__ == "__main__":
    asyncio.run(run())