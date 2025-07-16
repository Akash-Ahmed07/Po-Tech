// Po-Tech Educational Platform - Main JavaScript File

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialize the application
function initializeApp() {
    initializeAnimations();
    initializeFormValidation();
    initializeTooltips();
    initializeImageLazyLoading();
    initializeScrollEffects();
    initializeThemeManager();
    initializeSearch();
    initializeFileUpload();
    initializeNotifications();
}

// Initialize page animations
function initializeAnimations() {
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, { threshold: 0.1 });

    cards.forEach(card => {
        observer.observe(card);
    });

    // Add slide-up animation to sections
    const sections = document.querySelectorAll('section');
    sections.forEach((section, index) => {
        section.style.animationDelay = `${index * 0.1}s`;
        section.classList.add('slide-up');
    });
}

// Form validation and enhancement
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });

        // Real-time validation
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
        });
    });
}

// Validate individual form field
function validateField(field) {
    const feedback = field.nextElementSibling;
    
    if (field.checkValidity()) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        if (feedback && feedback.classList.contains('invalid-feedback')) {
            feedback.style.display = 'none';
        }
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        if (feedback && feedback.classList.contains('invalid-feedback')) {
            feedback.style.display = 'block';
        }
    }
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Lazy loading for images
function initializeImageLazyLoading() {
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

    images.forEach(img => imageObserver.observe(img));
}

// Scroll effects
function initializeScrollEffects() {
    let ticking = false;

    function updateScrollEffects() {
        const scrolled = window.pageYOffset;
        const rate = scrolled * -0.5;

        // Parallax effect for hero sections
        const heroElements = document.querySelectorAll('.hero-section');
        heroElements.forEach(hero => {
            hero.style.transform = `translateY(${rate}px)`;
        });

        // Show/hide scroll to top button
        const scrollTopBtn = document.getElementById('scrollTopBtn');
        if (scrollTopBtn) {
            if (scrolled > 300) {
                scrollTopBtn.style.display = 'block';
                scrollTopBtn.classList.add('fade-in');
            } else {
                scrollTopBtn.style.display = 'none';
            }
        }

        ticking = false;
    }

    function requestScrollUpdate() {
        if (!ticking) {
            requestAnimationFrame(updateScrollEffects);
            ticking = true;
        }
    }

    window.addEventListener('scroll', requestScrollUpdate);

    // Smooth scroll for anchor links
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
}

// Theme management
function initializeThemeManager() {
    const themeToggle = document.getElementById('themeToggle');
    const currentTheme = localStorage.getItem('theme') || 'dark';
    
    // Set initial theme
    document.documentElement.setAttribute('data-bs-theme', currentTheme);
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            // Update icon
            const icon = this.querySelector('i');
            if (icon) {
                icon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            }
        });
    }
}

// Search functionality
function initializeSearch() {
    const searchInputs = document.querySelectorAll('input[type="search"], input[name="search"]');
    
    searchInputs.forEach(input => {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(this.value, this);
            }, 300);
        });
    });
}

// Perform search with debouncing
function performSearch(query, inputElement) {
    if (query.length < 2) return;
    
    // Add search indicator
    const searchIndicator = inputElement.parentNode.querySelector('.search-indicator');
    if (searchIndicator) {
        searchIndicator.style.display = 'block';
    }
    
    // Simulate search delay (in real app, this would be an API call)
    setTimeout(() => {
        if (searchIndicator) {
            searchIndicator.style.display = 'none';
        }
        console.log('Search performed for:', query);
    }, 500);
}

// File upload enhancements
function initializeFileUpload() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            handleFileUpload(this);
        });
        
        // Drag and drop functionality
        const container = input.closest('.file-upload-container') || input.parentNode;
        
        container.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('drag-over');
        });
        
        container.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
        });
        
        container.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
                handleFileUpload(input);
            }
        });
    });
}

