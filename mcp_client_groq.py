from langchain_groq import ChatGroq
from contextlib import asynccontextmanager
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
import asyncio
import os
import logging

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


if os.getenv('GROQ_API_KEY'):
    llm = ChatGroq(
        model="qwen-qwq-32b",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    print("Using Groq with Qwen-qwq-32b")
else:
    print('Export GROQ_API_KEY to initialize Qwen LLM.')
    print('Get your API key from: https://console.groq.com/')
    exit(1)

@asynccontextmanager
async def main():
    client = MultiServerMCPClient({
        "pokemon_server": {
            "url": os.getenv("POKEMON_MCP_URL", "http://localhost:8000/sse"),
            "transport": "sse"
        }
    })
    
    tools = await client.get_tools()
    
    # Filter tools to include only Pokémon-related tools
    # pokemon_tools = [tool for tool in tools if tool.name in [
    #     "get_pokemon", 
    #     "compare_pokemon", 
    #     "get_type_matchups", 
    #     "suggest_team"
    # ]]
    
    print("Loaded Pokémon MCP tools: " + ", ".join(tool.name for tool in tools))
    
    agent = create_react_agent(
        llm,
        tools=tools,
        prompt="""You are a Pokémon expert assistant. You have access to tools that can:
        - Get detailed information about any Pokémon
        - Compare two Pokémon's attributes  
        - Analyze type matchups and strategies
        - Suggest balanced team compositions

        Use these tools to provide comprehensive and helpful responses about Pokémon.
        Always use the available tools when you need information about specific Pokémon."""
    )
    
    yield agent

async def invoke_agent(query):
    async with main() as agent:
        agent_response = await agent.ainvoke({"messages": query})
        print("==== Final Answer ====")
        print(agent_response['messages'][-1].content)

if __name__ == "__main__":
    # Example queries for different functionalities
    queries = [
        "Tell me about Charizard",
        "Compare Pikachu and Raichu", 
        "What are the best type matchups against Gyarados?",
        "Suggest a balanced team with a strong fire attacker and good defense",
        "What are Gengar's weaknesses and how can I counter them?"
    ]
    
    # You can change this to test different queries
    selected_query = queries[1]  # Change index to test different queries
    
    print(f"Query: {selected_query}")
    asyncio.run(invoke_agent(query=selected_query))