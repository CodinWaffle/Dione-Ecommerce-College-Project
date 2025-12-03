// My Purchases Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('My Purchases page loaded');
    
    // Initialize functionality
    initializeReviewFilters();
    initializeTooltips();
    initializeModals();
});

// Initialize review filters
function initializeReviewFilters() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const filter = this.dataset.rating;
            const reviewsList = this.closest('.reviews-dropdown').querySelector('.reviews-list');
            
            // Update active filter
            filterBtns.forEach(filterBtn => filterBtn.classList.remove('active'));
            this.classList.add('active');
            
            // Apply filter
            filterReviews(reviewsList, filter);
        });
    });
}

// Filter reviews by rating
function filterReviews(reviewsList, filter) {
    if (!reviewsList) return;
    
    const reviewItems = reviewsList.querySelectorAll('.review-item');
    let visibleCount = 0;
    
    reviewItems.forEach(item => {
        const rating = item.dataset.rating;
        let shouldShow = filter === 'all' || rating === filter;
        
        if (shouldShow) {
            item.style.display = 'block';
            visibleCount++;
        } else {
            item.style.display = 'none';
        }
    });
}

// Initialize tooltips
function initializeTooltips() {
    // Add tooltip functionality if needed
    console.log('Tooltips initialized');
}

// Initialize modals
function initializeModals() {
    const modals = document.querySelectorAll('.modal');
    
    modals.forEach(modal => {
        // Close on backdrop click
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal(modal);
            }
        });
        
        // Close on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal.classList.contains('active')) {
                closeModal(modal);
            }
        });
    });
}

// Close modal
function closeModal(modal) {
    modal.classList.remove('active');
}

// Toggle reviews dropdown
function toggleReviews(orderId) {
    const dropdown = document.getElementById(`reviews-${orderId}`);
    const toggle = document.querySelector(`[onclick="toggleReviews(${orderId})"]`);
    
    if (dropdown && toggle) {
        dropdown.classList.toggle('active');
        toggle.classList.toggle('active');
    }
}

// View order details
function viewOrderDetails(orderId) {
    window.location.href = `/buyer/order/${orderId}`;
}

// Track order
function trackOrder(orderId) {
    window.location.href = `/buyer/order/${orderId}/track`;
}

// Cancel order
async function cancelOrder(orderId) {
    if (!confirm('Are you sure you want to cancel this order?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/orders/${orderId}/cancel`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        });
        
        if (response.ok) {
            const result = await response.json();
            if (result.success) {
                showNotification('Order cancelled successfully', 'success');
                setTimeout(() => location.reload(), 1500);
            } else {
                showNotification('Failed to cancel order: ' + result.error, 'error');
            }
        } else {
            showNotification('Failed to cancel order. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Error cancelling order:', error);
        showNotification('An error occurred while cancelling the order.', 'error');
    }
}

// Open review modal
async function openReviewModal(orderItemId) {
    const modal = document.getElementById('reviewModal');
    const reviewForm = document.getElementById('reviewForm');
    
    if (!modal || !reviewForm) return;
    
    try {
        // Load review form
        const response = await fetch(`/buyer/review/write/${orderItemId}`);
        if (response.ok) {
            const html = await response.text();
            reviewForm.innerHTML = html;
            modal.classList.add('active');
        } else {
            showNotification('Failed to load review form', 'error');
        }
    } catch (error) {
        console.error('Error loading review form:', error);
        showNotification('An error occurred while loading the review form', 'error');
    }
}

// Close review modal
function closeReviewModal() {
    const modal = document.getElementById('reviewModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

// Close image modal
function closeImageModal() {
    const modal = document.getElementById('imageModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

// Show image modal
function showImageModal(imageSrc) {
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    
    if (modal && modalImage) {
        modalImage.src = imageSrc;
        modal.classList.add('active');
    }
}

// Submit review
async function submitReview(orderItemId) {
    const form = document.getElementById('reviewFormContent');
    if (!form) return;
    
    const formData = new FormData(form);
    const reviewData = {
        rating: parseInt(formData.get('rating')),
        title: formData.get('title'),
        comment: formData.get('comment'),
        images: [] // TODO: Handle image uploads
    };
    
    if (!reviewData.rating) {
        showNotification('Please select a rating', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`/buyer/review/write/${orderItemId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',
            body: JSON.stringify(reviewData)
        });
        
        if (response.ok) {
            const result = await response.json();
            if (result.success) {
                showNotification('Review submitted successfully!', 'success');
                closeReviewModal();
                setTimeout(() => location.reload(), 1500);
            } else {
                showNotification('Failed to submit review: ' + result.error, 'error');
            }
        } else {
            showNotification('Failed to submit review. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Error submitting review:', error);
        showNotification('An error occurred while submitting the review.', 'error');
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="ri-${getNotificationIcon(type)}-line"></i>
            <span>${message}</span>
        </div>
    `;

    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--surface);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: 1rem;
        box-shadow: var(--shadow-xl);
        z-index: 10000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        max-width: 400px;
    `;

    // Add type-specific styles
    if (type === 'success') {
        notification.style.borderColor = 'var(--success-color)';
        notification.style.color = 'var(--success-color)';
    } else if (type === 'error') {
        notification.style.borderColor = 'var(--danger-color)';
        notification.style.color = 'var(--danger-color)';
    } else if (type === 'warning') {
        notification.style.borderColor = 'var(--warning-color)';
        notification.style.color = 'var(--warning-color)';
    }

    // Add to page
    document.body.appendChild(notification);

    // Show notification
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);

    // Remove notification
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 4000);
}

// Get notification icon
function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'error-warning',
        warning: 'alert-triangle',
        info: 'information'
    };
    return icons[type] || 'information';
}