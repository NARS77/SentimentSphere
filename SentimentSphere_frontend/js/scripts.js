/*!
* SentimentSphere - Frontend Scripts
* v1.0
*/

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap components
    initializeBootstrapComponents();
    
    // Navigation - Shrink on scroll
    initNavbarShrink();
    
    // Smooth scrolling for navigation links
    initSmoothScrolling();
    
    // Add animations for sections when scrolling
    initScrollAnimations();
    
    // Initialize form validation and submission
    initContactForm();
});

/**
 * Initialize Bootstrap components
 */
function initializeBootstrapComponents() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Navbar shrink function
 */
function initNavbarShrink() {
    const mainNav = document.querySelector('#mainNav');
    if (mainNav) {
        const navbarShrink = function () {
            const scrollTop = window.pageYOffset;
            if (scrollTop === 0) {
                mainNav.classList.remove('navbar-shrink');
            } else {
                mainNav.classList.add('navbar-shrink');
            }
        };
        
        // Shrink the navbar when page is scrolled
        document.addEventListener('scroll', navbarShrink);
        
        // Shrink the navbar when page is loaded if not at the top
        navbarShrink();
        
        // Collapse responsive navbar when toggler is clicked
        const navbarToggler = document.querySelector('.navbar-toggler');
        const responsiveNavItems = document.querySelectorAll('.navbar-nav .nav-link');
        
        if (navbarToggler) {
            responsiveNavItems.forEach(function (responsiveNavItem) {
                responsiveNavItem.addEventListener('click', function () {
                    if (window.innerWidth < 992) {
                        navbarToggler.click();
                    }
                });
            });
        }
    }
}

/**
 * Smooth scrolling for navigation links
 */
function initSmoothScrolling() {
    document.querySelectorAll('a.nav-link[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 72, // Adjust for navbar height
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * Initialize scroll animations
 */
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.feature-item, .pricing-card, .team-member');
    
    if (animatedElements.length > 0) {
        const animateOnScroll = function() {
            animatedElements.forEach(element => {
                const elementPosition = element.getBoundingClientRect().top;
                const windowHeight = window.innerHeight;
                
                if (elementPosition < windowHeight * 0.9) {
                    element.classList.add('fade-in');
                }
            });
        };
        
        // Run once on page load
        animateOnScroll();
        
        // Run on scroll
        window.addEventListener('scroll', animateOnScroll);
    }
}

/**
 * Initialize contact form validation and submission
 */
function initContactForm() {
    const contactForm = document.getElementById('contactForm');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Basic form validation
            let isValid = true;
            const requiredFields = contactForm.querySelectorAll('[required]');
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
                
                // Email validation
                if (field.type === 'email' && field.value.trim()) {
                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (!emailRegex.test(field.value.trim())) {
                        isValid = false;
                        field.classList.add('is-invalid');
                    }
                }
            });
            
            if (isValid) {
                // In a real application, this would send the form data to a server
                // For demo purposes, we'll just show a success message
                contactForm.innerHTML = `
                    <div class="alert alert-success" role="alert">
                        <h4 class="alert-heading">Thank you for your message!</h4>
                        <p>We've received your inquiry and will get back to you shortly.</p>
                    </div>
                `;
                
                // Scroll to the success message
                window.scrollTo({
                    top: contactForm.offsetTop - 100,
                    behavior: 'smooth'
                });
            }
        });
        
        // Remove validation styling on input
        contactForm.querySelectorAll('input, textarea, select').forEach(field => {
            field.addEventListener('input', function() {
                if (field.value.trim()) {
                    field.classList.remove('is-invalid');
                }
            });
        });
    }
}

/**
 * Handle login form (on login page if exists)
 */
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Basic validation
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();
        
        if (!username || !password) {
            const alertElement = document.createElement('div');
            alertElement.className = 'alert alert-danger';
            alertElement.textContent = 'Please enter both username and password';
            
            const existingAlert = loginForm.querySelector('.alert');
            if (existingAlert) {
                existingAlert.remove();
            }
            
            loginForm.prepend(alertElement);
            return;
        }
        
        // In a real application, this would authenticate with the server
        // For demo purposes, we'll just redirect to the demo dashboard
        window.location.href = 'demo-dashboard.html';
    });
}

/**
 * Initialize demo dashboard features if on the demo page
 */
if (document.querySelector('.demo-dashboard')) {
    initDemoCharts();
}

/**
 * Create demo charts using Chart.js
 */
