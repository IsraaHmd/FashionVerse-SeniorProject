document.addEventListener('DOMContentLoaded', function() {
    // Handle place order button click
    document.getElementById('placeOrderBtn').addEventListener('click', function() {
        // Basic form validation
        const form = document.getElementById('checkoutForm');
        const firstName = document.getElementById('firstName').value.trim();
        const lastName = document.getElementById('lastName').value.trim();
        const phoneCountry = document.getElementById('phoneCountry').value.trim();
        const phoneNumber = document.getElementById('phoneNumber').value.trim();
        const location = document.getElementById('location').value.trim();
        
        let isValid = true;
        
        // Clear previous error messages
        document.querySelectorAll('.error-text').forEach(el => el.remove());
        document.querySelectorAll('.invalid-field').forEach(el => el.classList.remove('invalid-field'));
        
        // Validate first name
        if (!firstName) {
            isValid = false;
            document.getElementById('firstName').classList.add('invalid-field');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-text';
            errorDiv.textContent = 'Please enter your first name';
            document.getElementById('firstName').parentNode.appendChild(errorDiv);
        }
        
        // Validate last name
        if (!lastName) {
            isValid = false;
            document.getElementById('lastName').classList.add('invalid-field');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-text';
            errorDiv.textContent = 'Please enter your last name';
            document.getElementById('lastName').parentNode.appendChild(errorDiv);
        }
        
        // Validate phone country code
        if (!phoneCountry) {
            isValid = false;
            document.getElementById('phoneCountry').classList.add('invalid-field');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-text';
            errorDiv.textContent = 'Please enter a country code';
            document.getElementById('phoneCountry').parentNode.parentNode.appendChild(errorDiv);
        }
        
        // Validate phone number
        if (!phoneNumber) {
            isValid = false;
            document.getElementById('phoneNumber').classList.add('invalid-field');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-text';
            errorDiv.textContent = 'Please enter your phone number';
            document.getElementById('phoneNumber').parentNode.appendChild(errorDiv);
        } else if (!/^\d+$/.test(phoneNumber)) {
            isValid = false;
            document.getElementById('phoneNumber').classList.add('invalid-field');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-text';
            errorDiv.textContent = 'Phone number must contain only digits';
            document.getElementById('phoneNumber').parentNode.appendChild(errorDiv);
        }
        
        // Validate location
        if (!location) {
            isValid = false;
            document.getElementById('location').classList.add('invalid-field');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-text';
            errorDiv.textContent = 'Please enter your address';
            document.getElementById('location').parentNode.appendChild(errorDiv);
        }
        
        if (isValid) {
            // Show confirmation modal
            var confirmationModal = new bootstrap.Modal(document.getElementById('confirmationModal'));
            confirmationModal.show();
        }
    });
    
    // Handle confirm order button click
    document.getElementById('confirmOrder').addEventListener('click', function() {
        // Submit the form
        document.getElementById('checkoutForm').submit();
    });
    
    // Country code dropdown handling
    const phoneCountryInput = document.getElementById('phoneCountry');
    const countryCodeList = document.getElementById('countryCodeList');
    const dropdownItems = document.querySelectorAll('#countryCodeList .dropdown-item');
    
    // Show dropdown on input focus
    phoneCountryInput.addEventListener('focus', function() {
        countryCodeList.classList.add('show');
    });
    
    // Filter dropdown items as user types
    phoneCountryInput.addEventListener('input', function() {
        const filterValue = this.value.toLowerCase();
        
        dropdownItems.forEach(item => {
            const code = item.getAttribute('data-code').toLowerCase();
            if (code.startsWith(filterValue)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
        
        // Show dropdown if it's not already shown
        countryCodeList.classList.add('show');
    });
    
    // Select country code when clicked
    dropdownItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            phoneCountryInput.value = this.getAttribute('data-code');
            countryCodeList.classList.remove('show');
        });
    });
    
    // Hide dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!phoneCountryInput.contains(e.target) && !countryCodeList.contains(e.target)) {
            countryCodeList.classList.remove('show');
        }
    });
});
