document.addEventListener('DOMContentLoaded', function() {
    // Form elements
    const fileUpload = document.getElementById('fileUpload');
    const directUrlInput = document.getElementById('directUrlInput');
    const useUrlBtn = document.getElementById('useUrlBtn');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');
    const imagePreviewContainer = document.getElementById('imagePreviewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const changeImageBtn = document.getElementById('changeImageBtn');
    const postTitle = document.getElementById('postTitle');
    const postDescription = document.getElementById('postDescription');
    const categoryDropdown = document.getElementById('categoryDropdown');
    const selectedCategory = document.getElementById('selectedCategory');
    const categorySearch = document.getElementById('categorySearch');
    const commentsToggle = document.getElementById('commentsToggle');
    const savePostBtn = document.getElementById('savePostBtn');
    const backButton = document.getElementById('backButton');
    const postForm = document.getElementById('postForm');
    const dropArea = document.getElementById('uploadPlaceholder');
    // Get CSRF token for AJAX requests
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Check if we need to enable form fields (in case of returning with errors)
    const checkFormState = function() {
        const hasImageUrl = directUrlInput.value.trim() !== '';
        const hasImagePreview = imagePreviewContainer.style.display !== 'none';
        
        if (hasImageUrl || hasImagePreview) {
            enableFormFields();
        }
    };

    // Enable form fields
    const enableFormFields = function() {
        postTitle.disabled = false;
        postDescription.disabled = false;
        categoryDropdown.disabled = false;
        commentsToggle.disabled = false;
        savePostBtn.disabled = false;
    };

    // Disable form fields
    const disableFormFields = function() {
        postTitle.disabled = true;
        postDescription.disabled = true;
        categoryDropdown.disabled = true;
        commentsToggle.disabled = true;
        savePostBtn.disabled = true;
    };

    // Initialize form state
    checkFormState();

    // Handle file upload
    fileUpload.addEventListener('change', function(e) {
        if (this.files && this.files[0]) {
            const file = this.files[0];
            const reader = new FileReader();
            
            reader.onload = function(e) {
                imagePreview.src = e.target.result;
                uploadPlaceholder.style.display = 'none';
                imagePreviewContainer.style.display = 'block';
                
                // Clear URL input since we're using file upload
                directUrlInput.value = '';
                
                // Enable form fields
                enableFormFields();
            };
            
            reader.readAsDataURL(file);
        }
    });

    // Handle direct URL input
    useUrlBtn.addEventListener('click', function() {
        const url = directUrlInput.value.trim();
        if (url) {
            imagePreview.src = url;
            uploadPlaceholder.style.display = 'none';
            imagePreviewContainer.style.display = 'block';
            
            // Clear file input since we're using URL
            fileUpload.value = '';
            
            // Enable form fields
            enableFormFields();
        }
    });

    // Handle change image button
    // Modify the change image function to properly disable fields and check form state
    changeImageBtn.addEventListener('click', function(e) {
        e.preventDefault();
        const imageUrl = document.getElementById('directUrlInput').value.trim();
    
    
        // Hide the current image preview before opening the file dialog
        imagePreviewContainer.style.display = 'none';
        uploadPlaceholder.style.display = 'flex';

        // Disable form fields since we're back to image selection mode
        disableFormFields();

        // Trigger the file input click to allow uploading a new image'
        // If a URL is entered, don't open the file upload dialog
        if (!imageUrl) {
            fileUpload.click();
        }
        

        // Check the form state after making changes
        checkFormState();
    });

    // Make sure fields get disabled when dropping files fails
    dropArea.addEventListener('drop', function(e) {
        // If dropping fails or is cancelled
        if (!e.dataTransfer.files.length) {
            disableFormFields();
        }

        // Check form state after dropping or canceling
        checkFormState();
    });


    // Handle category search
    categorySearch.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const categoryItems = document.querySelectorAll('.dropdown-item-post:not(.create-new)');
        const dropdownMenu = document.querySelector('.dropdown-menu-post');
        const noResultsItem = dropdownMenu.querySelector('.no-results-item');
        let hasResults = false;
        
        categoryItems.forEach(function(item) {
            const categoryName = item.textContent.toLowerCase();
            if (categoryName.includes(searchTerm)) {
                item.style.display = 'block';
                hasResults = true;
            } else {
                item.style.display = 'none';
            }
        });
        
        // Remove existing "no results" item if it exists
        if (noResultsItem) {
            noResultsItem.remove();
        }
        
        // Show "no results" message if needed
        if (!hasResults && searchTerm) {
            const noResultsElement = document.createElement('li');
            noResultsElement.className = 'dropdown-item no-results-item';
            noResultsElement.innerHTML = `No results found. <a href="#" class="create-category-inline">Create "${searchTerm}"</a>`;
            
            // Insert before the divider
            const divider = dropdownMenu.querySelector('.dropdown-divider');
            dropdownMenu.insertBefore(noResultsElement, divider);
            
            // Add click handler to the inline create link
            noResultsElement.querySelector('.create-category-inline').addEventListener('click', function(e) {
                e.preventDefault();
                showCreateCategoryModal(searchTerm);
            });
        }
    });

    // Function to show create category modal
    function showCreateCategoryModal(categoryName = '') {
        const createCategoryModal = new bootstrap.Modal(document.getElementById('createCategoryModal'));
        document.getElementById('newCategoryName').value = categoryName;
        createCategoryModal.show();
    }

    // Handle category selection
    document.querySelectorAll('.dropdown-item-post:not(.create-new)').forEach(function(item) {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const categoryId = this.getAttribute('data-category-id');
            const categoryName = this.textContent;
            
            categoryDropdown.textContent = categoryName;
            selectedCategory.value = categoryId;
        });
    });

    // Handle create new category
    const createNewCategoryLink = document.querySelector('.dropdown-item.create-new');
    const createCategoryBtn = document.getElementById('createCategoryBtn');
    const newCategoryNameInput = document.getElementById('newCategoryName');
    
    // Add click event for create new category link
    if (createNewCategoryLink) {
        createNewCategoryLink.addEventListener('click', function(e) {
            e.preventDefault();
            showCreateCategoryModal(categorySearch.value);
        });
    }
    
    // Handle create category button click
    if (createCategoryBtn) {
        createCategoryBtn.addEventListener('click', function() {
            const categoryName = newCategoryNameInput.value.trim();
            if (!categoryName) {
                // Display error in modal
                alert('Category name cannot be empty');
                return;
            }
            
            // Create category via AJAX
            fetch(window.location.href, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                },
                body: new URLSearchParams({
                    'create_category': 'true',
                    'category_name': categoryName
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Add new category to dropdown if it doesn't exist
                    const dropdownMenu = document.querySelector('.dropdown-menu-post');
                    const divider = dropdownMenu.querySelector('.dropdown-divider');
                    let existingItem = null;
                    
                    // Check if category already exists in dropdown
                    document.querySelectorAll('.dropdown-item-post:not(.create-new)').forEach(item => {
                        if (item.getAttribute('data-category-id') == data.id) {
                            existingItem = item;
                        }
                    });
                    
                    if (!existingItem) {
                        const newItem = document.createElement('li');
                        newItem.innerHTML = `<a class="dropdown-item dropdown-item-post" href="#" data-category-id="${data.id}">${data.name}</a>`;
                        newItem.querySelector('a').addEventListener('click', function(e) {
                            e.preventDefault();
                            categoryDropdown.textContent = data.name;
                            selectedCategory.value = data.id;
                        });
                        
                        dropdownMenu.insertBefore(newItem, divider);
                    }
                    
                    // Select the new category
                    categoryDropdown.textContent = data.name;
                    selectedCategory.value = data.id;
                    
                    // Close modal
                    bootstrap.Modal.getInstance(document.getElementById('createCategoryModal')).hide();
                } else {
                    // Display error in modal
                    alert(data.error || 'An error occurred creating the category');
                }
            })
            .catch(error => {
                alert('Server error. Please try again.');
                console.error('Error creating category:', error);
            });
        });
    }

    // Handle Enter key in URL input
    directUrlInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            useUrlBtn.click();
        }
    });

   
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropArea.classList.add('highlight');
    }

    function unhighlight() {
        dropArea.classList.remove('highlight');
    }

    dropArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files && files.length) {
            fileUpload.files = files;
            const event = new Event('change');
            fileUpload.dispatchEvent(event);
        }
    }

    // Create Bootstrap modal for leave confirmation
    function createLeaveConfirmModal() {
        const modalDiv = document.createElement('div');
        modalDiv.className = 'modal fade';
        modalDiv.id = 'leaveConfirmModal';
        modalDiv.setAttribute('tabindex', '-1');
        modalDiv.setAttribute('aria-labelledby', 'leaveConfirmModalLabel');
        
        modalDiv.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="leaveConfirmModalLabel">Unsaved Changes</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        You have unsaved changes. Are you sure you want to leave this page?
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">No, stay on this page</button>
                        <button type="button" class="btn btn-danger" id="confirmLeaveBtn">Yes, go back to community</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modalDiv);
        
        // Add event listener to the confirm button
        document.getElementById('confirmLeaveBtn').addEventListener('click', function() {
            window.location.href = '/community/'; // Fixed link to community page
        });
        
        return new bootstrap.Modal(modalDiv);
    }

    // Confirm before leaving page if form has been modified
    const formElements = [postTitle, postDescription, fileUpload, directUrlInput, commentsToggle];
    let formModified = false;
    let leaveConfirmModal = null;

    formElements.forEach(element => {
        element.addEventListener('change', function() {
            formModified = true;
        });
    });

    // Also mark form as modified if category is selected
    document.querySelectorAll('.dropdown-item-post').forEach(item => {
        item.addEventListener('click', function() {
            formModified = true;
        });
    });

    // Handle back button with modal
    backButton.addEventListener('click', function(e) {
        e.preventDefault();
        if (formModified) {
            if (!leaveConfirmModal) {
                leaveConfirmModal = createLeaveConfirmModal();
            }
            leaveConfirmModal.show();
        } else {
            window.location.href = this.getAttribute('href') || '/';
        }
    });

    // Fix form resubmission issue with category
    // Make sure the selected category value is properly set when the page loads with errors
    const currentCategory = categoryDropdown.textContent.trim();
    if (currentCategory && currentCategory !== 'Choose a Category') {
        selectedCategory.value = selectedCategory.value || document.querySelector(`.dropdown-item-post[data-category-id]`).getAttribute('data-category-id');
    }
});