document.addEventListener('DOMContentLoaded', function() {
    // Get all reply forms
    const replyForms = document.querySelectorAll('.reply-form');
    
    // Handle reply form submissions
    replyForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            // Prevent default form submission
            event.preventDefault();
            
            // Get form data
            const formData = new FormData(this);
            const commentId = this.closest('.reply-container').id.replace('reply-container-', '');
            const repliesContainer = document.getElementById('replies-container-' + commentId);
            
            // Send AJAX request
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Add the new reply to the page
                    const replyHtml = createReplyElement(data.reply);
                    repliesContainer.insertAdjacentHTML('afterbegin', replyHtml);
                    
                    // Clear the form
                    this.reset();
                    
                    // Make sure the replies container is visible
                    repliesContainer.style.display = 'block';
                    
                    // Add event listener to the new delete button if present
                    const newDeleteBtn = repliesContainer.querySelector(`.delete-reply[data-reply-id="${data.reply.id}"]`);
                    if (newDeleteBtn) {
                        addDeleteReplyListener(newDeleteBtn);
                    }
                } else {
                    // Show error message
                    alert(data.error || 'An error occurred while adding your reply.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            });
        });
    });
    
    // Function to create a reply HTML element
    function createReplyElement(reply) {
        const profileImage = reply.user.profile_image 
            ? `<img src="${reply.user.profile_image}" alt="${reply.user.username}" class="profile-pic-small" width="20" height="20">`
            : `<span class="user-initial-small">${reply.user.initial}</span>`;
            
        const deleteButton = reply.is_owner 
            ? `<span class="delete-reply" data-reply-id="${reply.id}"><i class="bi bi-trash"></i></span>` 
            : '';
            
        return `
            <div class="reply" id="reply${reply.id}">
                <div class="reply-header">
                    <span class="reply-user">
                        ${profileImage}
                        ${reply.user.username}
                    </span>
                    ${deleteButton}
                </div>
                <p class="reply-text">
                    ${reply.text}
                </p>
                <span class="reply-date">${reply.added_at}</span>
            </div>
        `;
    }
    
    // Initialize delete reply buttons
    const deleteReplyBtns = document.querySelectorAll('.delete-reply');
    deleteReplyBtns.forEach(btn => {
        addDeleteReplyListener(btn);
    });
    
    // Function to add delete event listener to reply delete buttons
    function addDeleteReplyListener(btn) {
        btn.addEventListener('click', function() {
            const replyId = this.getAttribute('data-reply-id');
            const deleteForm = document.getElementById('deleteForm');
            deleteForm.action = deleteReplyUrl.replace('0', replyId);
            
            // Show delete confirmation modal
            const deleteConfirmModal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
            deleteConfirmModal.show();
        });
    }
});