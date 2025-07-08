// community/static/community/js/save_post.js

document.addEventListener('DOMContentLoaded', function() {
    // Get all save buttons
    const saveButtons = document.querySelectorAll('.save-button');
    
    // Add click event listener to each button
    saveButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get post ID from data attribute
            const postId = this.dataset.postId;
            
            // Get CSRF token from cookie
            const csrftoken = getCookie('csrftoken');
            
            // Send AJAX request to toggle save status
            fetch(`/community/post/${postId}/save/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    // If response is not OK, check if it's an authentication issue
                    return response.json().then(data => {
                        if (data && data.authenticated === false) {
                            // Handle authentication error
                            window.location.href = data.login_url;
                            throw new Error('Authentication required');
                        }
                        throw new Error('Network response was not ok');
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                   if (data.is_saved) {
                        this.innerHTML = '<i class="bi bi-bookmark-check-fill me-1"></i> Saved';
                        this.classList.add('saved');
                    } else {
                        this.innerHTML = '<i class="bi bi-bookmark-fill me-1"></i> Save';
                        this.classList.remove('saved');
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });
    
    // Function to get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});