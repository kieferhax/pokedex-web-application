# convert_to_json.py
import json

def create_pokemon_json():
    # First 151 Pokemon with basic data
    pokemon_data = []
    
    # Sample data structure for each Pokemon
    base_sprite_url = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/"
    
    pokemon_list = [
        {"id": 1, "name": "bulbasaur", "types": ["grass", "poison"]},
        {"id": 2, "name": "ivysaur", "types": ["grass", "poison"]},
        # ... Add more Pokemon here
    ]
    
    for pokemon in pokemon_list:
        pokemon_entry = {
            "id": pokemon["id"],
            "name": pokemon["name"],
            "types": pokemon["types"],
            "stats": [
                {"name": "hp", "base_stat": 45},
                {"name": "attack", "base_stat": 49},
                {"name": "defense", "base_stat": 49},
                {"name": "special-attack", "base_stat": 65},
                {"name": "special-defense", "base_stat": 65},
                {"name": "speed", "base_stat": 45}
            ],
            "sprites": {
                "front_default": f"{base_sprite_url}{pokemon['id']}.png"
            }
        }
        pokemon_data.append(pokemon_entry)
    
    # Write to JSON file
    with open('pokemon.json', 'w', encoding='utf-8') as f:
        json.dump(pokemon_data, f, indent=2)

if __name__ == "__main__":
    create_pokemon_json()