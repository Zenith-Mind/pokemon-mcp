from typing import Any, Optional, List, Dict
from .info_retrieval import InfoRetrievalModule

class TeamCompositionModule:
    def __init__(self):
        self.info_module = InfoRetrievalModule()
        self.role_pokemon = {
            'attacker': ['Charizard', 'Dragonite', 'Tyranitar', 'Gengar', 'Alakazam'],
            'defender': ['Blastoise', 'Steelix', 'Skarmory', 'Umbreon', 'Chansey'],
            'support': ['Clefable', 'Blissey', 'Togekiss', 'Whimsicott', 'Amoonguss'],
            'speed': ['Jolteon', 'Crobat', 'Aerodactyl', 'Weavile', 'Noivern'],
            'tank': ['Snorlax', 'Aggron', 'Metagross', 'Goodra', 'Toxapex']
        }
        
        self.type_coverage = {
            'fire': ['water', 'ground', 'rock'],
            'water': ['electric', 'grass'],
            'grass': ['fire', 'ice', 'poison', 'flying', 'bug'],
            'electric': ['ground'],
            'psychic': ['bug', 'ghost', 'dark'],
            'ice': ['fire', 'fighting', 'rock', 'steel'],
            'dragon': ['ice', 'dragon', 'fairy'],
            'dark': ['fighting', 'bug', 'fairy'],
            'fairy': ['poison', 'steel'],
            'fighting': ['flying', 'psychic', 'fairy'],
            'poison': ['ground', 'psychic'],
            'ground': ['water', 'grass', 'ice'],
            'flying': ['electric', 'ice', 'rock'],
            'bug': ['fire', 'flying', 'rock'],
            'rock': ['water', 'grass', 'fighting', 'ground', 'steel'],
            'ghost': ['ghost', 'dark'],
            'steel': ['fire', 'fighting', 'ground'],
            'normal': ['fighting']
        }
    
    async def get_pokemon_role(self, pokemon_data: dict) -> str:
        """Determine a Pokemon's role based on its stats."""
        stats = {stat['stat']['name']: stat['base_stat'] for stat in pokemon_data.get('stats', [])}
        
        attack = stats.get('attack', 0)
        sp_attack = stats.get('special-attack', 0)
        defense = stats.get('defense', 0)
        sp_defense = stats.get('special-defense', 0)
        speed = stats.get('speed', 0)
        hp = stats.get('hp', 0)
        
        # Calculate total defensive and offensive stats
        total_defense = defense + sp_defense + hp
        total_attack = attack + sp_attack
        
        if speed > 100 and total_attack > 150:
            return 'speed'
        elif total_attack > 150:
            return 'attacker'
        elif total_defense > 200:
            return 'defender'
        elif hp > 100 and total_defense > 150:
            return 'tank'
        else:
            return 'support'
    
    async def suggest_team(self, description: str) -> str:
        """Suggest a balanced Pokémon team based on a natural language description."""
        description_lower = description.lower()
        
        # Determine team focus from description
        team_focus = []
        if 'balanced' in description_lower:
            team_focus = ['attacker', 'defender', 'support', 'speed', 'tank']
        elif 'offensive' in description_lower or 'attack' in description_lower:
            team_focus = ['attacker', 'attacker', 'speed', 'attacker', 'support', 'tank']
        elif 'defensive' in description_lower or 'defense' in description_lower:
            team_focus = ['defender', 'tank', 'support', 'defender', 'tank', 'support']
        else:
            team_focus = ['attacker', 'defender', 'support', 'speed', 'tank', 'attacker']
        
        # Select Pokemon for each role
        selected_team = []
        for role in team_focus:
            if role in self.role_pokemon:
                selected_team.append(self.role_pokemon[role][0])  # Take first Pokemon from each role
                self.role_pokemon[role].append(self.role_pokemon[role].pop(0))  # Rotate the list
        
        # Get data for each team member
        team_details = []
        for pokemon in selected_team:
            pokemon_data = await self.info_module.make_pokemon_request(pokemon)
            if pokemon_data:
                name = pokemon_data.get('name', 'Unknown').title()
                types = [t['type']['name'].title() for t in pokemon_data.get('types', [])]
                role = await self.get_pokemon_role(pokemon_data)
                team_details.append(f"{name} ({', '.join(types)}) - {role.title()}")
            else:
                team_details.append(f"{pokemon} - Data unavailable")
        
        team_response = f"""
Team Suggestion Based On: "{description}"

Recommended Team:
{chr(10).join([f"{i+1}. {detail}" for i, detail in enumerate(team_details)])}

Team Strategy:
- Balanced type coverage
- Mix of offensive and defensive roles
- Synergistic team composition
- Adaptable to various battle scenarios

Note: This is a basic suggestion. Consider individual Pokemon movesets, abilities, and your specific battle format for optimal team building.
"""
        return team_response 