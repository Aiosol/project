// CRM Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Mark notification as read on click
    document.querySelectorAll('.notification-dropdown .dropdown-item').forEach(function(item) {
        item.addEventListener('click', function(e) {
            // Get notification ID from data attribute
            var notificationId = this.dataset.notificationId;
            if (notificationId) {
                // Send AJAX request to mark as read
                fetch('/crm/notifications/mark-read/' + notificationId + '/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Remove unread class
                        this.classList.remove('unread');
                    }
                })
                .catch(error => console.error('Error:', error));
            }
        });
    });

    // Function to get CSRF token from cookies
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

    // DataTables initialization (if present)
    if (typeof $.fn.DataTable !== 'undefined' && $('#dataTable').length > 0) {
        $('#dataTable').DataTable({
            order: [[0, 'desc']] // Sort by first column (Order ID) descending
        });
    }
});