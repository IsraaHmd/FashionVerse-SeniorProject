document.addEventListener('DOMContentLoaded', function() {
    /*In the code below:
    JS sees open_cart=true, opens the cart using Bootstrap
    JS removes open_cart=true from URL using replaceState
    => so that when an item is removed, the cart is opened again updated*/

    // Check URL parameters for open_cart
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('open_cart') === 'true') {
        // Open the cart offcanvas
        var offcanvasCart = new bootstrap.Offcanvas(document.getElementById('offcanvasCart'));
        offcanvasCart.show();
        
        // Clean up the URL to remove the parameter 
        if (window.history && window.history.replaceState) {
            const cleanUrl = window.location.pathname + 
                             window.location.search.replace(/[?&]open_cart=true/, '').replace(/^\?$/, '');
            window.history.replaceState({}, document.title, cleanUrl);
        }
    }
    //-------------------------Quanitity
    const quantityControls = document.querySelectorAll('.input-group');
  
    quantityControls.forEach(group => {
      const decrementBtn = group.querySelector('button:first-child');
      const incrementBtn = group.querySelector('button:last-child');
      const quantityInput = group.querySelector('.quanity-value');
      const itemId = quantityInput.getAttribute('data-item-id');
      
      // Handle decrement button click
      decrementBtn.addEventListener('click', function() {
        const currentValue = parseInt(quantityInput.value);
        if (currentValue > 1) {
          // Don't update input value here - wait for server response
          updateCartItemQuantity(itemId, currentValue - 1);
        }
      });
      
      // Handle increment button click
      incrementBtn.addEventListener('click', function() {
        const currentValue = parseInt(quantityInput.value);
        updateCartItemQuantity(itemId, currentValue + 1);
      });
      

      // Handle manual input change
      quantityInput.addEventListener('change', function() {
        let newValue = parseInt(this.value);
        
        // Ensure the value is a valid number
        if (isNaN(newValue) || newValue < 1) {
          newValue = 1;
          this.value = 1;
        }
        
        // Update server with new quantity
        updateCartItemQuantity(itemId, newValue);
      });
    });
    
    
    function updateCartItemQuantity(itemId, newQuantity) {
      // Get CSRF token from cookie
      const csrftoken = getCookie('csrftoken');

      // Let's try a simple form POST approach
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = `/update_cart_quantity/${itemId}/`;
      
      // Add CSRF token
      const csrfInput = document.createElement('input');
      csrfInput.type = 'hidden';
      csrfInput.name = 'csrfmiddlewaretoken';
      csrfInput.value = csrftoken;
      form.appendChild(csrfInput);
      
      // Add quantity
      const quantityInput = document.createElement('input');
      quantityInput.type = 'hidden';
      quantityInput.name = 'quantity';
      quantityInput.value = newQuantity;
      form.appendChild(quantityInput);
      
      // Submit the form via AJAX
      const formData = new FormData(form);
      
      fetch(form.action, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': csrftoken
        },
        body: formData
      })
      .then(response => {
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        return response.text().then(text => {
          console.log('Raw response:', text);
          try {
            return JSON.parse(text);
          } catch (e) {
            console.error('Failed to parse response as JSON:', e);
            throw new Error('Invalid response format');
          }
        });
      })
      .then(data => {
        console.log('Parsed data:', data);
        
        // Update UI with new data
        if (data.success) {
          // IMPORTANT FIX: Always update the input field with the server's value
          const inputField = document.querySelector(`.quanity-value[data-item-id="${itemId}"]`);
          if (inputField) {
            // Use adjusted_quantity if provided, otherwise use the requested quantity
            inputField.value = data.adjusted_quantity || newQuantity;
          }
          
          // Update cart total
          const totalElement = document.querySelector('.list-group-item.d-flex.justify-content-between strong');
          if (totalElement && data.new_total) {
            totalElement.textContent = '$' + data.new_total;
          }
          
          // Update cart badge
          const cartBadge = document.querySelector('.badge.badge-black');
          if (cartBadge && data.cart_total_quantity) {
            cartBadge.textContent = data.cart_total_quantity;
          }
          
          // Display message if any
          if (data.message) {
            // Check if alert already exists
            let alertElement = document.querySelector('.cart-message');
            if (!alertElement) {
              // Create new alert
              alertElement = document.createElement('div');
              alertElement.className = 'alert cart-message text-danger d-flex justify-content-between align-items-center';
              
              const messageSpan = document.createElement('span');
              alertElement.appendChild(messageSpan);
              
              const closeButton = document.createElement('button');
              closeButton.className = 'btn-close btn-sm';
              closeButton.setAttribute('data-bs-dismiss', 'alert');
              closeButton.setAttribute('aria-label', 'Close');
              alertElement.appendChild(closeButton);
              
              // Find position to insert alert (before the total)
              const CartItems = document.querySelector('.list-group-item.d-flex.justify-content-between');
              if (CartItems) {
                CartItems.parentNode.insertBefore(alertElement, CartItems);
              }
            }
            
            // Update message text
            const messageSpan = alertElement.querySelector('span');
            if (messageSpan) {
              messageSpan.textContent = data.message;
            }
          }
        } else {
          console.error('Server returned error:', data.message);
          alert('Server error: ' + (data.message || 'Unknown error'));
        }
      })
      .catch(error => {
        console.error('Error updating cart:', error);
        alert('Error updating cart: ' + error.message);
      });
    }
    // Helper function to get CSRF token from cookies
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
});
