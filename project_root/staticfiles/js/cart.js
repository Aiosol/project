// static/js/cart.js
document.addEventListener('DOMContentLoaded', function() {
    // Add hidden CSRF token form if not already present
    if (!document.querySelector('#csrf_form')) {
        const csrfForm = document.createElement('form');
        csrfForm.id = 'csrf_form';
        csrfForm.style.display = 'none';
        csrfForm.innerHTML = '<input type="hidden" name="csrfmiddlewaretoken" value="' + 
                             document.querySelector('[name=csrfmiddlewaretoken]').value + '">';
        document.body.appendChild(csrfForm);
    }
    
    // Handle all Add to Cart buttons, both on product cards and detail pages
    const addToCartButtons = document.querySelectorAll('.btn-add-to-cart, [id^="add-to-cart"]');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Add to cart button clicked');
            
            // Get product ID or variant ID
            const variantId = this.getAttribute('data-variant-id') || this.getAttribute('data-product-id');
            if (!variantId) {
                console.error('No product or variant ID found');
                return;
            }
            
            // Get quantity (default to 1 if no quantity selector)
            const quantityInput = document.getElementById('quantity');
            const quantity = quantityInput ? parseInt(quantityInput.value) : 1;
            
            console.log('Adding to cart:', {
                productId: variantId,
                quantity: quantity
            });
            
            // Get CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            // Create form data
            const formData = new FormData();
            formData.append('quantity', quantity);
            
            // Send AJAX request
            fetch(`/cart/add/${variantId}/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                },
                body: formData
            })
            .then(response => {
                console.log('Response status:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('Response data:', data);
                if (data.success) {
                    alert(data.message);
                    
                    // Update cart count in header
                    const cartCount = document.querySelector('.cart-count');
                    if (cartCount) {
                        cartCount.textContent = data.cart_total;
                        cartCount.style.display = data.cart_total > 0 ? 'inline-block' : 'none';
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('There was an error adding the item to your cart. Please try again.');
            });
        });
    });
    
    // Wishlist functionality
    const wishlistButtons = document.querySelectorAll('.wishlist-btn, #add-to-wishlist');
    wishlistButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            alert('Wishlist functionality coming soon!');
        });
    });
});