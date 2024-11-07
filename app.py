from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# Load Pokemon data
with open('pokemon.json', 'r') as f:
    POKEMON_DATA = json.load(f)

@app.route('/')
def index():
    return render_template('index.html', pokemon=POKEMON_DATA)

@app.route('/pokemon/<int:pokemon_id>')
def pokemon_detail(pokemon_id):
    pokemon = next((p for p in POKEMON_DATA if p['id'] == pokemon_id), None)
    return render_template('detail.html', pokemon=pokemon)

@app.route('/api/search')
def search():
    query = request.args.get('q', '').lower()
    results = [p for p in POKEMON_DATA if query in p['name'].lower()]
    return jsonify(results)

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    app.run(debug=debug_mode)