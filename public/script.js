
// Mobile Navigation
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

if (hamburger && navMenu) {
    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navMenu.classList.toggle('active');
    });

    // Close mobile menu when clicking on a link
    document.querySelectorAll('.nav-link').forEach(n => n.addEventListener('click', () => {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
    }));
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Navbar background on scroll
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 100) {
        navbar.style.background = 'rgba(255, 255, 255, 0.98)';
        navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
    } else {
        navbar.style.background = 'rgba(255, 255, 255, 0.95)';
        navbar.style.boxShadow = 'none';
    }
});

// Counter Animation for Stats
function animateCounters() {
    const counters = document.querySelectorAll('.stat-number');
    
    const observerOptions = {
        threshold: 0.7
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = parseInt(counter.getAttribute('data-target'));
                const increment = target / 100;
                let current = 0;

                const updateCounter = () => {
                    if (current < target) {
                        current += increment;
                        counter.textContent = Math.ceil(current);
                        setTimeout(updateCounter, 20);
                    } else {
                        counter.textContent = target;
                    }
                };

                updateCounter();
                observer.unobserve(counter);
            }
        });
    }, observerOptions);

    counters.forEach(counter => observer.observe(counter));
}

// Initialize counter animation when page loads
document.addEventListener('DOMContentLoaded', animateCounters);

// Scroll animations for elements
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.feature-card, .card');
    
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}

document.addEventListener('DOMContentLoaded', initScrollAnimations);

// Tab functionality
function initTabs() {
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.getAttribute('data-tab');

            // Remove active class from all tabs and contents
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to clicked tab and corresponding content
            tab.classList.add('active');
            const targetContent = document.getElementById(target);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', initTabs);

// Form validation and submission
function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.style.borderColor = '#ff6b6b';
            isValid = false;
        } else {
            input.style.borderColor = '#e1e1e1';
        }
    });

    return isValid;
}

// Show loading state
function showLoading(button) {
    const originalText = button.textContent;
    button.textContent = 'Loading...';
    button.disabled = true;
    return originalText;
}

function hideLoading(button, originalText) {
    button.textContent = originalText;
    button.disabled = false;
}

// Show alert messages
function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;

    const container = document.querySelector('.form-container') || document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);

    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// API call helper
async function apiCall(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        const data = await response.json();
        return { success: response.ok, data };
    } catch (error) {
        console.error('API call failed:', error);
        return { success: false, error: error.message };
    }
}

// Local storage helper
const storage = {
    set: (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('Storage set failed:', error);
        }
    },
    get: (key) => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (error) {
            console.error('Storage get failed:', error);
            return null;
        }
    },
    remove: (key) => {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('Storage remove failed:', error);
        }
    }
};

// Check authentication status
function checkAuth() {
    const token = storage.get('authToken');
    const user = storage.get('user');
    
    if (token && user) {
        updateNavForLoggedInUser(user);
        return true;
    }
    return false;
}

function updateNavForLoggedInUser(user) {
    const loginBtn = document.querySelector('.login-btn');
    if (loginBtn) {
        loginBtn.textContent = user.name;
        loginBtn.href = '#';
        loginBtn.addEventListener('click', (e) => {
            e.preventDefault();
            showUserMenu();
        });
    }
}

function showUserMenu() {
    // Create dropdown menu for logged in user
    const menu = document.createElement('div');
    menu.className = 'user-menu';
    menu.innerHTML = `
        <a href="profile.html">Profile</a>
        <a href="#" onclick="logout()">Logout</a>
    `;
    
    // Position and show menu
    document.body.appendChild(menu);
}

function logout() {
    storage.remove('authToken');
    storage.remove('user');
    window.location.reload();
}

// Initialize authentication check on page load
document.addEventListener('DOMContentLoaded', checkAuth);

// Intersection Observer for animations
const observeElements = (selector, callback, options = {}) => {
    const elements = document.querySelectorAll(selector);
    const observer = new IntersectionObserver(callback, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px',
        ...options
    });

    elements.forEach(el => observer.observe(el));
    return observer;
};

// Lazy loading for images
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(img => {
        img.classList.add('lazy');
        imageObserver.observe(img);
    });
}

document.addEventListener('DOMContentLoaded', initLazyLoading);

// Search functionality
function initSearch() {
    const searchInput = document.querySelector('#searchInput');
    const searchResults = document.querySelector('#searchResults');

    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();
            
            if (query.length < 2) {
                if (searchResults) searchResults.innerHTML = '';
                return;
            }

            searchTimeout = setTimeout(() => {
                performSearch(query);
            }, 300);
        });
    }
}

async function performSearch(query) {
    const searchResults = document.querySelector('#searchResults');
    if (!searchResults) return;

    searchResults.innerHTML = '<div class="loading">Searching...</div>';

    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (data.success && data.results.length > 0) {
            displaySearchResults(data.results);
        } else {
            searchResults.innerHTML = '<div class="no-content">No results found</div>';
        }
    } catch (error) {
        searchResults.innerHTML = '<div class="alert alert-error">Search failed. Please try again.</div>';
    }
}

function displaySearchResults(results) {
    const searchResults = document.querySelector('#searchResults');
    if (!searchResults) return;

    const html = results.map(result => `
        <div class="search-result">
            <h4><a href="${result.url}">${result.title}</a></h4>
            <p>${result.description}</p>
            <span class="result-type">${result.type}</span>
        </div>
    `).join('');

    searchResults.innerHTML = html;
}

document.addEventListener('DOMContentLoaded', initSearch);

// Utility functions
const utils = {
    formatDate: (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },

    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    throttle: (func, limit) => {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    copyToClipboard: async (text) => {
        try {
            await navigator.clipboard.writeText(text);
            showAlert('Copied to clipboard!', 'success');
        } catch (error) {
            console.error('Copy failed:', error);
            showAlert('Copy failed!', 'error');
        }
    }
};

// Export for use in other files
window.GrowEasy = {
    apiCall,
    storage,
    showAlert,
    validateForm,
    showLoading,
    hideLoading,
    utils
};
