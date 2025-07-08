// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Select all favorite buttons
    const favoriteBtns = document.querySelectorAll('.favorite-btn');
    
    // Add click event listener to each button
    favoriteBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Get product ID from data attribute or from nearest parent with the data
            const productId = this.getAttribute('data-product-id');

            if (!productId) {
                showAlert('Error', 'Could not identify product', 'danger');
                return;
            }
            
            // Create form data
            const formData = new FormData();
            formData.append('product_id', productId);
            formData.append('csrfmiddlewaretoken', getCsrfToken());
            
            // Send AJAX request
            fetch('/wishlist/toggle/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Toggle heart icon class based on action
                    const heartIcon = this.querySelector('i');
                    if (data.action === 'added') {
                        // Item was added to wishlist
                        heartIcon.classList.remove('fa-heart-o');
                        heartIcon.classList.add('fa-heart');
                        this.classList.add('in-wishlist');
                        this.setAttribute('data-tip', 'Remove from Wishlist');
                    } else {
                        // Item was removed from wishlist
                        heartIcon.classList.remove('fa-heart');
                        heartIcon.classList.add('fa-heart-o');
                        this.classList.remove('in-wishlist');
                        this.setAttribute('data-tip', 'Add to Wishlist');
                    }
                } else {
                    // Show error message
                    showAlert('Not LoggedIn', data.message || 'Something went wrong', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('Error', 'Something went wrong. Please try again later.', 'danger');
            });
        });
    });
    
    // Function to get CSRF token from cookies
    function getCsrfToken() {
        const name = 'csrftoken';
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
    
    // Function to show alert messages
    function showAlert(title, message, type = 'danger') {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show wishlist-alert`;
        alertDiv.setAttribute('role', 'alert');
        
        // Add alert content with custom styling
        alertDiv.innerHTML = `
            <strong>${title}:</strong> &nbsp; ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Add alert to the top of the page
        document.body.insertBefore(alertDiv, document.body.firstChild);
        
        // Auto-dismiss alert after 5 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }, 5000);
    }
});