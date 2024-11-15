from flask import Flask, render_template, jsonify, request
import requests
from functools import lru_cache
import logging
from concurrent.futures import ThreadPoolExecutor
import threading
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Configure session with retries and connection pooling
session = requests.Session()
retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=retries)
session.mount('http://', adapter)
session.mount('https://', adapter)

POKE_API_BASE = "https://pokeapi.co/api/v2"
initial_pokemon_cache = {}
cache_lock = threading.Lock()

# Modify API calls to use session and timeout
@lru_cache(maxsize=1000)
def get_pokemon_species(pokemon_id, lang='en'):
    try:
        response = session.get(f"{POKE_API_BASE}/pokemon-species/{pokemon_id}", timeout=5)
        if response.ok:
            data = response.json()
            # Find the flavor text in the requested language
            flavor_texts = data['flavor_text_entries']
            text = next((entry['flavor_text'] for entry in flavor_texts 
                        if entry['language']['name'] == lang), '')
            return text.replace('\n', ' ').replace('\f', ' ')
    except Exception as e:
        app.logger.error(f"Error in get_pokemon_species: {str(e)}")
    return ""

@lru_cache(maxsize=1000)
def get_pokemon_data(pokemon_id, lang='en'):
    try:
        response = session.get(f"{POKE_API_BASE}/pokemon/{pokemon_id}", timeout=5)
        if response.ok:
            data = response.json()
            app.logger.debug(f"Pokemon API response: {data}")
            species_text = get_pokemon_species(pokemon_id, lang)
            
            if lang == 'ja':
                try:
                    species_response = session.get(
                        f"{POKE_API_BASE}/pokemon-species/{pokemon_id}",
                        timeout=5
                    )
                    if species_response.ok:
                        species_data = species_response.json()
                        app.logger.debug(f"Species API response: {species_data}")
                        ja_name = next((name['name'] for name in species_data['names'] 
                                      if name['language']['name'] == 'ja'), data['name'])
                        data['name'] = ja_name

                except Exception as e:
                    app.logger.error(f"Error fetching Japanese name: {str(e)}")

            processed_data = {
                'id': data['id'],
                'name': data['name'],
                'sprites': {
                    'front_default': data['sprites'].get('front_default', '')
                },
                'types': [t['type']['name'] for t in data['types']],
                'stats': [{
                    'name': s['stat']['name'],
                    'base_stat': int(s['base_stat'])  # Ensure integer conversion
                } for s in data['stats']],
                'species_text': species_text,
                'lang': lang  # Add language to processed data
            }
            app.logger.debug(f"Processed pokemon data: {processed_data}")
            return processed_data
    except Exception as e:
        app.logger.error(f"Error in get_pokemon_data: {str(e)}")
        return None

def prefetch_pokemon_data():
    with ThreadPoolExecutor(max_workers=20) as executor:  # Increased workers
        futures = []
        for lang in ['en', 'ja']:
            for i in range(1, 151):  # Prefetch all Pokemon
                futures.append(executor.submit(get_pokemon_data, i, lang))
        
        for future in futures:
            try:
                result = future.result(timeout=10)  # Add timeout to future
                if result:
                    cache_key = f"{result['id']}_{result.get('lang', 'en')}"
                    with cache_lock:
                        initial_pokemon_cache[cache_key] = result
            except Exception as e:
                app.logger.error(f"Prefetch error: {e}")

# Remove the @app.before_first_request decorator
def init_pokemon_cache():
    threading.Thread(target=prefetch_pokemon_data, daemon=True).start()

# Create a new init_app function
def create_app():
    with app.app_context():
        init_pokemon_cache()
    return app

# Modify index route to use cache
@app.route('/')
def index():
    lang = request.args.get('lang', 'en')
    pokemon_list = []
    
    # Get from cache or fetch if not available
    for i in range(1, 21):
        cache_key = f"{i}_{lang}"
        with cache_lock:
            pokemon = initial_pokemon_cache.get(cache_key)
        if not pokemon:
            pokemon = get_pokemon_data(i, lang)
        if pokemon:
            pokemon_list.append(pokemon)
    
    return render_template('index.html', pokemon=pokemon_list, lang=lang)

@app.route('/api/pokemon')
def get_pokemon_batch():
    start = int(request.args.get('start', 1))
    end = min(start + 20, 152)  # Load 20 at a time, cap at 151
    lang = request.args.get('lang', 'en')
    
    pokemon_list = [get_pokemon_data(i, lang) for i in range(start, end)]
    return jsonify(pokemon_list)

@app.route('/pokemon/<int:pokemon_id>')
def pokemon_detail(pokemon_id):
    try:
        lang = request.args.get('lang', 'en')
        app.logger.debug(f"Fetching pokemon {pokemon_id} in language {lang}")
        pokemon = get_pokemon_data(pokemon_id, lang)
        if pokemon:
            return render_template('detail.html', pokemon=pokemon, lang=lang)
        return "Pokemon not found", 404
    except Exception as e:
        app.logger.error(f"Error in pokemon_detail: {str(e)}")
        return "An internal error has occurred!", 500

@app.route('/api/search')
def search_pokemon():
    query = request.args.get('q', '').lower()
    lang = request.args.get('lang', 'en')
    
    results = []
    try:
        # Use cache for search
        with cache_lock:
            cached_pokemon = [p for p in initial_pokemon_cache.values() 
                            if p.get('lang', 'en') == lang]
        
        # Search in cached data first
        for pokemon in cached_pokemon:
            if (query.isdigit() and str(pokemon['id']) == query) or \
               (query in pokemon['name'].lower()):
                results.append(pokemon)
                
        # Only search API if not found in cache
        if not results and query.isdigit():
            pokemon = get_pokemon_data(int(query), lang)
            if pokemon:
                results.append(pokemon)
    except Exception as e:
        app.logger.error(f"Search error: {e}")
    
    return jsonify(results)

# Call init at the bottom
if __name__ == '__main__':
    create_app()
    app.run(debug=False)  # Change debug to False