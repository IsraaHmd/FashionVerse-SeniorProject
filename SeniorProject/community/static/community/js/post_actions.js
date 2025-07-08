// Post options and deletion functionality - Add to a new file post_actions.js

document.addEventListener('DOMContentLoaded', function() {
    // Handle post options button clicks - Stop propagation to prevent immediate link clicks
    const postOptionsBtns = document.querySelectorAll('.post-options-btn');
    postOptionsBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            // Toggle the dropdown visibility explicitly (better UX than hover-only)
            const dropdown = this.nextElementSibling;
            dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
        });
    });

    // Handle clicks outside of dropdown to close them
    document.addEventListener('click', function(e) {
        const dropdowns = document.querySelectorAll('.post-options-dropdown');
        dropdowns.forEach(dropdown => {
            if (dropdown.style.display === 'block') {
                dropdown.style.display = 'none';
            }
        });
    });

    // Handle delete post button clicks
    const deletePostBtns = document.querySelectorAll('.delete-post-btn');
    const deletePostForm = document.getElementById('deletePostForm');
    
    deletePostBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const postId = this.getAttribute('data-post-id');
            
            // If using the modal
            if (deletePostForm) {
                // Set the form action dynamically based on post ID
                deletePostForm.action = `/community/delete_post/${postId}/`;
                
                // If not using Bootstrap's data-bs-toggle, manually show the modal
                if (!this.hasAttribute('data-bs-toggle')) {
                    const deletePostModal = new bootstrap.Modal(document.getElementById('deletePostModal'));
                    deletePostModal.show();
                }
            }
        });
    });

    // For profile page - Handle the hover effect for post cards
    const pinCards = document.querySelectorAll('.pin-card');
    pinCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            const headerActions = this.querySelector('.card-header-actions');
            if (headerActions) {
                headerActions.style.opacity = '1';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            const headerActions = this.querySelector('.card-header-actions');
            if (headerActions) {
                headerActions.style.opacity = '0';
            }
        });
    });
});