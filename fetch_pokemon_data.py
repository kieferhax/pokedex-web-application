# fetch_pokemon_data.py
import requests # type: ignore
import json
import time

def fetch_pokemon_data():
    pokemon_data = []
    base_url = "https://pokeapi.co/api/v2/pokemon/"
    
    for pokemon_id in range(1, 152):  # First 151 Pokemon
        print(f"Fetching Pokemon #{pokemon_id}")
        response = requests.get(f"{base_url}{pokemon_id}")
        pokemon = response.json()
        
        pokemon_entry = {
            "id": pokemon["id"],
            "name": pokemon["name"],
            "types": [t["type"]["name"] for t in pokemon["types"]],
            "stats": [
                {
                    "name": stat["stat"]["name"],
                    "base_stat": stat["base_stat"]
                }
                for stat in pokemon["stats"]
            ],
            "sprites": {
                "front_default": pokemon["sprites"]["front_default"]
            }
        }
        pokemon_data.append(pokemon_entry)
        time.sleep(1)  # Rate limiting
    
    with open('pokemon.json', 'w', encoding='utf-8') as f:
        json.dump(pokemon_data, f, indent=2)

if __name__ == "__main__":
    fetch_pokemon_data()