function initDemoCharts() {
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded');
        return;
    }
    
    // Set default Chart.js options
    Chart.defaults.global.defaultFontFamily = 'Nunito, sans-serif';
    Chart.defaults.global.defaultFontColor = '#858796';
    
    // Sentiment Distribution Chart
    const sentimentChart = document.getElementById('sentimentDistributionChart');
    if (sentimentChart) {
        new Chart(sentimentChart, {
            type: 'doughnut',
            data: {
                labels: ['Positive', 'Negative', 'Neutral', 'Feature Request', 'Bug Report'],
                datasets: [{
                    data: [55, 30, 15, 10, 8],
                    backgroundColor: ['#1cc88a', '#e74a3b', '#858796', '#4e73df', '#f6c23e'],
                    hoverBackgroundColor: ['#17a673', '#be3025', '#6e707e', '#2e59d9', '#dda20a'],
                    hoverBorderColor: 'rgba(234, 236, 244, 1)',
                }],
            },
            options: {
                maintainAspectRatio: false,
                tooltips: {
                    backgroundColor: 'rgb(255,255,255)',
                    bodyFontColor: '#858796',
                    borderColor: '#dddfeb',
                    borderWidth: 1,
                    xPadding: 15,
                    yPadding: 15,
                    displayColors: false,
                    caretPadding: 10,
                },
                legend: {
                    display: true,
                    position: 'bottom'
                },
                cutoutPercentage: 70,
            },
        });
    }
    
    // Feedback Over Time Chart
    const feedbackTimeChart = document.getElementById('feedbackTimeChart');
    if (feedbackTimeChart) {
        // Generate demo data for last 7 days
        const dates = [];
        const positiveData = [];
        const negativeData = [];
        
        const today = new Date();
        for (let i = 6; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(today.getDate() - i);
            dates.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
            
            // Generate random data
            positiveData.push(Math.floor(Math.random() * 20) + 10);
            negativeData.push(Math.floor(Math.random() * 10) + 5);
        }
        
        new Chart(feedbackTimeChart, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Positive Feedback',
                    lineTension: 0.3,
                    backgroundColor: 'rgba(28, 200, 138, 0.1)',
                    borderColor: 'rgba(28, 200, 138, 1)',
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(28, 200, 138, 1)',
                    pointBorderColor: 'rgba(28, 200, 138, 1)',
                    pointHoverRadius: 5,
                    pointHoverBackgroundColor: 'rgba(28, 200, 138, 1)',
                    pointHoverBorderColor: 'rgba(28, 200, 138, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2,
                    data: positiveData,
                },
                {
                    label: 'Negative Feedback',
                    lineTension: 0.3,
                    backgroundColor: 'rgba(231, 74, 59, 0.1)',
                    borderColor: 'rgba(231, 74, 59, 1)',
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(231, 74, 59, 1)',
                    pointBorderColor: 'rgba(231, 74, 59, 1)',
                    pointHoverRadius: 5,
                    pointHoverBackgroundColor: 'rgba(231, 74, 59, 1)',
                    pointHoverBorderColor: 'rgba(231, 74, 59, 1)',
                    pointHitRadius: 10,
                    pointBorderWidth: 2,
                    data: negativeData,
                }],
            },
            options: {
                maintainAspectRatio: false,
                layout: {
                    padding: {
                        left: 10,
                        right: 25,
                        top: 25,
                        bottom: 0
                    }
                },
                scales: {
                    xAxes: [{
                        time: {
                            unit: 'date'
                        },
                        gridLines: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            maxTicksLimit: 7
                        }
                    }],
                    yAxes: [{
                        ticks: {
                            maxTicksLimit: 5,
                            padding: 10,
                            beginAtZero: true
                        },
                        gridLines: {
                            color: 'rgb(234, 236, 244)',
                            zeroLineColor: 'rgb(234, 236, 244)',
                            drawBorder: false,
                            borderDash: [2],
                            zeroLineBorderDash: [2]
                        }
                    }],
                },
                legend: {
                    display: true,
                    position: 'bottom'
                },
                tooltips: {
                    backgroundColor: 'rgb(255,255,255)',
                    bodyFontColor: '#858796',
                    titleMarginBottom: 10,
                    titleFontColor: '#6e707e',
                    titleFontSize: 14,
                    borderColor: '#dddfeb',
                    borderWidth: 1,
                    xPadding: 15,
                    yPadding: 15,
                    displayColors: false,
                    intersect: false,
                    mode: 'index',
                    caretPadding: 10
                }
            }
        });
    }
    
    // Source Distribution Chart
    const sourceChart = document.getElementById('sourceDistributionChart');
    if (sourceChart) {
        new Chart(sourceChart, {
            type: 'bar',
            data: {
                labels: ['Google Play', 'App Store', 'Website', 'Instagram', 'Twitter'],
                datasets: [{
                    label: 'Feedback Count',
                    backgroundColor: '#4e73df',
                    hoverBackgroundColor: '#2e59d9',
                    data: [48, 35, 25, 20, 15],
                }],
            },
            options: {
                maintainAspectRatio: false,
                layout: {
                    padding: {
                        left: 10,
                        right: 25,
                        top: 25,
                        bottom: 0
                    }
                },
                scales: {
                    xAxes: [{
                        gridLines: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            maxTicksLimit: 7
                        },
                        maxBarThickness: 25,
                    }],
                    yAxes: [{
                        ticks: {
                            min: 0,
                            maxTicksLimit: 5,
                            padding: 10,
                        },
                        gridLines: {
                            color: 'rgb(234, 236, 244)',
                            zeroLineColor: 'rgb(234, 236, 244)',
                            drawBorder: false,
                            borderDash: [2],
                            zeroLineBorderDash: [2]
                        }
                    }],
                },
                legend: {
                    display: false
                },
                tooltips: {
                    titleMarginBottom: 10,
                    titleFontColor: '#6e707e',
                    titleFontSize: 14,
                    backgroundColor: 'rgb(255,255,255)',
                    bodyFontColor: '#858796',
                    borderColor: '#dddfeb',
                    borderWidth: 1,
                    xPadding: 15,
                    yPadding: 15,
                    displayColors: false,
                    caretPadding: 10,
                }
            }
        });
    }
}