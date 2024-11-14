function handleImageError(img) {
    img.onerror = null;
    img.src = '/static/missing-pokemon.png';
}

function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

let currentLanguage = localStorage.getItem('language') || 'en';

function setLanguage(lang) {
    currentLanguage = lang;
    localStorage.setItem('language', lang);
    window.location.reload();
}

document.getElementById('search').addEventListener('input', debounce(async (e) => {
    const query = e.target.value;
    const grid = document.querySelector('.pokemon-grid');
    
    grid.classList.add('loading');
    
    try {
        const response = await fetch(`/api/search?q=${query}&lang=${currentLanguage}`);
        const pokemon = await response.json();
        
        grid.innerHTML = pokemon.map(p => `
            <div class="pokemon-card">
                <a href="/pokemon/${p.id}?lang=${currentLanguage}">
                    <img src="${p.sprites.front_default}" 
                         alt="${p.name}" 
                         onerror="handleImageError(this)">
                    <h3>#${String(p.id).padStart(3, '0')} ${p.name}</h3>
                </a>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error fetching Pokemon:', error);
        grid.innerHTML = '<div class="error">Error loading Pokemon</div>';
    } finally {
        grid.classList.remove('loading');
    }
}, 300));

document.querySelector('.pokemon-grid').addEventListener('mouseover', (e) => {
    if (e.target.closest('.pokemon-card')) {
    }
});

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    document.querySelector('.theme-icon').textContent = theme === 'dark' ? '🌞' : '🌓';
}

document.getElementById('theme-toggle')?.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
});

document.getElementById('language-toggle')?.addEventListener('click', () => {
    const newLang = currentLanguage === 'en' ? 'ja' : 'en';
    setLanguage(newLang);
});

setTheme(localStorage.getItem('theme') || 'light');