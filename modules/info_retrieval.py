from typing import Any, Optional
import httpx

class InfoRetrievalModule:
    def __init__(self):
        self.POKEMON_API_BASE = "https://pokeapi.co/api/v2"
        self.USER_AGENT = "pokemon-app/1.0"
    
    async def make_pokemon_request(self, pokemon_name: str) -> Optional[dict[str, Any]]:
        """Make a request to the Pokemon API with proper error handling."""
        url = f"{self.POKEMON_API_BASE}/pokemon/{pokemon_name.lower()}"
        headers = {
            "User-Agent": self.USER_AGENT,
            "Accept": "application/json"
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers, timeout=30.0)
                response.raise_for_status()
                return response.json()
            except Exception:
                return None

    def format_pokemon_data(self, pokemon_data: dict) -> str:
        """Format Pokemon data into a detailed readable string."""
        name = pokemon_data.get('name', 'Unknown').title()
        height = pokemon_data.get('height', 0) / 10  # Convert to meters
        weight = pokemon_data.get('weight', 0) / 10  # Convert to kg
        types = [t['type']['name'].title() for t in pokemon_data.get('types', [])]
        abilities = [a['ability']['name'].title() for a in pokemon_data.get('abilities', [])]
        
        # Extract base stats
        stats = {stat['stat']['name']: stat['base_stat'] for stat in pokemon_data.get('stats', [])}
        
        # Extract moves (limited to first 5)
        moves = [move['move']['name'].title() for move in pokemon_data.get('moves', [])[:5]]
        
        # Calculate total base stats
        total_stats = sum(stats.values())
        
        # Get held items
        held_items = [item['item']['name'].title() for item in pokemon_data.get('held_items', [])]
        
        # Get game appearances
        game_indices = [game['version']['name'].title() for game in pokemon_data.get('game_indices', [])]
        
        # Get sprites
        sprites = pokemon_data.get('sprites', {})
        front_sprite = sprites.get('front_default', 'Not available')
        back_sprite = sprites.get('back_default', 'Not available')
        
        return f"""
Pokemon Information for {name}
====================================

Basic Information:
-----------------
Height: {height} m
Weight: {weight} kg
Types: {', '.join(types) if types else 'Unknown'}
Base Experience: {pokemon_data.get('base_experience', 'Unknown')}

Abilities:
----------
{chr(10).join([f"- {ability}" for ability in abilities]) if abilities else 'Unknown'}

Base Stats:
-----------
HP: {stats.get('hp', 0)}
Attack: {stats.get('attack', 0)}
Defense: {stats.get('defense', 0)}
Sp. Attack: {stats.get('special-attack', 0)}
Sp. Defense: {stats.get('special-defense', 0)}
Speed: {stats.get('speed', 0)}
Total: {total_stats}

Sample Moves:
------------
{chr(10).join([f"- {move}" for move in moves]) if moves else 'Unknown'}

Held Items:
----------
{chr(10).join([f"- {item}" for item in held_items]) if held_items else 'No held items'}

Game Appearances:
---------------
{chr(10).join([f"- {game}" for game in game_indices]) if game_indices else 'No game data available'}

Sprites:
--------
Front: {front_sprite}
Back: {back_sprite}

Additional Information:
---------------------
- Order: #{pokemon_data.get('order', 'Unknown')}
- Base Happiness: {pokemon_data.get('base_happiness', 'Unknown')}
- Capture Rate: {pokemon_data.get('capture_rate', 'Unknown')}
- Is Legendary: {'Yes' if pokemon_data.get('is_legendary', False) else 'No'}
- Is Mythical: {'Yes' if pokemon_data.get('is_mythical', False) else 'No'}
""" 