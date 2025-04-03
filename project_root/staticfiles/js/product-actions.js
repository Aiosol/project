document.addEventListener('DOMContentLoaded', function() {
    // Wishlist button functionality
    const wishlistButtons = document.querySelectorAll('.wishlist-btn');
    wishlistButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');
            
            // Toggle active class for visual feedback
            this.classList.toggle('active');
            
            // Toggle heart icon
            const icon = this.querySelector('i');
            if (icon.classList.contains('bi-heart')) {
                icon.classList.remove('bi-heart');
                icon.classList.add('bi-heart-fill');
            } else {
                icon.classList.remove('bi-heart-fill');
                icon.classList.add('bi-heart');
            }
            
            // AJAX call to add/remove from wishlist
            // This will be implemented later when we create the wishlist functionality
            console.log('Toggled wishlist for product ID:', productId);
        });
    });
    
    // Add to cart functionality
    const addToCartButtons = document.querySelectorAll('.btn-add-to-cart');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');
            
            // Visual feedback
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="bi bi-check-circle me-1"></i>Added';
            this.disabled = true;
            
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            }, 2000);
            
            // AJAX call to add to cart
            // This will be implemented later when we create the cart functionality
            console.log('Added to cart product ID:', productId);
        });
    });
});