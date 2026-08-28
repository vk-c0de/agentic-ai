"""LangChain agent for e-commerce support."""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import Tool, initialize_agent, AgentType
from langchain_bot.rag_tool import search_policies

load_dotenv()

# Module-level cache
_agent = None


def create_support_agent():
    """Create the main e-commerce support agent with tools."""
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Wrap the tool function
    tools = [
        Tool(
            name="search_policies",
            func=lambda query: search_policies.invoke({"query": query}),
            description="Search policy documents for information about returns, shipping, FAQs, and company policies"
        )
    ]
    
    # Create agent with conversational capability
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=False,
        handle_parsing_errors=True,
        max_iterations=5,
        memory=None  # We'll handle memory through session state
    )
    
    return agent


def get_agent():
    """Get or create the singleton agent instance."""
    global _agent
    if _agent is None:
        _agent = create_support_agent()
    return _agent


__all__ = ["create_support_agent", "get_agent"]