// Handle file upload with preview and validation
function handleFileUpload(input) {
    const files = input.files;
    const maxSize = 50 * 1024 * 1024; // 50MB
    const allowedTypes = {
        image: ['image/jpeg', 'image/png', 'image/gif'],
        pdf: ['application/pdf'],
        document: ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    };
    
    Array.from(files).forEach(file => {
        // Validate file size
        if (file.size > maxSize) {
            showNotification('File size exceeds 50MB limit', 'danger');
            input.value = '';
            return;
        }
        
        // Show file preview
        showFilePreview(file, input);
        
        // Update progress bar if exists
        const progressBar = input.parentNode.querySelector('.progress-bar');
        if (progressBar) {
            simulateUploadProgress(progressBar);
        }
    });
}

// Show file preview
function showFilePreview(file, input) {
    const previewContainer = input.parentNode.querySelector('.file-preview') || 
                           document.getElementById('filePreview');
    
    if (!previewContainer) return;
    
    const preview = document.createElement('div');
    preview.className = 'file-preview-item d-flex align-items-center p-2 border rounded mb-2';
    
    if (file.type.startsWith('image/')) {
        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        img.className = 'preview-image me-2';
        img.style.width = '50px';
        img.style.height = '50px';
        img.style.objectFit = 'cover';
        img.style.borderRadius = '4px';
        preview.appendChild(img);
    } else {
        const icon = document.createElement('i');
        icon.className = 'fas fa-file fa-2x text-muted me-2';
        preview.appendChild(icon);
    }
    
    const info = document.createElement('div');
    info.className = 'flex-grow-1';
    info.innerHTML = `
        <div class="fw-bold">${file.name}</div>
        <small class="text-muted">${formatFileSize(file.size)}</small>
    `;
    preview.appendChild(info);
    
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'btn btn-sm btn-outline-danger';
    removeBtn.innerHTML = '<i class="fas fa-times"></i>';
    removeBtn.onclick = () => {
        preview.remove();
        input.value = '';
    };
    preview.appendChild(removeBtn);
    
    previewContainer.appendChild(preview);
}

// Format file size for display
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Simulate upload progress
function simulateUploadProgress(progressBar) {
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress >= 100) {
            progress = 100;
            clearInterval(interval);
        }
        progressBar.style.width = progress + '%';
        progressBar.setAttribute('aria-valuenow', progress);
    }, 200);
}

// Notification system
function initializeNotifications() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentNode) {
                alert.classList.add('fade');
                setTimeout(() => alert.remove(), 300);
            }
        }, 5000);
    });
}

// Show notification
function showNotification(message, type = 'info', duration = 5000) {
    const notificationContainer = document.getElementById('notificationContainer') || 
                                 document.body;
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    notificationContainer.appendChild(notification);
    
    // Auto-dismiss
    setTimeout(() => {
        if (notification.parentNode) {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }
    }, duration);
}

// Utility functions
const Utils = {
    // Debounce function
    debounce: function(func, wait, immediate) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func(...args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func(...args);
        };
    },
    
    // Throttle function
    throttle: function(func, limit) {
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
    
    // Copy to clipboard
    copyToClipboard: function(text) {
        if (navigator.clipboard) {
            return navigator.clipboard.writeText(text).then(() => {
                showNotification('Copied to clipboard!', 'success', 2000);
            });
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            showNotification('Copied to clipboard!', 'success', 2000);
        }
    },
    
    // Format date
    formatDate: function(date, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        };
        return new Date(date).toLocaleDateString('en-US', { ...defaultOptions, ...options });
    },
    
    // Validate email
    isValidEmail: function(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
};

// Global error handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    showNotification('An unexpected error occurred. Please try again.', 'danger');
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    showNotification('A network error occurred. Please check your connection.', 'warning');
});

// Export utilities for use in other scripts
window.PoTechUtils = Utils;
window.showNotification = showNotification;

// Service Worker registration for PWA capabilities
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(err) {
                console.log('ServiceWorker registration failed');
            });
    });
}
