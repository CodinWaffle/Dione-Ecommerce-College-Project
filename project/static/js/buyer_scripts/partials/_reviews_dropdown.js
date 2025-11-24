// Reviews Grid JavaScript
let userLikedReviews = new Set(); // Track user's liked reviews
let allReviews = []; // Store all reviews for filtering/sorting
let currentFilters = {
    sort: 'newest',
    rating: 'all',
    variation: 'all'
};

// Toggle individual review menu
function toggleReviewMenu(reviewId) {
    const menu = document.getElementById(`reviewMenu${reviewId}`);
    const allMenus = document.querySelectorAll('.dropdown-menu');
    
    // Close all other menus first
    allMenus.forEach(m => {
        if (m !== menu) {
            m.classList.remove('show');
        }
    });
    
    // Toggle current menu
    menu.classList.toggle('show');
}

// Close review menus when clicking outside
document.addEventListener('click', function(event) {
    const menus = document.querySelectorAll('.dropdown-menu');
    const menuBtns = document.querySelectorAll('.menu-btn');
    
    let clickedOnMenu = false;
    menuBtns.forEach(btn => {
        if (btn.contains(event.target)) {
            clickedOnMenu = true;
        }
    });
    
    menus.forEach(menu => {
        if (!menu.contains(event.target) && !clickedOnMenu) {
            menu.classList.remove('show');
        }
    });
});

// Edit review function
function editReview(reviewId) {
    const reviewTextElement = document.querySelector(`#reviewText${reviewId} p`);
    const currentText = reviewTextElement.textContent;
    
    // Create textarea for editing
    const textarea = document.createElement('textarea');
    textarea.value = currentText;
    textarea.style.width = '100%';
    textarea.style.minHeight = '80px';
    textarea.style.padding = '10px';
    textarea.style.border = '2px solid #3b82f6';
    textarea.style.borderRadius = '6px';
    textarea.style.fontSize = '14px';
    textarea.style.fontFamily = 'inherit';
    textarea.style.resize = 'vertical';
    
    // Create save and cancel buttons
    const buttonContainer = document.createElement('div');
    buttonContainer.style.marginTop = '10px';
    buttonContainer.style.display = 'flex';
    buttonContainer.style.gap = '8px';
    
    const saveBtn = document.createElement('button');
    saveBtn.textContent = 'Save';
    saveBtn.style.padding = '6px 12px';
    saveBtn.style.backgroundColor = '#3b82f6';
    saveBtn.style.color = 'white';
    saveBtn.style.border = 'none';
    saveBtn.style.borderRadius = '4px';
    saveBtn.style.cursor = 'pointer';
    saveBtn.style.fontWeight = '500';
    saveBtn.style.fontSize = '12px';
    
    const cancelBtn = document.createElement('button');
    cancelBtn.textContent = 'Cancel';
    cancelBtn.style.padding = '6px 12px';
    cancelBtn.style.backgroundColor = '#6b7280';
    cancelBtn.style.color = 'white';
    cancelBtn.style.border = 'none';
    cancelBtn.style.borderRadius = '4px';
    cancelBtn.style.cursor = 'pointer';
    cancelBtn.style.fontWeight = '500';
    cancelBtn.style.fontSize = '12px';
    
    buttonContainer.appendChild(saveBtn);
    buttonContainer.appendChild(cancelBtn);
    
    // Replace review text with textarea
    const reviewContainer = document.getElementById(`reviewText${reviewId}`);
    reviewContainer.innerHTML = '';
    reviewContainer.appendChild(textarea);
    reviewContainer.appendChild(buttonContainer);
    
    // Focus on textarea
    textarea.focus();
    
    // Save functionality
    saveBtn.addEventListener('click', function() {
        const newText = textarea.value.trim();
        if (newText) {
            // Here you would typically make an AJAX call to update the review
            updateReviewOnServer(reviewId, newText);
            reviewContainer.innerHTML = `<p>${newText}</p>`;
            showNotification('Review updated successfully!', 'success');
        } else {
            showNotification('Review cannot be empty!', 'error');
        }
    });
    
    // Cancel functionality
    cancelBtn.addEventListener('click', function() {
        reviewContainer.innerHTML = `<p>${currentText}</p>`;
    });
    
    // Close dropdown menu
    document.getElementById(`reviewMenu${reviewId}`).classList.remove('show');
}

