from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
import asyncio
import os

# Ensure you have OPENAI_API_KEY set in your environment
# os.environ["OPENAI_API_KEY"] = "your-api-key-here"


async def main():
    # Create a MultiServerMCPClient with the Database Server
    client = MultiServerMCPClient(
        {
            "database": {
                "transport": "stdio",  # Local subprocess communication
                # Must be mcpvenv Python so the server runs with the current MCP SDK
                "command": r"C:\Users\localadmin\Desktop\vijay\pycode\mcpvenv\Scripts\python.exe",
                # Update with the absolute path to your DatabaseServer script
                "args": ["C:\\Users\\localadmin\\Desktop\\vijay\\pycode\\mcpdemo\\03-DatabaseServer.py"],
            }
        }
    )

    # Get tools from the MCP server
    tools = await client.get_tools()
    print(f"Available tools: {[tool.name for tool in tools]}")

    # Create a LangChain agent using create_agent with gpt-4o-mini
    agent = create_agent(
        "openai:gpt-4o-mini",  # Model specification
        tools  # MCP tools
    )

    # Example query: list all tables
    print("\n" + "="*80)
    print("List all tables in the fintech database")
    print("="*80)
    result = await agent.ainvoke({
        "messages": [{"role": "user", "content": "List all tables in the database located at c:\\database\\fintech.db"}]
    })
    print(f"\nResult: {result['messages'][-1].content}\n")


if __name__ == "__main__":
    asyncio.run(main())