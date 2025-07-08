// homepage.js
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Masonry layout
    initMasonryGrid();
    
    // Handle image load events to recalculate grid
    handleImageLoad();
    
    // Add event listeners for save buttons
    //addSaveButtonListeners();
  });
  
  // Initialize Masonry grid layout
  function initMasonryGrid() {
    const grid = document.querySelector('.grid');
    
    // Check if we have a grid
    if (!grid) return;
    
    // Initialize Masonry
    const masonry = new Masonry(grid, {
      itemSelector: '.grid-item',
      columnWidth: '.grid-item',
      percentPosition: true,
      transitionDuration: '0.2s'
    });
    
    // Initial layout
    masonry.layout();
  }
  
  // Handle image load events to update grid layout
  function handleImageLoad() {
    const images = document.querySelectorAll('.pin-image');
    
    images.forEach(image => {
      if (image.complete) {
        resizeGridItem(image);
      } else {
        image.addEventListener('load', function() {
          resizeGridItem(image);
        });
      }
    });
  }
  
  // Resize grid item based on image height
  function resizeGridItem(image) {
    const gridItem = image.closest('.grid-item');
    const rowHeight = 10; // Default grid row height
    const rowSpan = Math.ceil((image.getBoundingClientRect().height + 60) / rowHeight); // Adding some space for text
    
    gridItem.style.gridRowEnd = 'span ' + rowSpan;
    
    // Update Masonry layout
    const grid = document.querySelector('.grid');
    if (grid) {
      const masonry = Masonry.data(grid);
      if (masonry) {
        masonry.layout();
      }
    }
  }
  
  /* Add event listeners for save buttons
  function addSaveButtonListeners() {
    const saveButtons = document.querySelectorAll('.save-btn');
    
    saveButtons.forEach(button => {
      button.addEventListener('click', function(e) {
        e.preventDefault();
        // Toggle saved state (for frontend demo only)
        if (button.classList.contains('saved')) {
          button.classList.remove('saved');
          button.textContent = 'Save';
        } else {
          button.classList.add('saved');
          button.textContent = 'Saved';
        }
      });
    });
   
      var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
      var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
          return new bootstrap.Tooltip(tooltipTriggerEl)
      })
  
  }*/