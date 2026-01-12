// Documentation Search with Dropdown Suggestions
const docsData = [
    {
        title: "Getting Started",
        description: "Install ORC, set up your first project, and run your first analysis",
        url: "/docs/getting-started",
        keywords: ["installation", "setup", "install", "begin", "start", "first"]
    },
    {
        title: "CLI Reference",
        description: "Complete command-line interface documentation with examples",
        url: "/docs/cli",
        keywords: ["command", "terminal", "cli", "commands", "orc index", "orc analyze"]
    },
    {
        title: "Web Interface",
        description: "Learn how to use the interactive web dashboard",
        url: "/docs/web",
        keywords: ["dashboard", "web", "interface", "gui", "browser"]
    },
    {
        title: "API Documentation",
        description: "Integrate ORC into your tools with our REST API",
        url: "/docs/api",
        keywords: ["api", "rest", "integration", "endpoint", "token"]
    },
    {
        title: "Tutorials",
        description: "Step-by-step guides for common workflows",
        url: "/docs/tutorials",
        keywords: ["tutorial", "guide", "learn", "how to"]
    },
    {
        title: "Your First Analysis",
        description: "Index and analyze your first project",
        url: "/docs/tutorial/first-analysis",
        keywords: ["first", "analysis", "index", "tutorial", "begin"]
    },
    {
        title: "Using AI Chat",
        description: "Ask questions about your codebase with AI",
        url: "/docs/tutorial/ai-chat",
        keywords: ["ai", "chat", "assistant", "questions", "ask"]
    },
    {
        title: "Web Interface Setup",
        description: "Set up and use the web dashboard",
        url: "/docs/tutorial/web-setup",
        keywords: ["web", "setup", "dashboard", "configure", "account"]
    },
    {
        title: "Authentication",
        description: "Login methods and token generation",
        url: "/docs/getting-started#authentication",
        keywords: ["login", "auth", "authentication", "token", "api key"]
    },
    {
        title: "AI Chat Commands",
        description: "Slash commands available in AI chat",
        url: "/docs/cli#ai-chat",
        keywords: ["slash", "commands", "/help", "/status", "/models", "chat"]
    },
    {
        title: "Dead Code Detection",
        description: "Find potentially unused code",
        url: "/docs/cli",
        keywords: ["dead", "unused", "code", "orc dead", "cleanup"]
    },
    {
        title: "Complexity Analysis",
        description: "Show complexity metrics and find complex functions",
        url: "/docs/cli",
        keywords: ["complexity", "metrics", "orc complexity", "analysis"]
    },
    {
        title: "API Configuration",
        description: "Set up AI provider API keys",
        url: "/docs/web#setting-up-api-keys",
        keywords: ["api", "config", "provider", "groq", "openai", "keys"]
    }
];

class DocsSearch {
    constructor() {
        this.searchInput = document.getElementById('docsSearch');
        this.resultsContainer = document.getElementById('searchResults');
        this.isOpen = false;
        
        if (!this.searchInput || !this.resultsContainer) return;
        
        this.init();
    }
    
    init() {
        // Search on input
        this.searchInput.addEventListener('input', (e) => {
            this.handleSearch(e.target.value);
        });
        
        // Focus handler
        this.searchInput.addEventListener('focus', () => {
            if (this.searchInput.value.trim()) {
                this.handleSearch(this.searchInput.value);
            }
        });
        
        // Close on click outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.docs-search-container')) {
                this.closeResults();
            }
        });
        
        // Keyboard navigation
        this.searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeResults();
                this.searchInput.blur();
            }
        });
    }
    
    handleSearch(query) {
        if (!query || query.trim().length < 2) {
            this.closeResults();
            return;
        }
        
        const results = this.search(query.toLowerCase().trim());
        this.displayResults(results);
    }
    
    search(query) {
        const results = [];
        
        for (const doc of docsData) {
            let score = 0;
            
            // Title match (highest priority)
            if (doc.title.toLowerCase().includes(query)) {
                score += 100;
            }
            
            // Description match
            if (doc.description.toLowerCase().includes(query)) {
                score += 50;
            }
            
            // Keywords match
            for (const keyword of doc.keywords) {
                if (keyword.includes(query)) {
                    score += 30;
                }
                if (keyword === query) {
                    score += 50; // Exact keyword match
                }
            }
            
            if (score > 0) {
                results.push({ ...doc, score });
            }
        }
        
        // Sort by score and return top 5
        return results.sort((a, b) => b.score - a.score).slice(0, 5);
    }
    
    displayResults(results) {
        if (results.length === 0) {
            this.resultsContainer.innerHTML = `
                <div class="search-result-item no-results">
                    <div class="search-result-title">No results found</div>
                    <div class="search-result-description">Try a different search term</div>
                </div>
            `;
            this.openResults();
            return;
        }
        
        const html = results.map(result => `
            <a href="${result.url}" class="search-result-item">
                <div class="search-result-content">
                    <div class="search-result-title">${this.highlightMatch(result.title, this.searchInput.value)}</div>
                    <div class="search-result-description">${result.description}</div>
                </div>
            </a>
        `).join('');
        
        this.resultsContainer.innerHTML = html;
        this.openResults();
    }
    
    highlightMatch(text, query) {
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }
    
    openResults() {
        this.resultsContainer.classList.add('open');
        this.isOpen = true;
    }
    
    closeResults() {
        this.resultsContainer.classList.remove('open');
        this.isOpen = false;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    new DocsSearch();
});
