document.getElementById('search').addEventListener('input', async (e) => {
    const query = e.target.value;
    const response = await fetch(`/api/search?q=${query}`);
    const pokemon = await response.json();
    
    const grid = document.querySelector('.pokemon-grid');
    grid.innerHTML = pokemon.map(p => `
        <div class="pokemon-card">
            <a href="/pokemon/${p.id}">
                <img src="${p.sprites.front_default}" alt="${p.name}">
                <h3>#${p.id} ${p.name}</h3>
            </a>
        </div>
    `).join('');
});