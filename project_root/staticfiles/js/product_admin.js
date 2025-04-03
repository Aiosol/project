(function($) {
    $(document).ready(function() {
        // Function to toggle simple product fields
        function toggleSimpleProductFields() {
            var productType = $('#id_product_type').val();
            var simpleFields = $('.field-stock_quantity, .field-sku').parent().parent();
            
            if (productType === 'simple') {
                simpleFields.show();
                // Hide variants inline
                $('.inline-related.tabular h2:contains("Product variants")').parent().hide();
            } else {
                simpleFields.hide();
                // Show variants inline
                $('.inline-related.tabular h2:contains("Product variants")').parent().show();
            }
        }
        
        // Run on page load
        toggleSimpleProductFields();
        
        // Run when product type changes
        $('#id_product_type').change(function() {
            toggleSimpleProductFields();
        });
    });
})(django.jQuery);