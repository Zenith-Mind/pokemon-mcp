from typing import Any, Optional
from .info_retrieval import InfoRetrievalModule

class ComparisonModule:
    def __init__(self):
        self.info_module = InfoRetrievalModule()
    
    async def compare_pokemon(self, pokemon1: str, pokemon2: str) -> str:
        """Compare attributes of two Pokémon."""
        data1 = await self.info_module.make_pokemon_request(pokemon1)
        data2 = await self.info_module.make_pokemon_request(pokemon2)
        
        if not data1:
            return f"Unable to find Pokémon '{pokemon1}'. Please check the spelling and try again."
        if not data2:
            return f"Unable to find Pokémon '{pokemon2}'. Please check the spelling and try again."
        
        name1 = data1.get('name', 'Unknown').title()
        name2 = data2.get('name', 'Unknown').title()
        
        # Extract stats for comparison
        stats1 = {stat['stat']['name']: stat['base_stat'] for stat in data1.get('stats', [])}
        stats2 = {stat['stat']['name']: stat['base_stat'] for stat in data2.get('stats', [])}
        
        # Extract moves (limited to first 5)
        moves1 = [move['move']['name'].title() for move in data1.get('moves', [])[:5]]
        moves2 = [move['move']['name'].title() for move in data2.get('moves', [])[:5]]
        
        # Get held items
        held_items1 = [item['item']['name'].title() for item in data1.get('held_items', [])]
        held_items2 = [item['item']['name'].title() for item in data2.get('held_items', [])]
        
        # Calculate total stats
        total_stats1 = sum(stats1.values())
        total_stats2 = sum(stats2.values())
        
        comparison = f"""
Detailed Comparison: {name1} vs {name2}
====================================

Basic Information:
-----------------
{name1}: Height {data1.get('height', 0) / 10}m, Weight {data1.get('weight', 0) / 10}kg
{name2}: Height {data2.get('height', 0) / 10}m, Weight {data2.get('weight', 0) / 10}kg

Types:
------
{name1}: {', '.join([t['type']['name'].title() for t in data1.get('types', [])])}
{name2}: {', '.join([t['type']['name'].title() for t in data2.get('types', [])])}

Abilities:
----------
{name1}:
{chr(10).join([f"- {a['ability']['name'].title()}" for a in data1.get('abilities', [])])}
{name2}:
{chr(10).join([f"- {a['ability']['name'].title()}" for a in data2.get('abilities', [])])}

Base Stats Comparison:
--------------------
HP: {name1} {stats1.get('hp', 0)} vs {name2} {stats2.get('hp', 0)}
Attack: {name1} {stats1.get('attack', 0)} vs {name2} {stats2.get('attack', 0)}
Defense: {name1} {stats1.get('defense', 0)} vs {name2} {stats2.get('defense', 0)}
Sp. Attack: {name1} {stats1.get('special-attack', 0)} vs {name2} {stats2.get('special-attack', 0)}
Sp. Defense: {name1} {stats1.get('special-defense', 0)} vs {name2} {stats2.get('special-defense', 0)}
Speed: {name1} {stats1.get('speed', 0)} vs {name2} {stats2.get('speed', 0)}
Total: {name1} {total_stats1} vs {name2} {total_stats2}

Sample Moves:
------------
{name1}:
{chr(10).join([f"- {move}" for move in moves1]) if moves1 else 'No moves available'}
{name2}:
{chr(10).join([f"- {move}" for move in moves2]) if moves2 else 'No moves available'}

Held Items:
----------
{name1}:
{chr(10).join([f"- {item}" for item in held_items1]) if held_items1 else 'No held items'}
{name2}:
{chr(10).join([f"- {item}" for item in held_items2]) if held_items2 else 'No held items'}

Additional Information:
---------------------
{name1}:
- Order: #{data1.get('order', 'Unknown')}
- Base Experience: {data1.get('base_experience', 'Unknown')}
- Base Happiness: {data1.get('base_happiness', 'Unknown')}
- Capture Rate: {data1.get('capture_rate', 'Unknown')}
- Is Legendary: {'Yes' if data1.get('is_legendary', False) else 'No'}
- Is Mythical: {'Yes' if data1.get('is_mythical', False) else 'No'}

{name2}:
- Order: #{data2.get('order', 'Unknown')}
- Base Experience: {data2.get('base_experience', 'Unknown')}
- Base Happiness: {data2.get('base_happiness', 'Unknown')}
- Capture Rate: {data2.get('capture_rate', 'Unknown')}
- Is Legendary: {'Yes' if data2.get('is_legendary', False) else 'No'}
- Is Mythical: {'Yes' if data2.get('is_mythical', False) else 'No'}
"""
        return comparison 