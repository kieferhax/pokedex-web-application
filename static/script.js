function handleImageError(img) {
    img.onerror = null;
    img.src = '/static/missing-pokemon.png';
}

document.getElementById('search').addEventListener('input', async (e) => {
    const query = e.target.value;
    const grid = document.querySelector('.pokemon-grid');
    
    grid.classList.add('loading');
    
    try {
        const response = await fetch(`/api/search?q=${query}`);
        const pokemon = await response.json();
        
        grid.innerHTML = pokemon.map(p => `
            <div class="pokemon-card">
                <a href="/pokemon/${p.id}">
                    <img src="${p.sprites.front_default}" 
                         alt="${p.name}" 
                         onerror="handleImageError(this)">
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

// Improve theme toggle
function setTheme(theme) {
    document.body.dataset.theme = theme;
    localStorage.setItem('theme', theme);
    document.querySelector('.theme-icon').textContent = theme === 'dark' ? '🌞' : '🌓';
}

document.getElementById('theme-toggle')?.addEventListener('click', () => {
    const newTheme = document.body.dataset.theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
});

// Initialize theme
setTheme(localStorage.getItem('theme') || 'light');