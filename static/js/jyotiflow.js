javascript
// JyotiFlow.ai - Basic Frontend Functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('🙏 JyotiFlow.ai frontend loaded successfully');
    
    // Add smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
    
    // Add basic form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            console.log('Form submitted:', this.action);
        });
    });
});