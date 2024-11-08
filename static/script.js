document.getElementById('search').addEventListener('input', async (e) => {
    const query = e.target.value;
    const grid = document.querySelector('.pokemon-grid');
    
    // Add loading state
    grid.classList.add('loading');
    
    try {
        const response = await fetch(`/api/search?q=${query}`);
        const pokemon = await response.json();
        
        grid.innerHTML = pokemon.map(p => `
            <div class="pokemon-card">
                <a href="/pokemon/${p.id}">
                    <img src="${p.sprites.front_default}" alt="${p.name}">
                    <h3>#${String(p.id).padStart(3, '0')} ${p.name.charAt(0).toUpperCase() + p.name.slice(1)}</h3>
                </a>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error fetching Pokemon:', error);
        grid.innerHTML = '<div class="error">Error loading Pokemon</div>';
    } finally {
        grid.classList.remove('loading');
    }
});

// Add hover sound effect for cards
document.querySelector('.pokemon-grid').addEventListener('mouseover', (e) => {
    if (e.target.closest('.pokemon-card')) {
        // You can add a subtle hover sound here if desired
    }
});