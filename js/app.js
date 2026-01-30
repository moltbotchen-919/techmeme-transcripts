/**
 * 股癌 Podcast 逐字稿網站
 * Gooaye Transcripts App
 */

class GooayeApp {
    constructor() {
        this.episodes = [];
        this.filteredEpisodes = [];
        this.container = document.getElementById('cardsContainer');
        this.searchInput = document.getElementById('searchInput');
        this.modal = document.getElementById('modal');
        this.loading = document.getElementById('loading');
        this.emptyState = document.getElementById('emptyState');
        
        this.init();
    }

    async init() {
        await this.loadEpisodes();
        this.setupEventListeners();
        this.render();
    }

    async loadEpisodes() {
        try {
            const response = await fetch('data/episodes.json');
            const data = await response.json();
            this.episodes = data.episodes || [];
            // Sort by date descending (most recent first)
            this.episodes.sort((a, b) => new Date(b.date) - new Date(a.date));
            this.filteredEpisodes = [...this.episodes];
        } catch (error) {
            console.error('Failed to load episodes:', error);
            this.episodes = [];
            this.filteredEpisodes = [];
        }
        this.loading.style.display = 'none';
    }

    setupEventListeners() {
        // Search functionality
        this.searchInput.addEventListener('input', (e) => {
            this.handleSearch(e.target.value);
        });

        // Modal close button
        document.getElementById('modalClose').addEventListener('click', () => {
            this.closeModal();
        });

        // Close modal on backdrop click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.closeModal();
            }
        });

        // Close modal on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.classList.contains('active')) {
                this.closeModal();
            }
        });
    }

    handleSearch(query) {
        const searchTerm = query.toLowerCase().trim();
        
        if (!searchTerm) {
            this.filteredEpisodes = [...this.episodes];
        } else {
            this.filteredEpisodes = this.episodes.filter(episode => {
                const titleMatch = episode.title.toLowerCase().includes(searchTerm);
                const summaryMatch = episode.summary.toLowerCase().includes(searchTerm);
                const contentMatch = episode.content.toLowerCase().includes(searchTerm);
                const tagsMatch = episode.tags?.some(tag => 
                    tag.toLowerCase().includes(searchTerm)
                );
                return titleMatch || summaryMatch || contentMatch || tagsMatch;
            });
        }
        
        this.render();
    }

    render() {
        this.container.innerHTML = '';
        
        if (this.filteredEpisodes.length === 0) {
            this.emptyState.style.display = 'block';
            return;
        }
        
        this.emptyState.style.display = 'none';
        
        this.filteredEpisodes.forEach(episode => {
            const card = this.createCard(episode);
            this.container.appendChild(card);
        });
    }

    createCard(episode) {
        const card = document.createElement('article');
        card.className = 'card';
        card.setAttribute('data-id', episode.id);
        
        const tagsHTML = episode.tags?.length 
            ? `<div class="card-tags">${episode.tags.map(tag => 
                `<span class="tag">${tag}</span>`).join('')}</div>` 
            : '';
        
        card.innerHTML = `
            <div class="card-date">${this.formatDate(episode.date)}</div>
            <h2 class="card-title">${episode.title}</h2>
            <p class="card-summary">${episode.summary}</p>
            ${tagsHTML}
            <div class="card-footer">
                <span class="read-more">閱讀全文 →</span>
                <span class="episode-num">EP${episode.episode}</span>
            </div>
        `;
        
        card.addEventListener('click', () => {
            this.openModal(episode);
        });
        
        return card;
    }

    openModal(episode) {
        document.getElementById('modalDate').textContent = 
            `EP${episode.episode} · ${this.formatDate(episode.date)}`;
        document.getElementById('modalTitle').textContent = episode.title;
        
        let bodyContent = '';
        
        // Add companies section FIRST if available
        if (episode.companies && episode.companies.length > 0) {
            bodyContent += this.formatCompanies(episode.companies);
        }
        
        bodyContent += this.formatContent(episode.content);
        
        document.getElementById('modalBody').innerHTML = bodyContent;
        
        this.modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    formatCompanies(companies) {
        let html = '<div class="companies-section">';
        html += '<h3>📊 提及公司</h3>';
        html += '<div class="companies-grid">';
        
        companies.forEach(company => {
            const ticker = company.ticker ? `<span class="company-ticker">${company.ticker}</span>` : '';
            html += `
                <div class="company-card">
                    <div class="company-header">
                        ${ticker}
                        <span class="company-name">${company.name}</span>
                    </div>
                    ${company.note ? `<p class="company-note">${company.note}</p>` : ''}
                </div>
            `;
        });
        
        html += '</div></div>';
        return html;
    }

    closeModal() {
        this.modal.classList.remove('active');
        document.body.style.overflow = '';
    }

    formatDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleDateString('zh-TW', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    formatContent(content) {
        // Convert line breaks to paragraphs
        const paragraphs = content.split('\n\n').filter(p => p.trim());
        return paragraphs.map(p => {
            // Check if it's a heading (starts with ##)
            if (p.startsWith('## ')) {
                return `<h3>${p.replace('## ', '')}</h3>`;
            }
            return `<p>${p.replace(/\n/g, '<br>')}</p>`;
        }).join('');
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new GooayeApp();
});
