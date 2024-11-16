import he from 'he';

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

// Add these variables at the top
let isLoading = false;
let currentPage = 1;

function setLanguage(lang) {
    currentLanguage = lang;
    localStorage.setItem('language', lang);
    window.location.reload();
}

// Initialize language from URL parameter or localStorage
const urlParams = new URLSearchParams(window.location.search);
currentLanguage = urlParams.get('lang') || localStorage.getItem('language') || 'en';
localStorage.setItem('language', currentLanguage);

document.getElementById('search').addEventListener('input', debounce(async (e) => {
    const query = e.target.value;
    const grid = document.querySelector('.pokemon-grid');
    
    grid.classList.add('loading');
    
    try {
        const response = await fetch(`/api/search?q=${query}&lang=${currentLanguage}`);
        const pokemon = await response.json();
        
        grid.innerHTML = pokemon.map(p => `
            <div class="pokemon-card">
                <a href="/pokemon/${p.id}?lang=${he.encode(currentLanguage)}">
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

// Add infinite scroll handler
async function loadMorePokemon() {
    if (isLoading) return;
    
    const grid = document.querySelector('.pokemon-grid');
    const scrollPosition = window.innerHeight + window.scrollY;
    const scrollThreshold = document.documentElement.scrollHeight - 200;

    if (scrollPosition >= scrollThreshold) {
        isLoading = true;
        const start = currentPage * 20 + 1;
        
        try {
            const response = await fetch(`/api/pokemon?start=${start}&lang=${currentLanguage}`);
            const pokemon = await response.json();
            
            if (pokemon.length > 0) {
                const newCards = pokemon.map(p => `
                    <div class="pokemon-card">
                        <a href="/pokemon/${p.id}?lang=${he.encode(currentLanguage)}">
                            <img src="${p.sprites.front_default}" 
                                 alt="${p.name}" 
                                 onerror="handleImageError(this)">
                            <h3>#${String(p.id).padStart(3, '0')} ${p.name}</h3>
                        </a>
                    </div>
                `).join('');
                
                grid.insertAdjacentHTML('beforeend', newCards);
                currentPage++;
            }
        } catch (error) {
            console.error('Error loading more Pokemon:', error);
        } finally {
            isLoading = false;
        }
    }
}

// Add scroll event listener
window.addEventListener('scroll', debounce(loadMorePokemon, 100));

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
    const currentPath = window.location.pathname;
    const searchParams = new URLSearchParams(window.location.search);
    searchParams.set('lang', newLang);
    window.location.href = `${currentPath}?${searchParams.toString()}`;
});

setTheme(localStorage.getItem('theme') || 'light');