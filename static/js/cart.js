/* mealKart - Cart Operations and Wishlist */

document.addEventListener('DOMContentLoaded', function() {
    
    // --- Helper to show Toast Notification dynamically ---
    function showToast(message, type = 'success') {
        let container = document.getElementById('django-messages-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'django-messages-container';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        
        const toast = document.createElement('div');
        toast.className = `toast-alert ${type}`;
        
        const iconClass = type === 'success' ? 'fa-circle-check' : (type === 'error' ? 'fa-circle-exclamation' : 'fa-circle-info');
        toast.innerHTML = `
            <i class="fa-solid ${iconClass} toast-icon"></i>
            <span class="toast-message">${message}</span>
            <button class="toast-close-btn">&times;</button>
        `;
        
        // Close button functionality
        toast.querySelector('.toast-close-btn').addEventListener('click', function() {
            toast.remove();
        });
        
        container.appendChild(toast);
        
        // Auto remove
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(-20px)';
            toast.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            setTimeout(() => toast.remove(), 400);
        }, 4000);
    }

    // --- 1. Add to Cart AJAX (Event Delegation) ---
    document.body.addEventListener('click', function(e) {
        const button = e.target.closest('.btn-add-to-cart');
        if (!button) return;
        
        e.preventDefault();
        const foodId = button.getAttribute('data-food-id');
        
        fetch('/cart/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrfToken
            },
            body: JSON.stringify({ food_id: foodId, quantity: 1 })
        })
        .then(response => {
            if (response.status === 403) {
                window.location.href = '/auth/login/';
                return;
            }
            return response.json();
        })
        .then(data => {
            if (data && data.success) {
                showToast(data.message, 'success');
                
                // Update global cart badge count
                const badge = document.getElementById('global-cart-qty');
                if (badge) {
                    badge.textContent = data.cart_count;
                    badge.classList.add('badge-pulse');
                    setTimeout(() => badge.classList.remove('badge-pulse'), 2000);
                }
            } else if (data && data.error) {
                showToast(data.error, 'error');
            }
        })
        .catch(err => {
            console.error('Error adding to cart:', err);
            showToast('Failed to add item. Please try again.', 'error');
        });
    });

    // --- 1.5 Add Combo to Cart (Event Delegation) ---
    document.body.addEventListener('click', function(e) {
        const button = e.target.closest('.btn-combo-add');
        if (!button) return;
        
        e.preventDefault();
        const itemsJson = button.getAttribute('data-items-json');
        if (!itemsJson) return;
        
        let foodIds = [];
        try {
            foodIds = JSON.parse(itemsJson);
        } catch(e) {
            console.error("Invalid JSON in combo button:", e);
            return;
        }
        
        button.disabled = true;
        button.innerHTML = 'Adding... <i class="fa-solid fa-spinner fa-spin"></i>';
        
        const requests = foodIds.map(foodId => {
            return fetch('/cart/add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.csrfToken
                },
                body: JSON.stringify({ food_id: foodId, quantity: 1 })
            }).then(res => {
                if (res.status === 403) {
                    window.location.href = '/auth/login/';
                    throw new Error("Unauthorized");
                }
                return res.json();
            });
        });
        
        Promise.all(requests)
            .then(results => {
                const validResults = results.filter(r => r && r.success);
                if (validResults.length > 0) {
                    showToast('Combo added to cart successfully!', 'success');
                    // Get latest cart count from the last valid response
                    const lastSuccess = validResults[validResults.length - 1];
                    const badge = document.getElementById('global-cart-qty');
                    if (badge) {
                        badge.textContent = lastSuccess.cart_count;
                        badge.classList.add('badge-pulse');
                        setTimeout(() => badge.classList.remove('badge-pulse'), 2000);
                    }
                } else {
                    showToast('Failed to add combo.', 'error');
                }
            })
            .catch(err => {
                if (err.message !== "Unauthorized") {
                    console.error('Combo add error:', err);
                    showToast('Error adding combo. Please try again.', 'error');
                }
            })
            .finally(() => {
                button.disabled = false;
                button.innerHTML = 'Add Combo <i class="fa-solid fa-plus"></i>';
            });
    });

    // --- 2. Wishlist Favorite Toggle (Event Delegation) ---
    document.body.addEventListener('click', function(e) {
        const btn = e.target.closest('.favorite-heart-btn');
        if (!btn) return;
        
        e.preventDefault();
        const foodId = btn.getAttribute('data-food-id');
        
        fetch('/api/favorite/toggle/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrfToken
            },
            body: JSON.stringify({ food_id: foodId })
        })
        .then(response => {
            if (response.status === 403) {
                window.location.href = '/auth/login/';
                return;
            }
            return response.json();
        })
        .then(data => {
            if (data && data.success) {
                const icon = btn.querySelector('i');
                if (data.is_favorite) {
                    btn.classList.add('liked');
                    icon.className = 'fa-solid fa-heart';
                    showToast('Added to Favourites', 'info');
                } else {
                    btn.classList.remove('liked');
                    icon.className = 'fa-regular fa-heart';
                    showToast('Removed from Favourites', 'info');
                }
            }
        })
        .catch(err => console.error('Error toggling favorite:', err));
    });

    // --- 3. Cart Page Operations (Increase / Decrease / Remove) ---
    function updateCartDetailsUI(data, itemId, action) {
        const qtyDisplay = document.getElementById(`qty-val-${itemId}`);
        const itemRow = document.getElementById(`cart-item-${itemId}`);
        
        if (action === 'remove' || data.quantity === 0) {
            if (itemRow) {
                itemRow.style.opacity = '0';
                itemRow.style.transform = 'scale(0.9)';
                itemRow.style.transition = 'all 0.3s ease';
                setTimeout(() => {
                    itemRow.remove();
                    // If no items left in list, reload to display empty cart view
                    const remainingItems = document.querySelectorAll('.cart-item-card');
                    if (remainingItems.length === 0) {
                        window.location.reload();
                    }
                }, 300);
            }
        } else if (qtyDisplay) {
            qtyDisplay.textContent = data.quantity;
        }

        // Update billing figures
        document.getElementById('bill-subtotal').textContent = `₹${data.subtotal.toFixed(2)}`;
        document.getElementById('bill-delivery').textContent = `₹${data.delivery_charge.toFixed(2)}`;
        document.getElementById('bill-gst').textContent = `₹${data.gst.toFixed(2)}`;
        
        const discountRow = document.getElementById('bill-discount-row');
        const discountVal = document.getElementById('bill-discount');
        if (data.discount > 0) {
            if (discountRow) discountRow.classList.remove('hidden');
            if (discountVal) discountVal.textContent = `-₹${data.discount.toFixed(2)}`;
        } else {
            if (discountRow) discountRow.classList.add('hidden');
        }

        document.getElementById('bill-grandtotal').textContent = `₹${data.grand_total.toFixed(2)}`;

        // Update nav badge count
        const badge = document.getElementById('global-cart-qty');
        if (badge) {
            badge.textContent = data.cart_count;
        }
    }

    const incBtns = document.querySelectorAll('.inc-qty-btn');
    const decBtns = document.querySelectorAll('.dec-qty-btn');
    const removeBtns = document.querySelectorAll('.remove-item-btn');

    incBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const itemId = btn.getAttribute('data-item-id');
            fetch('/cart/update/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.csrfToken
                },
                body: JSON.stringify({ item_id: itemId, action: 'increase' })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    updateCartDetailsUI(data, itemId, 'increase');
                }
            });
        });
    });

    decBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const itemId = btn.getAttribute('data-item-id');
            fetch('/cart/update/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.csrfToken
                },
                body: JSON.stringify({ item_id: itemId, action: 'decrease' })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    updateCartDetailsUI(data, itemId, 'decrease');
                }
            });
        });
    });

    removeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const itemId = btn.getAttribute('data-item-id');
            if (confirm('Are you sure you want to remove this item?')) {
                fetch('/cart/update/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': window.csrfToken
                    },
                    body: JSON.stringify({ item_id: itemId, action: 'remove' })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        updateCartDetailsUI(data, itemId, 'remove');
                        showToast('Item removed from cart', 'info');
                    }
                });
            }
        });
    });

    // --- 4. Promo Coupon Apply/Remove ---
    const applyCouponBtn = document.getElementById('btn-apply-coupon-code');
    const removeCouponBtn = document.getElementById('btn-remove-coupon-code');
    const couponInput = document.getElementById('coupon-input-code');
    const couponError = document.getElementById('coupon-error-msg');

    if (applyCouponBtn && couponInput) {
        applyCouponBtn.addEventListener('click', function() {
            const code = couponInput.value.trim();
            if (!code) {
                if (couponError) {
                    couponError.textContent = 'Please enter a coupon code.';
                    couponError.classList.remove('hidden');
                }
                return;
            }

            fetch('/cart/apply-coupon/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.csrfToken
                },
                body: JSON.stringify({ coupon_code: code })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.location.reload(); // Reload page to update full coupon wrapper & math templates
                } else {
                    if (couponError) {
                        couponError.textContent = data.message;
                        couponError.classList.remove('hidden');
                    }
                }
            });
        });
    }

    if (removeCouponBtn) {
        removeCouponBtn.addEventListener('click', function() {
            fetch('/cart/remove-coupon/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.csrfToken
                },
                body: JSON.stringify({})
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.location.reload();
                }
            });
        });
    }
});