// Remove review function
function removeReview(reviewId) {
    if (confirm('Are you sure you want to remove this review? This action cannot be undone.')) {
        const reviewCard = document.querySelector(`[data-review-id="${reviewId}"]`);
        reviewCard.style.transform = 'scale(0.95)';
        reviewCard.style.opacity = '0.5';
        
        setTimeout(() => {
            // Here you would typically make an AJAX call to delete the review
            deleteReviewOnServer(reviewId);
            reviewCard.style.display = 'none';
            showNotification('Review removed successfully!', 'success');
            updateReviewCount(-1);
        }, 300);
    }
    
    // Close dropdown menu
    document.getElementById(`reviewMenu${reviewId}`).classList.remove('show');
}

// Toggle like function
function toggleReviewLike(reviewId) {
    const likeBtn = document.getElementById(`likeBtn${reviewId}`);
    const heartIcon = document.getElementById(`heartIcon${reviewId}`);
    const likeCountElement = document.getElementById(`likeCount${reviewId}`);
    
    let currentCount = parseInt(likeCountElement.textContent) || 0;
    let isLiked = userLikedReviews.has(reviewId);
    
    if (!isLiked) {
        // Like the review
        heartIcon.className = 'fas fa-heart';
        likeBtn.classList.add('liked');
        currentCount++;
        userLikedReviews.add(reviewId);
        
        // Add animation
        heartIcon.style.transform = 'scale(1.2)';
        setTimeout(() => {
            heartIcon.style.transform = 'scale(1)';
        }, 200);
        
        // Here you would typically make an AJAX call to like the review
        likeReviewOnServer(reviewId);
    } else {
        // Unlike the review
        heartIcon.className = 'far fa-heart';
        likeBtn.classList.remove('liked');
        currentCount--;
        userLikedReviews.delete(reviewId);
        
        // Here you would typically make an AJAX call to unlike the review
        unlikeReviewOnServer(reviewId);
    }
    
    likeCountElement.textContent = currentCount;
}

// Load more reviews
function loadMoreReviews() {
    const currentReviews = document.querySelectorAll('.review-card').length;
    
    // Here you would typically make an AJAX call to load more reviews
    // For now, we'll just show a notification
    showNotification('Loading more reviews...', 'info');
    
    // Simulate loading
    setTimeout(() => {
        showNotification('No more reviews to load', 'info');
    }, 1000);
}

// Image lightbox functions
function openImageLightbox(imageSrc) {
    const lightbox = document.getElementById('imageLightbox');
    const lightboxImage = document.getElementById('lightboxImage');
    
    lightboxImage.src = imageSrc;
    lightbox.style.display = 'block';
    
    // Prevent body scrolling
    document.body.style.overflow = 'hidden';
}

function closeLightbox() {
    const lightbox = document.getElementById('imageLightbox');
    lightbox.style.display = 'none';
    
    // Restore body scrolling
    document.body.style.overflow = 'auto';
}

// Close lightbox when clicking outside the image
document.addEventListener('click', function(event) {
    const lightbox = document.getElementById('imageLightbox');
    const lightboxImage = document.getElementById('lightboxImage');
    
    if (lightbox && event.target === lightbox) {
        closeLightbox();
    }
});

// Close lightbox with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeLightbox();
    }
});

// Show notification function
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    
    // Styling
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.padding = '12px 20px';
    notification.style.borderRadius = '8px';
    notification.style.color = 'white';
    notification.style.fontWeight = '500';
    notification.style.zIndex = '2000';
    notification.style.transform = 'translateX(100%)';
    notification.style.transition = 'transform 0.3s ease';
    notification.style.fontSize = '14px';
    
    // Color based on type
    if (type === 'success') {
        notification.style.backgroundColor = '#059669';
    } else if (type === 'error') {
        notification.style.backgroundColor = '#dc2626';
    } else {
        notification.style.backgroundColor = '#3b82f6';
    }
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Update review count in UI (for future implementation)
function updateReviewCount(change) {
    const totalReviewsElement = document.querySelector('.total-reviews');
    if (totalReviewsElement) {
        const currentText = totalReviewsElement.textContent;
        const currentCount = parseInt(currentText.match(/\d+/)[0]) || 0;
        const newCount = Math.max(0, currentCount + change);
        totalReviewsElement.textContent = `Based on ${newCount} reviews`;
    }
}

