// Edit post JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Elements for image upload/preview
    const fileUpload = document.getElementById('fileUpload');
    const directUrlInput = document.getElementById('directUrlInput');
    const useUrlBtn = document.getElementById('useUrlBtn');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');
    const imagePreviewContainer = document.getElementById('imagePreviewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const changeImageBtn = document.getElementById('changeImageBtn');
    
    // Form elements
    const postForm = document.getElementById('postForm');
    const postTitle = document.getElementById('postTitle');
    const postDescription = document.getElementById('postDescription');
    const categoryDropdown = document.getElementById('categoryDropdown');
    const selectedCategory = document.getElementById('selectedCategory');
    const categorySearch = document.getElementById('categorySearch');
    const savePostBtn = document.getElementById('savePostBtn');
    
    // Initialize state based on existing post data
    const hasExistingImage = imagePreview && imagePreview.getAttribute('src') && 
                            imagePreview.getAttribute('src').trim() !== '';

    // New load: Function to handle when image loads
    function handleImageLoad() {
        imagePreview.classList.add('loaded');
    }
    // Check if image is already loaded
    if (imagePreview.complete) {
        handleImageLoad();
    } else {
        // Add load event listener
        imagePreview.addEventListener('load', handleImageLoad);
    }

    // Set initial visibility for image containers
    if (hasExistingImage) {
        uploadPlaceholder.style.display = 'none';
        imagePreviewContainer.style.display = 'block';
    } else {
        uploadPlaceholder.style.display = 'flex';
        imagePreviewContainer.style.display = 'none';
    }
    
    // File upload handler
    if (fileUpload) {
        fileUpload.addEventListener('change', function(e) {
            if (fileUpload.files && fileUpload.files[0]) {
                const file = fileUpload.files[0];
                
                // Create URL for preview
                const objectUrl = URL.createObjectURL(file);
                imagePreview.src = objectUrl;
                
                // Show preview, hide placeholder
                uploadPlaceholder.style.display = 'none';
                imagePreviewContainer.style.display = 'block';
                
                // Clear URL input as we're using file upload
                directUrlInput.value = '';
            }
        });
    }
    
    // URL input handler
    if (useUrlBtn) {
        useUrlBtn.addEventListener('click', function() {
            const url = directUrlInput.value.trim();
            if (url) {
                imagePreview.src = url;
                
                // Show preview, hide placeholder
                uploadPlaceholder.style.display = 'none';
                imagePreviewContainer.style.display = 'block';
                
                // Clear file input as we're using URL
                if (fileUpload) {
                    fileUpload.value = '';
                }
            }
        });
    }
    
    // Change image button handler
    if (changeImageBtn) {
        changeImageBtn.addEventListener('click', function() {
            // Hide preview, show upload placeholder
            uploadPlaceholder.style.display = 'flex';
            imagePreviewContainer.style.display = 'none';
            
            // Clear existing image selection
            if (fileUpload) {
                fileUpload.value = '';
            }
            //directUrlInput.value = '';
        });
    }
    
    // Category dropdown item selection
    document.querySelectorAll('.dropdown-item-post').forEach(item => {
        if (!item.classList.contains('create-new')) {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                const id = this.getAttribute('data-category-id');
                const name = this.textContent;
                
                categoryDropdown.textContent = name;
                selectedCategory.value = id;
            });
        }
    });
    
    // Create new category
    const createNewCategoryLinks = document.querySelectorAll('.dropdown-item.create-new');
    const createCategoryModal = new bootstrap.Modal(document.getElementById('createCategoryModal'));
    const createCategoryBtn = document.getElementById('createCategoryBtn');
    const newCategoryName = document.getElementById('newCategoryName');
    
    createNewCategoryLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            createCategoryModal.show();
        });
    });
    
    if (createCategoryBtn) {
        createCategoryBtn.addEventListener('click', function() {
            const categoryName = newCategoryName.value.trim();
            
            if (!categoryName) {
                // Show error
                return;
            }
            
            // AJAX request to create category
            fetch(window.location.pathname, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: new URLSearchParams({
                    'create_category': 'true',
                    'category_name': categoryName
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Add new category to dropdown
                    const dropdownMenu = document.querySelector('.dropdown-menu-post');
                    const existingItem = dropdownMenu.querySelector(`[data-category-id="${data.id}"]`);
                    if (!existingItem) {
                        const newItem = document.createElement('li');
                        newItem.innerHTML = `<a class="dropdown-item dropdown-item-post" href="#" data-category-id="${data.id}">${data.name}</a>`;
                        
                        // Insert before the divider
                        const divider = dropdownMenu.querySelector('.dropdown-divider');
                        dropdownMenu.insertBefore(newItem, divider);
                        
                        // Add event listener to the new item
                        newItem.querySelector('a').addEventListener('click', function(e) {
                            e.preventDefault();
                            categoryDropdown.textContent = data.name;
                            selectedCategory.value = data.id;
                        });
                    }
                    
                    // Select the new category
                    categoryDropdown.textContent = data.name;
                    selectedCategory.value = data.id;
                    
                    // Hide modal
                    createCategoryModal.hide();
                    
                    // Reset input
                    newCategoryName.value = '';
                } else {
                    // Show error
                    alert(data.error || 'An error occurred creating the category');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            });
        });
    }
    
    // Category search functionality
    if (categorySearch) {
        categorySearch.addEventListener('input', function() {
            const searchValue = this.value.toLowerCase();
            
            // Filter dropdown items
            document.querySelectorAll('.dropdown-item-post').forEach(item => {
                if (item.classList.contains('create-new')) return;
                
                const text = item.textContent.toLowerCase();
                const li = item.parentElement;
                
                if (text.includes(searchValue)) {
                    li.style.display = '';
                } else {
                    li.style.display = 'none';
                }
            });
        });
    }
    
    // Form validation
    if (postForm) {
        postForm.addEventListener('submit', function(e) {
            let isValid = true;
            
            // Clear previous error messages
            document.querySelectorAll('.error-message').forEach(el => el.remove());
            document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
            
            // Validate title
            if (!postTitle.value.trim()) {
                isValid = false;
                postTitle.classList.add('is-invalid');
                const errorMsg = document.createElement('div');
                errorMsg.className = 'error-message';
                errorMsg.innerText = 'Title is required';
                postTitle.parentNode.appendChild(errorMsg);
            }
            
            // Validate image (only if no existing image OR if changed to empty)
            const hasImageUpload = fileUpload && fileUpload.files && fileUpload.files.length > 0;
            const hasImageUrl = directUrlInput && directUrlInput.value.trim() !== '';
            const hasImage = hasImageUpload || hasImageUrl || hasExistingImage;
            
            if (!hasImage) {
                isValid = false;
                const errorMsg = document.createElement('div');
                errorMsg.className = 'error-message';
                errorMsg.innerText = 'Either an image file or URL is required';
                
                if (directUrlInput) {
                    directUrlInput.classList.add('is-invalid');
                    directUrlInput.parentNode.appendChild(errorMsg);
                } else {
                    const uploadArea = document.querySelector('.image-upload-area');
                    if (uploadArea) {
                        uploadArea.appendChild(errorMsg);
                    }
                }
            }
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    }
});