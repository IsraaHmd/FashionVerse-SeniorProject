
document.addEventListener("DOMContentLoaded", function () {
       
    const colorButtons = document.querySelectorAll('.color-button');

    colorButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Get the product URL from the data attribute
            const productUrl = this.getAttribute('data-product-url');
            window.location.href = productUrl;  // Navigate to the selected color's product page
        });
    });
    // For the colored buttons to have the hex color: 
    document.querySelectorAll('.color-button').forEach(button => {
        const color = button.getAttribute('data-color');
        button.style.setProperty('--color', color);
    });

    //sizes:
    // Get all size buttons that are not disabled
    const sizeButtons = document.querySelectorAll('.size-options-button:not(.disabled)');
    
    // Add click event to each button
    sizeButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove 'selected' class from all buttons
            sizeButtons.forEach(btn => btn.classList.remove('selected'));
            
            // Add 'selected' class to clicked button
            this.classList.add('selected');
            
            //which variant was choosen => update the form
            const variantId = this.dataset.variantId;
            document.getElementById('selected_variant_id').value = variantId;
            
        });
    });
});

/*  //In the below comment there is the ajax code to make the change from one color to another seemless but it was cancelled and replaced by the below it to change url
    //Get all color buttons and add event listeners to them
    const colorButtons = document.querySelectorAll('.color-button');
    colorButtons.forEach(button => {
        button.addEventListener('click', function() {
            //if another color was selected: 
    
            // Get the product color id from the data attribute
            const productColorId = this.getAttribute('data-product-id');
           
            // Make an AJAX request to update the product image and variants dynamically
            fetch(`/product/${productColorId}/variants/`)
            .then(response => response.json())
            .then(data => {
                if(data.total_color_stock > 0) {
                    // If this color is avaliable in stock then make it the selected one: 
                    
                    // Remove the 'selected' class from all buttons
                    colorButtons.forEach(b => b.classList.remove('selected'));
                    
                    // Add 'selected' class to the clicked button
                    this.classList.add('selected');
        
                    const productImage = document.querySelector('.selected-product-image');
        
                    if (productImage && data.product_image) {
                        // Update product image
                        productImage.src = data.product_image;
                    } 
                    // Update the available sizes and quantities
                    let variantsHtml = '';
                    data.variants.forEach(variant => {
                        variantsHtml += `<button class="size-options-button">${variant.size__name}</button>`;
                    });
                    document.querySelector('.size-options').innerHTML = variantsHtml;
                }
            });
        });
        }); */