// Server communication functions (these would be implemented with actual AJAX calls)
function updateReviewOnServer(reviewId, newText) {
    // Implementation would go here
    console.log(`Updating review ${reviewId} with text: ${newText}`);
}

function deleteReviewOnServer(reviewId) {
    // Implementation would go here
    console.log(`Deleting review ${reviewId}`);
}

function likeReviewOnServer(reviewId) {
    // Implementation would go here
    console.log(`Liking review ${reviewId}`);
}

function unlikeReviewOnServer(reviewId) {
    // Implementation would go here
    console.log(`Unliking review ${reviewId}`);
}

// Sort reviews function
function sortReviews(sortType) {
    currentFilters.sort = sortType;
    const reviewsGrid = document.querySelector('.reviews-grid');
    const reviewCards = Array.from(reviewsGrid.querySelectorAll('.review-card'));
    
    // Add sorting indicator
    document.getElementById('reviewSortSelect').classList.add('filter-active');
    
    reviewCards.sort((a, b) => {
        switch (sortType) {
            case 'newest':
                // Sort by newest first (assuming data-created attribute exists)
                const dateA = new Date(a.dataset.created || '2023-01-01');
                const dateB = new Date(b.dataset.created || '2023-01-01');
                return dateB - dateA;
                
            case 'oldest':
                // Sort by oldest first
                const oldDateA = new Date(a.dataset.created || '2023-01-01');
                const oldDateB = new Date(b.dataset.created || '2023-01-01');
                return oldDateA - oldDateB;
                
            case 'highest-rating':
                // Sort by highest rating first
                const ratingA = parseInt(a.querySelector('.stars').dataset.rating) || 0;
                const ratingB = parseInt(b.querySelector('.stars').dataset.rating) || 0;
                return ratingB - ratingA;
                
            case 'lowest-rating':
                // Sort by lowest rating first
                const lowRatingA = parseInt(a.querySelector('.stars').dataset.rating) || 0;
                const lowRatingB = parseInt(b.querySelector('.stars').dataset.rating) || 0;
                return lowRatingA - lowRatingB;
                
            case 'most-helpful':
                // Sort by most helpful (assuming data-helpful attribute exists)
                const helpfulA = parseInt(a.dataset.helpful) || 0;
                const helpfulB = parseInt(b.dataset.helpful) || 0;
                return helpfulB - helpfulA;
                
            default:
                return 0;
        }
    });
    
    // Clear and re-append sorted cards
    reviewsGrid.innerHTML = '';
    reviewCards.forEach(card => {
        reviewsGrid.appendChild(card);
    });
    
    // Animate the reordered cards
    animateReviewCards();
    showNotification(`Reviews sorted by ${sortType.replace('-', ' ')}`, 'info');
}

// Filter reviews function
function filterReviews(filterType) {
    currentFilters.rating = filterType;
    const reviewCards = document.querySelectorAll('.review-card');
    
    // Add filtering indicator
    const filterSelect = document.getElementById('reviewFilterSelect');
    if (filterType !== 'all') {
        filterSelect.classList.add('filter-active');
    } else {
        filterSelect.classList.remove('filter-active');
    }
    
    reviewCards.forEach(card => {
        let shouldShow = true;
        
        switch (filterType) {
            case 'all':
                shouldShow = true;
                break;
                
            case '5-stars':
            case '4-stars':
            case '3-stars':
            case '2-stars':
            case '1-star':
                const targetRating = parseInt(filterType.charAt(0));
                const cardRating = parseInt(card.querySelector('.stars').dataset.rating) || 0;
                shouldShow = cardRating === targetRating;
                break;
                
            case 'with-photos':
                shouldShow = card.querySelector('.product-media') !== null;
                break;
                
            case 'verified-only':
                shouldShow = card.querySelector('.verified-buyer') !== null;
                break;
                
            default:
                shouldShow = true;
        }
        
        if (shouldShow) {
            card.style.display = 'block';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        } else {
            card.style.opacity = '0';
            card.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                card.style.display = 'none';
            }, 300);
        }
    });
    
    // Update review count display
    updateVisibleReviewCount();
    
    if (filterType !== 'all') {
        showNotification(`Filtered reviews by ${filterType.replace('-', ' ')}`, 'info');
    }
}

