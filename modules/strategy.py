from typing import Any, Optional, Dict
import httpx
from .info_retrieval import InfoRetrievalModule

class StrategyModule:
    def __init__(self):
        self.info_module = InfoRetrievalModule()
        self.POKEMON_API_BASE = "https://pokeapi.co/api/v2"
        self.USER_AGENT = "pokemon-app/1.0"
        self.type_effectiveness_cache = {}
    
    async def get_type_effectiveness(self, type_name: str) -> Dict[str, float]:
        """Get type effectiveness data from PokeAPI."""
        if type_name in self.type_effectiveness_cache:
            return self.type_effectiveness_cache[type_name]
            
        url = f"{self.POKEMON_API_BASE}/type/{type_name.lower()}"
        headers = {
            "User-Agent": self.USER_AGENT,
            "Accept": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers, timeout=30.0)
                response.raise_for_status()
                type_data = response.json()
                
                # Process defensive damage relations
                effectiveness = {}
                
                # Super effective against this type (2x damage)
                for relation in type_data.get('damage_relations', {}).get('double_damage_from', []):
                    effectiveness[relation['name']] = 2.0
                
                # Not very effective against this type (0.5x damage)
                for relation in type_data.get('damage_relations', {}).get('half_damage_from', []):
                    effectiveness[relation['name']] = 0.5
                
                # No effect against this type (0x damage)
                for relation in type_data.get('damage_relations', {}).get('no_damage_from', []):
                    effectiveness[relation['name']] = 0.0
                
                # Cache the results
                self.type_effectiveness_cache[type_name] = effectiveness
                return effectiveness
                
            except Exception:
                return {}
    
    async def get_type_matchups(self, pokemon_name: str) -> str:
        """Get type effectiveness and counter-strategy recommendations for a Pokémon."""
        pokemon_data = await self.info_module.make_pokemon_request(pokemon_name)
        
        if not pokemon_data:
            return f"Unable to find Pokémon '{pokemon_name}'. Please check the spelling and try again."
        
        name = pokemon_data.get('name', 'Unknown').title()
        types = [t['type']['name'] for t in pokemon_data.get('types', [])]
        
        # Get effectiveness against this Pokemon's types
        weaknesses = {}
        for type_name in types:
            effectiveness = await self.get_type_effectiveness(type_name)
            for defending_type, multiplier in effectiveness.items():
                if multiplier >= 2.0:  # Super effective
                    weaknesses[defending_type] = weaknesses.get(defending_type, 0) + 1
        
        # Sort weaknesses by effectiveness
        sorted_weaknesses = sorted(
            weaknesses.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        strategy = f"""
Type Matchup Analysis for {name}

Pokemon Types: {', '.join([t.title() for t in types])}

Counter-Strategy Recommendations:
- Use Pokemon with these types: {', '.join([w.title() for w, _ in sorted_weaknesses[:3]]) if sorted_weaknesses else 'Any type'}
- These types are super effective: {', '.join([f"{w.title()} (x{w_count})" for w, w_count in sorted_weaknesses]) if sorted_weaknesses else 'None identified'}
"""
        return strategy 