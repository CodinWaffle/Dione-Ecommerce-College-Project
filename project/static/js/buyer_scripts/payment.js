document.addEventListener('DOMContentLoaded', function() {
    // Payment method expansion/collapse
    const paymentMethods = document.querySelectorAll('.payment-method');
    
    paymentMethods.forEach(method => {
        const header = method.querySelector('.method-header');
        const expandBtn = method.querySelector('.expand-btn');
        
        header.addEventListener('click', function() {
            // Close all other payment methods
            paymentMethods.forEach(otherMethod => {
                if (otherMethod !== method) {
                    otherMethod.classList.remove('active');
                    const otherExpandBtn = otherMethod.querySelector('.expand-btn');
                    otherExpandBtn.textContent = '+';
                }
            });
            
            // Toggle current method
            method.classList.toggle('active');
            expandBtn.textContent = method.classList.contains('active') ? '−' : '+';
        });
    });

    // Credit card number formatting
    const cardNumberInput = document.getElementById('card-number');
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\s/g, '').replace(/[^0-9]/gi, '');
            let formattedValue = value.match(/.{1,4}/g)?.join(' ') || value;
            if (formattedValue.length > 19) {
                formattedValue = formattedValue.substring(0, 19);
            }
            e.target.value = formattedValue;
        });
    }

    // Expiry date formatting
    const expiryInput = document.getElementById('expiry');
    if (expiryInput) {
        expiryInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length >= 2) {
                value = value.substring(0, 2) + ' / ' + value.substring(2, 4);
            }
            e.target.value = value;
        });
    }

    // Security code validation
    const securityCodeInput = document.getElementById('security-code');
    if (securityCodeInput) {
        securityCodeInput.addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/[^0-9]/g, '');
        });
    }

    // GCash mobile number formatting
    const gcashNumberInput = document.getElementById('gcash-number');
    if (gcashNumberInput) {
        gcashNumberInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/[^0-9]/g, '');
            
            // Format as 09XX XXX XXXX
            if (value.length > 0) {
                if (value.length <= 4) {
                    value = value;
                } else if (value.length <= 7) {
                    value = value.substring(0, 4) + ' ' + value.substring(4);
                } else {
                    value = value.substring(0, 4) + ' ' + value.substring(4, 7) + ' ' + value.substring(7, 11);
                }
            }
            
            e.target.value = value;
        });

        // Validate Philippine mobile number format
        gcashNumberInput.addEventListener('blur', function(e) {
            const value = e.target.value.replace(/\s/g, '');
            if (value && !value.match(/^09\d{9}$/)) {
                e.target.style.borderColor = '#dc3545';
                // You could show an error message here
            } else {
                e.target.style.borderColor = '#ddd';
            }
        });
    }

    // Same as shipping address checkbox
    const sameAddressCheckbox = document.getElementById('same-address');
    const billingAddress = document.querySelector('.billing-address');
    
    if (sameAddressCheckbox && billingAddress) {
        sameAddressCheckbox.addEventListener('change', function() {
            if (this.checked) {
                billingAddress.style.display = 'block';
            } else {
                billingAddress.style.display = 'none';
            }
        });
    }

    // Form validation
    const reviewOrderBtn = document.querySelector('.review-order-btn');
    const creditCardForm = document.querySelector('.credit-card-form');
    
    if (reviewOrderBtn && creditCardForm) {
        reviewOrderBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get active payment method
            const activeMethod = document.querySelector('.payment-method.active');
            
            if (activeMethod && activeMethod.dataset.method === 'credit-card') {
                // Validate credit card form
                const cardNumber = document.getElementById('card-number').value;
                const expiry = document.getElementById('expiry').value;
                const securityCode = document.getElementById('security-code').value;
                const cardName = document.getElementById('card-name').value;
                
                let isValid = true;
                let errorMessage = '';
                
                if (!cardNumber || cardNumber.replace(/\s/g, '').length < 13) {
                    isValid = false;
                    errorMessage = 'Please enter a valid card number';
                }
                
                if (!expiry || expiry.length < 7) {
                    isValid = false;
                    errorMessage = 'Please enter a valid expiry date';
                }
                
                if (!securityCode || securityCode.length < 3) {
                    isValid = false;
                    errorMessage = 'Please enter a valid security code';
                }
                
                if (!cardName.trim()) {
                    isValid = false;
                    errorMessage = 'Please enter the name on card';
                }
                
                if (!isValid) {
                    alert(errorMessage);
                    return;
                }
            } else if (activeMethod && activeMethod.dataset.method === 'gcash') {
                // Validate GCash form
                const gcashNumber = document.getElementById('gcash-number').value;
                
                if (!gcashNumber || !gcashNumber.replace(/\s/g, '').match(/^09\d{9}$/)) {
                    alert('Please enter a valid GCash mobile number (09XX XXX XXXX)');
                    return;
                }
            }
            
            // Show loading state
            reviewOrderBtn.textContent = 'PROCESSING...';
            reviewOrderBtn.disabled = true;
            
            // Simulate payment processing
            setTimeout(() => {
                // Show success message
                showNotification('Payment processed successfully! Redirecting...', 'success');
                
                // Redirect to order confirmation / success page
                setTimeout(() => {
                    window.location.href = '/order-success';
                }, 1500);
            }, 2000);
        });
    }

    // Edit buttons functionality
    const editButtons = document.querySelectorAll('.edit-btn');
    editButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            alert('Edit functionality would open a modal or redirect to edit page');
        });
    });

    // Add discount/gift card functionality
    const addBtn = document.querySelector('.add-btn');
    if (addBtn) {
        addBtn.addEventListener('click', function() {
            const giftCardCode = prompt('Enter your gift card or discount code:');
            if (giftCardCode) {
                alert('Gift card/discount code applied: ' + giftCardCode);
                // Here you would typically validate and apply the code
            }
        });
    }

    // Card type detection
    function detectCardType(number) {
        const cardTypes = {
            visa: /^4/,
            mastercard: /^5[1-5]/,
            amex: /^3[47]/,
            discover: /^6(?:011|5)/
        };
        
        for (let type in cardTypes) {
            if (cardTypes[type].test(number)) {
                return type;
            }
        }
        return null;
    }

    // Update card type display
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function() {
            const cardType = detectCardType(this.value.replace(/\s/g, ''));
            const cardIcons = document.querySelectorAll('.card-types img');
            
            cardIcons.forEach(icon => {
                icon.style.opacity = '0.3';
            });
            
            if (cardType) {
                const activeIcon = document.querySelector(`.card-types img[alt*="${cardType}"]`);
                if (activeIcon) {
                    activeIcon.style.opacity = '1';
                }
            }
        });
    }
    
    // Add notification function
    function showNotification(message, type = 'info') {
        // Remove existing notifications
        const existingNotification = document.querySelector('.notification');
        if (existingNotification) {
            existingNotification.remove();
        }
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 4px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
            max-width: 300px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        `;
        
        // Set background color based on type
        if (type === 'success') {
            notification.style.backgroundColor = '#28a745';
        } else if (type === 'error') {
            notification.style.backgroundColor = '#dc3545';
        } else {
            notification.style.backgroundColor = '#007bff';
        }
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
});