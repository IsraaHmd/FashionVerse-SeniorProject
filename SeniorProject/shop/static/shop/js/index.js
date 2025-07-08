document.addEventListener('DOMContentLoaded', function() {
    /* new */
    document.querySelectorAll('.quick-view').forEach(button => {
        button.addEventListener('click', function() {
          const productUrl = this.getAttribute('data-product-url');
          if (productUrl) {
            window.location.href = productUrl;
          }
        });
      });
    /*-------------------------------- Responsiveness: TOGGLE THE NAV MENU FOR SMALLER SCREENS-------------------*/
    // Mobile Nav Toggle Function
        const mobileNavToggleBtn = document.querySelector('.mobile-nav-toggle');
        const body = document.querySelector('body');
        const headerMenuContainer = document.querySelector('.header-menu-container')
        
        // Toggle the mobile nav
        function mobileNavToogle() {
            body.classList.toggle('mobile-nav-active');  // Toggle active class on body
            mobileNavToggleBtn.classList.toggle('bi-list');  // Toggle hamburger icon
            mobileNavToggleBtn.classList.toggle('bi-x');  // Toggle cross icon
            headerMenuContainer.classList.toggle('header-menu-container-nav-active');
        }
        mobileNavToggleBtn.addEventListener('click', mobileNavToogle);
        document.querySelectorAll('#navmenu a').forEach(navmenuItem => {
            navmenuItem.addEventListener('click', () => {
                if (body.classList.contains('mobile-nav-active')) {
                    mobileNavToogle();
                }
            });
        });
    //-------------------------------------------------------NEW SENIOR:
    /* =========================================Testimonials section ============================================*/
    // keep the video on
    const backgroundVideo = document.getElementById('background-video');

    // Keep the video playing no matter what
    function ensureVideoPlays() {
        if (backgroundVideo && backgroundVideo.paused) {
            backgroundVideo.play();
        }
    }

    // Check video playback status regularly
    setInterval(ensureVideoPlays, 1000);

    // Add event listeners to the entire document to prevent pausing
    document.addEventListener('mouseover', function() {
        ensureVideoPlays();
    });

    document.addEventListener('click', function() {
        ensureVideoPlays();
    });

    // Specifically target the testimonial section
    const testimonialSection = document.querySelector('.section-test');
    if (testimonialSection) {
        testimonialSection.addEventListener('mouseover', function(e) {
            e.stopPropagation();
            ensureVideoPlays();
        });
        
        testimonialSection.addEventListener('click', function(e) {
            e.stopPropagation();
            ensureVideoPlays();
        });
    }
    // end of keep the video on
    const slides = document.querySelectorAll('.testimonial-slide');
    const dots = document.querySelectorAll('.w-slider-dot');
    const prevButton = document.querySelector('.slider-arrow.left');
    const nextButton = document.querySelector('.slider-arrow.w-slider-arrow-right');
    
    let currentSlide = 0;
    
    // Initialize
    slides[0].classList.add('active');
    
    // Function to show a specific slide
    function showSlide(index) {
        // Hide all slides
        slides.forEach(slide => {
        slide.classList.add('hidden');
        slide.classList.remove('active');
        });
        
        // Show the selected slide
        slides[index].classList.remove('hidden');
        slides[index].classList.add('active');
        
        // Update active dot
        dots.forEach(dot => dot.classList.remove('w-active'));
        dots[index].classList.add('w-active');
        
        // Update current slide
        currentSlide = index;
    }
    
    // Previous slide
    prevButton.addEventListener('click', function() {
        const newIndex = (currentSlide - 1 + slides.length) % slides.length;
        showSlide(newIndex);
    });
    
    // Next slide
    nextButton.addEventListener('click', function() {
        const newIndex = (currentSlide + 1) % slides.length;
        showSlide(newIndex);
    });
    
    // Dot navigation
    dots.forEach(dot => {
        dot.addEventListener('click', function() {
        const index = parseInt(this.getAttribute('data-index'));
        showSlide(index);
        });
    });
    
    // Show circles on hover
    const slider = document.querySelector('.testimonial-slider');
    
    slider.addEventListener('mousemove', function(e) {
        const sliderRect = slider.getBoundingClientRect();
        const x = e.clientX - sliderRect.left;
        const y = e.clientY - sliderRect.top;
        const sliderWidth = sliderRect.width;
        
        // Get the arrow elements
        const leftArrow = document.querySelector('.slider-arrow.left');
        const rightArrow = document.querySelector('.slider-arrow.w-slider-arrow-right');
        
        // Show arrows based on which half the mouse is in
        if (x < sliderWidth / 2) {
        // Show left arrow and position it where the mouse is
        leftArrow.style.opacity = '1';
        rightArrow.style.opacity = '0';
        
        // Position the arrow at the mouse position (with some offset)
        leftArrow.style.left = (x - 50) + 'px'; 
        leftArrow.style.top = (y - 50) + 'px';
        leftArrow.style.transform = 'none'; // Remove default centering
        } else {
        // Show right arrow and position it where the mouse is
        leftArrow.style.opacity = '0';
        rightArrow.style.opacity = '1';
        
        // Position the arrow at the mouse position (with some offset)
        rightArrow.style.left = (x - 50) + 'px';
        rightArrow.style.top = (y - 50) + 'px';
        rightArrow.style.transform = 'none'; // Remove default centering
        }
    });
            
    // Hide arrows when mouse leaves slider
    slider.addEventListener('mouseleave', function() {
        prevButton.style.opacity = '0';
        nextButton.style.opacity = '0';
    });
    
    const sliderContent = document.querySelectorAll('.testimonial-content');

    // Add event listeners to each content area
    sliderContent.forEach(content => {
        content.addEventListener('mouseenter', function() {
        // Hide both arrows when hovering directly over content
        document.querySelector('.slider-arrow.left').style.opacity = '0';
        document.querySelector('.slider-arrow.w-slider-arrow-right').style.opacity = '0';
        });
        
        content.addEventListener('mouseleave', function() {
        // Let the main mousemove handler take over again
        // We don't need to do anything here as the main handler will update
        });
    });

    //---------------------------------------- Search
    const searchTrigger = document.getElementById('searchTrigger');
    const searchOverlay = document.getElementById('searchOverlay');
    const searchClose = document.getElementById('searchClose');
    const searchInput = document.getElementById('searchInput');
    
    // Open search overlay
    searchTrigger.addEventListener('click', (e) => {
        e.preventDefault();
        searchOverlay.style.display = 'flex';
        
        // Delay to allow the display:flex to take effect before adding active class
        setTimeout(() => {
            searchOverlay.classList.add('active');
            document.body.style.overflow = 'hidden'; // Prevent scrolling
            searchInput.focus(); // Focus the input
        }, 10);
    });
    
    // Close search overlay
    searchClose.addEventListener('click', () => {
        closeSearchOverlay();
    });
    
    // Close when clicking outside search box on mobile
    searchOverlay.addEventListener('click', (e) => {
        if (e.target === searchOverlay && window.innerWidth < 1200) {
            closeSearchOverlay();
        }
    });
    
    // Function to close the search overlay
    function closeSearchOverlay() {
        searchOverlay.classList.remove('active');
        
        // Wait for the transition to complete before hiding the overlay
        setTimeout(() => {
            searchOverlay.style.display = 'none';
            document.body.style.overflow = ''; // Restore scrolling
        }, 300);
    }
    
    // Close on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && searchOverlay.style.display === 'flex') {
            closeSearchOverlay();
        }
    });
    
    // Form submission
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            const query = searchInput.value.trim();
            if (query) {
                window.location.href = `/search/?q=${encodeURIComponent(query)}`;
            }
        }
    });
    //---------------------------------------- End of Search

    //----------------------------------------- Latest Products:
    // Carousel functionality
    const carouselItems = document.querySelectorAll('.carousel-item');
    const indicators = document.querySelectorAll('.carousel-indicator');
    let currentIndex = 0;
    
    // Store carousel state in object to avoid issues with clearInterval scope
    const carouselState = {
        interval: null,
        isScrolling: false,
        scrollTimeout: null
    };
    
    // Function to update carousel
    function updateCarousel(index) {
        // Remove all classes
        carouselItems.forEach(item => {
        item.classList.remove('active', 'prev');
        });
        
        indicators.forEach(indicator => {
        indicator.classList.remove('active');
        });
        
        // Add active class to current item
        carouselItems[index].classList.add('active');
        indicators[index].classList.add('active');
        
        // Add prev class to previous item
        const prevIndex = (index - 1 + carouselItems.length) % carouselItems.length;
        carouselItems[prevIndex].classList.add('prev');
    }
    
    // Start automatic rotation
    function startCarouselRotation() {
        // Clear any existing interval first
        if (carouselState.interval) {
        clearInterval(carouselState.interval);
        }
        
        carouselState.interval = setInterval(() => {
        if (!carouselState.isScrolling) {
            currentIndex = (currentIndex + 1) % carouselItems.length;
            updateCarousel(currentIndex);
        }
        }, 5000); // 5 seconds between changes
    }
    
    // Set up click handlers for indicators
    indicators.forEach((indicator, index) => {
        indicator.addEventListener('click', function() {
        currentIndex = index;
        updateCarousel(currentIndex);
        
        // Reset rotation timer after manual interaction
        startCarouselRotation();
        });
    });
    
    // Hover effect to pause carousel
    const carouselElement = document.querySelector('.athletics-carousel');
    carouselElement.addEventListener('mouseenter', function() {
        if (carouselState.interval) {
        clearInterval(carouselState.interval);
        }
    });
    
    carouselElement.addEventListener('mouseleave', function() {
        startCarouselRotation();
    });
    
    // Product card hover effects
    const productCards = document.querySelectorAll('.product-card');
    productCards.forEach(card => {
        const buttons = card.querySelector('.product-buttons');
        
        card.addEventListener('mouseenter', function() {
        buttons.style.opacity = '1';
        buttons.style.bottom = '20px';
        });
        
        card.addEventListener('mouseleave', function() {
        buttons.style.opacity = '0';
        buttons.style.bottom = '-50px';
        });
    });
    
    // Scroll behavior for sticky carousel
    function handleScroll() {
        // Set scrolling flag to prevent carousel changing during scroll
        carouselState.isScrolling = true;
        
        // Clear previous timeout if exists
        if (carouselState.scrollTimeout) {
        clearTimeout(carouselState.scrollTimeout);
        }
        
        // Set timeout to mark end of scrolling
        carouselState.scrollTimeout = setTimeout(() => {
        carouselState.isScrolling = false;
        }, 100);
        
        const featuredSection = document.querySelector('.featured-products-section');
        const carousel = document.querySelector('.athletics-carousel');
        const productsGrid = document.querySelector('.products-grid');
        
        if (window.innerWidth >= 992 && featuredSection && carousel && productsGrid) {
        // Save the current height before position changes to prevent jumps
        const currentHeight = carousel.getBoundingClientRect().height;
        
        const productsGridRect = productsGrid.getBoundingClientRect();
        const productsGridBottom = productsGridRect.bottom;
        
        // If the bottom of products grid is still visible, keep carousel fixed
        if (productsGridBottom > window.innerHeight) {
            if (carousel.style.position !== 'sticky') {
            carousel.style.position = 'sticky';
            carousel.style.top = '0';
            }
        } 
        // When products are fully scrolled, let the carousel scroll with the page
        else {
            const carouselHeight = carousel.offsetHeight;
            const productsHeight = productsGrid.offsetHeight;
            
            // Use transition only when switching positions to make it smooth
            if (carousel.style.position === 'sticky') {
            carousel.style.transition = 'none';
            carousel.style.position = 'relative';
            carousel.style.top = `${productsHeight - carouselHeight}px`;
            // Force reflow before adding transition back
            carousel.offsetHeight;
            }
        }
        }
    }
    
    // Initialize
    updateCarousel(currentIndex);
    startCarouselRotation();
    handleScroll(); // Initialize scroll position
    
    // Add scroll event listener with passive option for better performance
    window.addEventListener('scroll', handleScroll, { passive: true });
    window.addEventListener('resize', handleScroll, { passive: true });

    //----------------------------------------End of latest products
});


