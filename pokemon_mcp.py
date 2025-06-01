from mcp.server.fastmcp import FastMCP
from modules import (
    InfoRetrievalModule,
    ComparisonModule,
    StrategyModule,
    TeamCompositionModule
)

# Initialize FastMCP server
mcp = FastMCP("pokemon")

# Initialize modules
info_module = InfoRetrievalModule()
comparison_module = ComparisonModule()
strategy_module = StrategyModule()
team_module = TeamCompositionModule()

@mcp.tool()
async def get_pokemon(name: str) -> str:
    """Get detailed information about a Pokémon.

    Args:
        name: Name of the Pokémon to look up
    """
    pokemon_data = await info_module.make_pokemon_request(name)
    
    if not pokemon_data:
        return f"Unable to find Pokémon '{name}'. Please check the spelling and try again."
    
    return info_module.format_pokemon_data(pokemon_data)

@mcp.tool()
async def compare_pokemon(pokemon1: str, pokemon2: str) -> str:
    """Compare attributes of two Pokémon.

    Args:
        pokemon1: Name of the first Pokémon
        pokemon2: Name of the second Pokémon
    """
    return await comparison_module.compare_pokemon(pokemon1, pokemon2)

@mcp.tool()
async def get_type_matchups(pokemon_name: str) -> str:
    """Get type effectiveness and counter-strategy recommendations for a Pokémon.

    Args:
        pokemon_name: Name of the Pokémon to analyze
    """
    return await strategy_module.get_type_matchups(pokemon_name)

@mcp.tool()
async def suggest_team(description: str) -> str:
    """Suggest a balanced Pokémon team based on a natural language description.

    Args:
        description: Description of desired team (e.g., "balanced team with strong defense and fire attacker")
    """
    return await team_module.suggest_team(description)

if __name__ == "__main__":
    mcp.run(transport='stdio')