/**
 * Main JavaScript file for the AI Story Generator application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Add event listener for mobile menu toggle
    const menuToggle = document.querySelector('.menu-toggle');
    if (menuToggle) {
        menuToggle.addEventListener('click', toggleMobileMenu);
    }
    
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add fade-in animation for elements
    animateOnScroll();
    window.addEventListener('scroll', animateOnScroll);
});

/**
 * Initialize tooltips
 */
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[title]');
    
    tooltipElements.forEach(element => {
        const tooltipText = element.getAttribute('title');
        element.setAttribute('data-tooltip', tooltipText);
        element.removeAttribute('title');
        
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

/**
 * Show tooltip
 * @param {Event} e - Mouse event
 */
function showTooltip(e) {
    const tooltipText = this.getAttribute('data-tooltip');
    
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = tooltipText;
    
    document.body.appendChild(tooltip);
    
    const rect = this.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    
    tooltip.style.top = `${rect.top - tooltipRect.height - 10 + window.scrollY}px`;
    tooltip.style.left = `${rect.left + (rect.width / 2) - (tooltipRect.width / 2) + window.scrollX}px`;
    
    this.tooltip = tooltip;
}

/**
 * Hide tooltip
 */
function hideTooltip() {
    if (this.tooltip) {
        document.body.removeChild(this.tooltip);
        this.tooltip = null;
    }
}

/**
 * Toggle mobile menu
 */
function toggleMobileMenu() {
    const nav = document.querySelector('nav');
    nav.classList.toggle('active');
    
    const isActive = nav.classList.contains('active');
    this.setAttribute('aria-expanded', isActive);
}

/**
 * Animate elements when they come into view
 */
function animateOnScroll() {
    const elements = document.querySelectorAll('.animate-on-scroll');
    
    elements.forEach(element => {
        const position = element.getBoundingClientRect();
        
        // Check if element is in viewport
        if (position.top < window.innerHeight && position.bottom >= 0) {
            element.classList.add('animated');
        }
    });
}

/**
 * Format a date string
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date string
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

/**
 * Truncate text to a specified length
 * @param {string} text - Text to truncate
 * @param {number} length - Maximum length
 * @returns {string} Truncated text
 */
function truncateText(text, length) {
    if (text.length <= length) return text;
    return text.substring(0, length) + '...';
}

/**
 * Show an alert message
 * @param {string} message - Message to display
 * @param {string} type - Alert type (success, error, warning, info)
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type}`;
    alertContainer.textContent = message;
    
    document.body.appendChild(alertContainer);
    
    // Add visible class after a small delay to trigger animation
    setTimeout(() => {
        alertContainer.classList.add('visible');
    }, 10);
    
    // Remove the alert after 5 seconds
    setTimeout(() => {
        alertContainer.classList.remove('visible');
        
        // Remove from DOM after animation completes
        setTimeout(() => {
            document.body.removeChild(alertContainer);
        }, 300);
    }, 5000);
}

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} Success status
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (err) {
        console.error('Failed to copy text: ', err);
        return false;
    }
}
