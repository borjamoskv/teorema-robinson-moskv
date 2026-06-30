document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('grid');
    const stats = document.getElementById('stats');
    const filters = document.getElementById('filters');
    
    let entities = [];

    // Fetch data from local SQLite backend
    fetch('http://localhost:3060/api/entities')
        .then(res => res.json())
        .then(data => {
            entities = data.data || [];
            renderStats();
            renderGrid('all');
        })
        .catch(err => {
            console.error('[C5-REAL] Error fetching entities:', err);
            grid.innerHTML = `<div style="color: red; grid-column: 1/-1;">Error de Conexión C5-REAL: Verifica que server.js está corriendo.</div>`;
        });

    function renderStats() {
        const counts = entities.reduce((acc, curr) => {
            acc[curr.category] = (acc[curr.category] || 0) + 1;
            return acc;
        }, {});
        
        stats.innerHTML = `
            <div>NODES: <strong>${entities.length}</strong></div>
            <div>PRIM: <strong>${counts['PRIMITIVAS'] || 0}</strong></div>
            <div>INV: <strong>${counts['INVARIANTES'] || 0}</strong></div>
        `;
    }

    function renderGrid(filter) {
        grid.innerHTML = '';
        const filtered = filter === 'all' 
            ? entities 
            : entities.filter(e => e.category === filter);
            
        filtered.forEach(e => {
            const card = document.createElement('article');
            card.className = 'card';
            card.dataset.category = e.category;
            
            card.innerHTML = `
                <div class="card-id">${e.id}</div>
                <h3 class="card-title">${e.title}</h3>
                <p class="card-desc">${e.description}</p>
            `;
            
            grid.appendChild(card);
        });
    }

    // Filter Logic
    filters.addEventListener('click', (e) => {
        if (e.target.tagName === 'BUTTON') {
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            e.target.classList.add('active');
            renderGrid(e.target.dataset.filter);
        }
    });
});
