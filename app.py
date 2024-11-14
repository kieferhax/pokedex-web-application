from flask import Flask, render_template, jsonify, request
import requests
from functools import lru_cache

app = Flask(__name__)

POKE_API_BASE = "https://pokeapi.co/api/v2"

@lru_cache(maxsize=1000)
def get_pokemon_species(pokemon_id, lang='en'):
    response = requests.get(f"{POKE_API_BASE}/pokemon-species/{pokemon_id}")
    if response.ok:
        data = response.json()
        # Find the flavor text in the requested language
        flavor_texts = data['flavor_text_entries']
        text = next((entry['flavor_text'] for entry in flavor_texts 
                    if entry['language']['name'] == lang), '')
        return text.replace('\n', ' ').replace('\f', ' ')
    return ""

@lru_cache(maxsize=1000)
def get_pokemon_data(pokemon_id, lang='en'):
    response = requests.get(f"{POKE_API_BASE}/pokemon/{pokemon_id}")
    if response.ok:
        data = response.json()
        species_text = get_pokemon_species(pokemon_id, lang)
        
        # Get Japanese name if needed
        if lang == 'ja':
            species_response = requests.get(f"{POKE_API_BASE}/pokemon-species/{pokemon_id}")
            if species_response.ok:
                species_data = species_response.json()
                ja_name = next((name['name'] for name in species_data['names'] 
                              if name['language']['name'] == 'ja'), data['name'])
                data['name'] = ja_name

        return {
            'id': data['id'],
            'name': data['name'],
            'sprites': data['sprites'],
            'types': [t['type']['name'] for t in data['types']],
            'stats': [
                {'name': s['stat']['name'],
                 'base_stat': s['base_stat']} for s in data['stats']
            ],
            'species_text': species_text
        }
    return None

@app.route('/')
def index():
    lang = request.args.get('lang', 'en')
    pokemon_list = [get_pokemon_data(i, lang) for i in range(1, 152)]  # First 151 Pokemon
    return render_template('index.html', pokemon=pokemon_list, lang=lang)

@app.route('/pokemon/<int:pokemon_id>')
def pokemon_detail(pokemon_id):
    lang = request.args.get('lang', 'en')
    pokemon = get_pokemon_data(pokemon_id, lang)
    if pokemon:
        return render_template('detail.html', pokemon=pokemon, lang=lang)
    return "Pokemon not found", 404

@app.route('/api/search')
def search_pokemon():
    query = request.args.get('q', '').lower()
    lang = request.args.get('lang', 'en')
    
    # Handle both number and name searches
    results = []
    try:
        # Try number search first
        if query.isdigit():
            pokemon = get_pokemon_data(int(query), lang)
            if pokemon:
                results.append(pokemon)
        
        # Then search by name
        for i in range(1, 152):  # First 151 Pokemon
            pokemon = get_pokemon_data(i, lang)
            if pokemon and query in pokemon['name'].lower():
                if pokemon not in results:  # Avoid duplicates
                    results.append(pokemon)
    except Exception as e:
        print(f"Search error: {e}")
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)