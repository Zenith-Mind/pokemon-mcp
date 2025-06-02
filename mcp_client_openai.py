from langchain_openai import ChatOpenAI
from contextlib import asynccontextmanager
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
import asyncio
import os
import logging

# Set up logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'ERROR'))
logger = logging.getLogger(__name__)

if os.getenv('OPENAI_API_KEY'):
    llm = ChatOpenAI(model="o3-mini")
else:
    print('Export OPENAI_API_KEY to initialize OpenAI LLM.')
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
    pokemon_tools = [tool for tool in tools if tool.name in [
        "get_pokemon", 
        "compare_pokemon", 
        "get_type_matchups", 
        "suggest_team"
    ]]
    
    logger.info("Loaded Pokémon MCP tools: " + ", ".join(tool.name for tool in pokemon_tools))
    
    agent = create_react_agent(
        llm,
        tools=pokemon_tools,
        prompt="""You are a Pokémon expert assistant. You have access to tools that can:
        - Get detailed information about any Pokémon
        - Compare two Pokémon's attributes
        - Analyze type matchups and strategies
        - Suggest balanced team compositions

        Use these tools to provide comprehensive and helpful responses about Pokémon."""
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
        "Tell me about Charizard and its strengths",
        "Compare Pikachu and Raichu",
        "What are the best type matchups against Gyarados?",
        "Suggest a balanced team with a strong fire attacker and good defense"
    ]
    
    # You can change this to test different queries
    selected_query = queries[0]  # Change index to test different queries
    
    print(f"Query: {selected_query}")
    asyncio.run(invoke_agent(query=selected_query))