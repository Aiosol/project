document.addEventListener('DOMContentLoaded', function() {
    // Select all orders functionality
    const selectAllCheckbox = document.getElementById('select-all-orders');
    const orderCheckboxes = document.querySelectorAll('.order-select');
    const bulkActionsToolbar = document.getElementById('bulk-actions-toolbar');
    
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const isChecked = this.checked;
            orderCheckboxes.forEach(checkbox => {
                checkbox.checked = isChecked;
            });
            updateBulkActionsToolbar();
        });
    }
    
    // Individual checkbox change
    orderCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateBulkActionsToolbar);
    });
    
    // Show/hide bulk actions toolbar
    function updateBulkActionsToolbar() {
        const checkedCount = document.querySelectorAll('.order-select:checked').length;
        bulkActionsToolbar.style.display = checkedCount > 0 ? 'block' : 'none';
    }
    
    // Bulk actions handling
    document.querySelectorAll('.bulk-action').forEach(button => {
        button.addEventListener('click', function() {
            const action = this.dataset.action;
            const selectedIds = getSelectedOrderIds();
            
            if (selectedIds.length === 0) return;
            
            switch(action) {
                case 'status':
                    showStatusUpdateModal(selectedIds);
                    break;
                case 'export':
                    exportOrders(selectedIds);
                    break;
                case 'delete':
                    if (confirm(`Are you sure you want to delete ${selectedIds.length} orders?`)) {
                        deleteOrders(selectedIds);
                    }
                    break;
            }
        });
    });
    
    // Helper functions
    function getSelectedOrderIds() {
        return Array.from(document.querySelectorAll('.order-select:checked'))
            .map(checkbox => checkbox.value);
    }
    
    function showStatusUpdateModal(orderIds) {
        // Implementation for status update modal
        // This will be added in the next steps
    }
    
    function exportOrders(orderIds) {
        window.location.href = `/crm/orders/export/?ids=${orderIds.join(',')}`;
    }
    
    function deleteOrders(orderIds) {
        // Implement with fetch API
        fetch('/crm/orders/bulk-delete/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ order_ids: orderIds })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Refresh page or remove rows
                window.location.reload();
            } else {
                alert('Error: ' + data.message);
            }
        });
    }
});