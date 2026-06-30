/* mealKart - Global JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    // --- CSRF Fetch Helper Helper ---
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    window.csrfToken = getCookie('csrftoken') || document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    // --- Light/Dark Mode Theme Toggle ---
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const body = document.body;
    
    if (themeToggleBtn) {
        const themeIcon = themeToggleBtn.querySelector('.theme-icon');
        
        // Check saved theme or system preference
        const currentTheme = localStorage.getItem('theme');
        if (currentTheme === 'dark') {
            body.classList.remove('light-mode');
            body.classList.add('dark-mode');
            if (themeIcon) {
                themeIcon.classList.remove('fa-moon');
                themeIcon.classList.add('fa-sun');
            }
        } else {
            body.classList.remove('dark-mode');
            body.classList.add('light-mode');
            if (themeIcon) {
                themeIcon.classList.remove('fa-sun');
                themeIcon.classList.add('fa-moon');
            }
        }
        
        themeToggleBtn.addEventListener('click', function() {
            if (body.classList.contains('light-mode')) {
                body.classList.remove('light-mode');
                body.classList.add('dark-mode');
                localStorage.setItem('theme', 'dark');
                if (themeIcon) {
                    themeIcon.classList.remove('fa-moon');
                    themeIcon.classList.add('fa-sun');
                }
            } else {
                body.classList.remove('dark-mode');
                body.classList.add('light-mode');
                localStorage.setItem('theme', 'light');
                if (themeIcon) {
                    themeIcon.classList.remove('fa-sun');
                    themeIcon.classList.add('fa-moon');
                }
            }
        });
    }

    // --- Dropdown Management (Profile & Notifications) ---
    const profileBtn = document.getElementById('profile-menu-btn');
    const profileDropdown = document.getElementById('profile-dropdown');
    
    const notifBtn = document.getElementById('notif-toggle-btn');
    const notifDropdown = document.getElementById('notif-dropdown');

    if (profileBtn && profileDropdown) {
        profileBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            profileDropdown.classList.toggle('hidden');
            if (notifDropdown) notifDropdown.classList.add('hidden');
        });
    }

    if (notifBtn && notifDropdown) {
        notifBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            notifDropdown.classList.toggle('hidden');
            if (profileDropdown) profileDropdown.classList.add('hidden');
        });
    }

    // Close dropdowns on clicking outside
    document.addEventListener('click', function() {
        if (profileDropdown) profileDropdown.classList.add('hidden');
        if (notifDropdown) notifDropdown.classList.add('hidden');
    });

    // Prevent closing when clicking inside the dropdown content
    if (profileDropdown) {
        profileDropdown.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
    if (notifDropdown) {
        notifDropdown.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }

    // --- Auto-dismiss Toast Messages ---
    const messagesContainer = document.getElementById('django-messages-container');
    if (messagesContainer) {
        const alerts = messagesContainer.querySelectorAll('.toast-alert');
        alerts.forEach(alert => {
            setTimeout(() => {
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-20px)';
                alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
                setTimeout(() => alert.remove(), 400);
            }, 4000);
        });
    }
});