/* Function to change the video source based on screen size
function changeVideoSource() {
    var video = document.getElementById('background-video');
    var videoSource = document.getElementById('video-source');
    
    // Check window width and change the source accordingly
    if (window.innerWidth < 768) {
        videoSource.src = "https://videos.pexels.com/video-files/5822768/5822768-hd_1080_1920_25fps.mp4"; // Vertical video
    } else {
        videoSource.src = "https://videos.pexels.com/video-files/5822850/5822850-hd_1920_1080_25fps.mp4"; // Horizontal video
    }

    // Reload the video with the new source
    video.load();
    video.play();
}

// Run the function on page load
window.onload = changeVideoSource;

// Run the function on window resize (to adjust if the user resizes the window)
window.onresize = changeVideoSource; */

//======================================The code below is the new version of the one above
// Function to change the video source based on screen size
async function changeVideoSource() {
    var video = document.getElementById('background-video');
    var videoSource = document.getElementById('video-source');
    
    if (!video || !videoSource) {
        console.warn('Video element or source not found');
        return;
    }
    
    // Pause the video first to prevent conflicts
    video.pause();
    
    // Check window width and change the source accordingly
    var newSrc;
    if (window.innerWidth < 768) {
        newSrc = "https://videos.pexels.com/video-files/5822768/5822768-hd_1080_1920_25fps.mp4"; // Vertical video
    } else {
        newSrc = "https://videos.pexels.com/video-files/5822850/5822850-hd_1920_1080_25fps.mp4"; // Horizontal video
    }
    
    // Only change source if it's different from current source
    if (videoSource.src !== newSrc) {
        videoSource.src = newSrc;
        
        // Reload the video with the new source
        video.load();
        
        // Wait for the video to be ready before playing
        try {
            await new Promise((resolve, reject) => {
                const onCanPlay = () => {
                    video.removeEventListener('canplay', onCanPlay);
                    video.removeEventListener('error', onError);
                    resolve();
                };
                
                const onError = (error) => {
                    video.removeEventListener('canplay', onCanPlay);
                    video.removeEventListener('error', onError);
                    reject(error);
                };
                
                video.addEventListener('canplay', onCanPlay);
                video.addEventListener('error', onError);
                
                // If video is already ready, resolve immediately
                if (video.readyState >= 3) {
                    onCanPlay();
                }
            });
            
            // Now safely play the video
            await video.play();
        } catch (error) {
            console.error('Error playing video:', error);
            // Optionally, you can try to play again after a short delay
            setTimeout(async () => {
                try {
                    await video.play();
                } catch (retryError) {
                    console.error('Retry failed:', retryError);
                }
            }, 100);
        }
    }
}

// Debounce function to prevent excessive calls during window resize
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Create debounced version of the function
const debouncedChangeVideoSource = debounce(changeVideoSource, 250);

// Run the function on page load
window.addEventListener('load', changeVideoSource);

// Run the debounced function on window resize
window.addEventListener('resize', debouncedChangeVideoSource);
