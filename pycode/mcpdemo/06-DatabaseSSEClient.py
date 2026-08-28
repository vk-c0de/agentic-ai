from mcp import Client
from mcp.client.sse import sse_client
import asyncio

async def run():
    # Connect over SSE and hand the transport to Client
    async with Client(sse_client("http://localhost:8000/sse")) as client:
        tools = await client.list_tools()
        print("Available tools:", [tool.name for tool in tools.tools])

        db_path = "c:\\database\\fintech.db"

        tables = await client.call_tool("list_tables", {"db_path": db_path})
        print("Tables in database:", tables.structured_content)

        schema = await client.call_tool("get_table_schema", {
            "db_path": db_path,
            "table_name": "customers"
        })
        print("Table schema for users:", schema.structured_content)

        results = await client.call_tool("execute_query", {
            "db_path": db_path,
            "query": "SELECT * FROM users LIMIT 5"
        })
        print("First 5 customers:", results.structured_content)

if __name__ == "__main__":
    asyncio.run(run())