// Filter by variation function
function filterByVariation(variation) {
    currentFilters.variation = variation;
    const reviewCards = document.querySelectorAll('.review-card');
    
    // Add filtering indicator
    const variationSelect = document.getElementById('variationFilterSelect');
    if (variation !== 'all') {
        variationSelect.classList.add('filter-active');
    } else {
        variationSelect.classList.remove('filter-active');
    }
    
    reviewCards.forEach(card => {
        let shouldShow = true;
        
        if (variation !== 'all') {
            const variationElement = card.querySelector('.variation-details');
            if (variationElement) {
                const cardVariation = variationElement.textContent.trim();
                // Convert variation format (e.g., "XS-Black" to "Size XS, Color Black")
                const [size, color] = variation.split('-');
                const expectedVariation = `Size ${size}, Color ${color}`;
                shouldShow = cardVariation.includes(size) && cardVariation.includes(color);
            } else {
                shouldShow = false; // Hide reviews without variation info when filtering
            }
        }
        
        if (shouldShow) {
            card.style.display = 'block';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        } else {
            card.style.opacity = '0';
            card.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                card.style.display = 'none';
            }, 300);
        }
    });
    
    // Update review count display
    updateVisibleReviewCount();
    
    if (variation !== 'all') {
        const [size, color] = variation.split('-');
        showNotification(`Filtered reviews for ${size} - ${color}`, 'info');
    }
}

// Clear all filters function
function clearAllFilters() {
    // Reset all selects
    document.getElementById('reviewSortSelect').value = 'newest';
    document.getElementById('reviewFilterSelect').value = 'all';
    document.getElementById('variationFilterSelect').value = 'all';
    
    // Remove active indicators
    document.getElementById('reviewSortSelect').classList.remove('filter-active');
    document.getElementById('reviewFilterSelect').classList.remove('filter-active');
    document.getElementById('variationFilterSelect').classList.remove('filter-active');
    
    // Reset current filters
    currentFilters = {
        sort: 'newest',
        rating: 'all',
        variation: 'all'
    };
    
    // Show all reviews
    const reviewCards = document.querySelectorAll('.review-card');
    reviewCards.forEach(card => {
        card.style.display = 'block';
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
    });
    
    // Re-sort by newest
    sortReviews('newest');
    
    // Update review count display
    updateVisibleReviewCount();
    
    showNotification('All filters cleared', 'info');
}

// Update visible review count
function updateVisibleReviewCount() {
    const allCards = document.querySelectorAll('.review-card');
    const visibleCards = document.querySelectorAll('.review-card[style*="display: block"], .review-card:not([style*="display: none"])');
    
    // Update the total reviews count in the header
    const totalReviewsElement = document.querySelector('.total-reviews');
    if (totalReviewsElement) {
        const totalCount = allCards.length;
        const visibleCount = visibleCards.length;
        
        if (visibleCount === totalCount) {
            totalReviewsElement.textContent = `Based on ${totalCount} reviews`;
        } else {
            totalReviewsElement.textContent = `Showing ${visibleCount} of ${totalCount} reviews`;
        }
    }
}

// Animate review cards
function animateReviewCards() {
    const reviewCards = document.querySelectorAll('.review-card[style*="display: block"], .review-card:not([style*="display: none"])');
    
    reviewCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 50);
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Add smooth transitions
    const reviewCards = document.querySelectorAll('.review-card');
    reviewCards.forEach(card => {
        card.style.transition = 'all 0.3s ease';
        
        // Add mock data attributes for sorting (in a real app, this would come from the server)
        if (!card.dataset.created) {
            const randomDate = new Date(2023, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1);
            card.dataset.created = randomDate.toISOString();
        }
        if (!card.dataset.helpful) {
            card.dataset.helpful = Math.floor(Math.random() * 50);
        }
    });
    
    // Initialize user liked reviews (this would typically come from the server)
    // For demo purposes, we'll leave it empty
    userLikedReviews = new Set();
    
    // Store all reviews for filtering
    allReviews = Array.from(reviewCards);
    
    // Add staggered animation to review cards on load
    reviewCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // Initialize review count
    updateVisibleReviewCount();
    
    console.log('Reviews grid initialized with sorting and filtering');
});