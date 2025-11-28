// My Purchases Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('My Purchases page loaded');

    // Initialize functionality
    initOrderTabs();
    initReviewsDropdown();
    initWriteReviewModal();
    initReviewFilters();
    initStarRatings();
    initPhotoUpload();

    // Order Status Tabs
    function initOrderTabs() {
        const tabBtns = document.querySelectorAll('.tab-btn');
        const orderCards = document.querySelectorAll('.order-card');

        tabBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const status = this.dataset.status;
                
                // Update active tab
                tabBtns.forEach(tab => tab.classList.remove('active'));
                this.classList.add('active');

                // Filter orders
                filterOrders(status);
            });
        });

        function filterOrders(status) {
            orderCards.forEach(card => {
                const cardStatus = card.dataset.status;
                
                if (status === 'all' || cardStatus === status) {
                    card.style.display = 'block';
                    // Add animation
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    
                    setTimeout(() => {
                        card.style.transition = 'all 0.3s ease';
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 100);
                } else {
                    card.style.display = 'none';
                }
            });
        }
    }

    // Reviews Dropdown Toggle
    function initReviewsDropdown() {
        const reviewsToggles = document.querySelectorAll('.reviews-toggle');

        reviewsToggles.forEach(toggle => {
            toggle.addEventListener('click', function() {
                const orderId = this.dataset.order;
                const dropdown = document.getElementById(`reviews-${orderId}`);
                
                // Toggle active state
                this.classList.toggle('active');
                dropdown.classList.toggle('active');

                // Update button text and icon
                const icon = this.querySelector('.dropdown-icon');
                if (this.classList.contains('active')) {
                    // Scroll to reviews section smoothly
                    setTimeout(() => {
                        dropdown.scrollIntoView({ 
                            behavior: 'smooth', 
                            block: 'nearest' 
                        });
                    }, 300);
                }
            });
        });
    }

    // Write Review Modal
    function initWriteReviewModal() {
        const modal = document.getElementById('writeReviewModal');
        const reviewBtns = document.querySelectorAll('.btn-review');
        const closeBtn = document.getElementById('closeReviewModal');
        const cancelBtn = document.getElementById('cancelReview');
        const submitBtn = document.getElementById('submitReview');
        const reviewForm = document.getElementById('reviewForm');

        // Open modal
        reviewBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const productId = this.dataset.productId;
                const orderId = this.dataset.orderId;
                
                // Get product info from the order item
                const orderItem = this.closest('.order-item');
                const productName = orderItem.querySelector('.item-name').textContent;
                const productVariant = orderItem.querySelector('.item-variant').textContent;
                const productImage = orderItem.querySelector('.item-image').src;

                // Update modal content
                document.getElementById('reviewProductName').textContent = productName;
                document.getElementById('reviewProductVariant').textContent = productVariant;
                document.querySelector('.product-image').src = productImage;

                // Store data for submission
                reviewForm.dataset.productId = productId;
                reviewForm.dataset.orderId = orderId;

                // Show modal
                modal.classList.add('active');
                document.body.style.overflow = 'hidden';
            });
        });

        // Close modal
        function closeModal() {
            modal.classList.remove('active');
            document.body.style.overflow = '';
            resetReviewForm();
        }

        closeBtn.addEventListener('click', closeModal);
        cancelBtn.addEventListener('click', closeModal);

        // Close on backdrop click
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal();
            }
        });

        // Submit review
        reviewForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitReview();
        });

        function submitReview() {
            const formData = new FormData();
            const productId = reviewForm.dataset.productId;
            const orderId = reviewForm.dataset.orderId;

            // Get ratings
            const productRating = getStarRating('product');
            const storeRating = getStarRating('store');
            const deliveryRating = getStarRating('delivery');

            // Get review text
            const reviewText = document.getElementById('reviewText').value.trim();

            // Get photos
            const photos = document.getElementById('reviewPhotos').files;

            // Validate required fields
            if (!productRating || !storeRating || !deliveryRating) {
                showNotification('Please rate all categories', 'error');
                return;
            }

            if (!reviewText) {
                showNotification('Please write a review', 'error');
                return;
            }

            // Prepare form data
            formData.append('productId', productId);
            formData.append('orderId', orderId);
            formData.append('productRating', productRating);
            formData.append('storeRating', storeRating);
            formData.append('deliveryRating', deliveryRating);
            formData.append('reviewText', reviewText);

            // Add photos
            for (let i = 0; i < photos.length; i++) {
                formData.append('photos', photos[i]);
            }

            // Show loading state
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="ri-loader-4-line"></i> Submitting...';

            // Simulate API call (replace with actual endpoint)
            setTimeout(() => {
                // Success simulation
                showNotification('Review submitted successfully!', 'success');
                closeModal();
                
                // Update UI to show review was submitted
                const reviewBtn = document.querySelector(`[data-product-id="${productId}"]`);
                if (reviewBtn) {
                    reviewBtn.innerHTML = '<i class="ri-check-line"></i> Reviewed';
                    reviewBtn.disabled = true;
                    reviewBtn.style.background = '#00b894';
                }

                // Reset button
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="ri-send-plane-line"></i> Submit Review';
            }, 2000);
        }

        function resetReviewForm() {
            // Reset star ratings
            document.querySelectorAll('.star-rating i').forEach(star => {
                star.classList.remove('active');
                star.classList.add('ri-star-line');
                star.classList.remove('ri-star-fill');
            });

            // Reset text
            document.getElementById('reviewText').value = '';
            updateCharacterCount();

            // Reset photos
            document.getElementById('reviewPhotos').value = '';
            document.getElementById('photoPreview').innerHTML = '';
        }
    }

    // Review Filters
    function initReviewFilters() {
        const filterBtns = document.querySelectorAll('.btn-filter');

        filterBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const filter = this.dataset.filter;
                const reviewsList = this.closest('.reviews-dropdown').querySelector('.reviews-list');
                
                // Update active filter
                filterBtns.forEach(filterBtn => filterBtn.classList.remove('active'));
                this.classList.add('active');

                // Apply filter
                filterReviews(reviewsList, filter);
            });
        });

        function filterReviews(reviewsList, filter) {
            const reviewItems = reviewsList.querySelectorAll('.review-item');
            const noReviews = reviewsList.querySelector('.no-reviews');

            let visibleCount = 0;

            reviewItems.forEach(item => {
                let shouldShow = true;

                switch (filter) {
                    case 'photos':
                        shouldShow = item.querySelector('.review-photos') && 
                                   item.querySelector('.review-photos').children.length > 0;
                        break;
                    case 'recent':
                        // For demo, show all. In real app, sort by date
                        shouldShow = true;
                        break;
                    case 'all':
                    default:
                        shouldShow = true;
                        break;
                }

                if (shouldShow) {
                    item.style.display = 'block';
                    visibleCount++;
                } else {
                    item.style.display = 'none';
                }
            });

            // Show/hide no reviews message
            if (noReviews) {
                noReviews.style.display = visibleCount === 0 ? 'block' : 'none';
            }
        }
    }

    // Star Rating System
    function initStarRatings() {
        const starRatings = document.querySelectorAll('.star-rating');

        starRatings.forEach(rating => {
            const stars = rating.querySelectorAll('i');
            
            stars.forEach((star, index) => {
                star.addEventListener('click', function() {
                    const ratingValue = index + 1;
                    const ratingType = rating.dataset.rating;
                    
                    // Update visual state
                    updateStarDisplay(rating, ratingValue);
                    
                    // Store rating value
                    rating.dataset.value = ratingValue;
                    
                    // Update rating text
                    updateRatingText(rating, ratingValue);
                });

                star.addEventListener('mouseenter', function() {
                    const hoverValue = index + 1;
                    updateStarDisplay(rating, hoverValue, true);
                });
            });

            rating.addEventListener('mouseleave', function() {
                const currentValue = rating.dataset.value || 0;
                updateStarDisplay(rating, currentValue);
            });
        });

        function updateStarDisplay(rating, value, isHover = false) {
            const stars = rating.querySelectorAll('i');
            
            stars.forEach((star, index) => {
                if (index < value) {
                    star.classList.remove('ri-star-line');
                    star.classList.add('ri-star-fill');
                    star.classList.add('active');
                } else {
                    star.classList.remove('ri-star-fill');
                    star.classList.add('ri-star-line');
                    star.classList.remove('active');
                }
            });
        }

        function updateRatingText(rating, value) {
            const ratingText = rating.parentNode.querySelector('.rating-text');
            const ratingType = rating.dataset.rating;
            
            const texts = {
                product: ['Poor quality', 'Fair quality', 'Good quality', 'Very good quality', 'Excellent quality'],
                store: ['Poor service', 'Fair service', 'Good service', 'Very good service', 'Excellent service'],
                delivery: ['Very slow', 'Slow', 'On time', 'Fast', 'Very fast']
            };

            if (ratingText && texts[ratingType]) {
                ratingText.textContent = texts[ratingType][value - 1] || 'Rate this';
            }
        }
    }

    // Photo Upload
    function initPhotoUpload() {
        const photoInput = document.getElementById('reviewPhotos');
        const photoPreview = document.getElementById('photoPreview');
        const charCountElement = document.getElementById('charCount');
        const reviewTextarea = document.getElementById('reviewText');

        // Character count
        reviewTextarea.addEventListener('input', updateCharacterCount);

        function updateCharacterCount() {
            const count = reviewTextarea.value.length;
            charCountElement.textContent = count;
            
            if (count > 450) {
                charCountElement.style.color = '#e17055';
            } else {
                charCountElement.style.color = '#636e72';
            }
        }

        // Photo upload
        photoInput.addEventListener('change', function() {
            const files = Array.from(this.files);
            
            if (files.length > 5) {
                showNotification('Maximum 5 photos allowed', 'error');
                return;
            }

            photoPreview.innerHTML = '';
            
            files.forEach((file, index) => {
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    
                    reader.onload = function(e) {
                        const previewItem = document.createElement('div');
                        previewItem.className = 'preview-item';
                        
                        previewItem.innerHTML = `
                            <img src="${e.target.result}" alt="Preview">
                            <button type="button" class="remove-photo" data-index="${index}">
                                <i class="ri-close-line"></i>
                            </button>
                        `;
                        
                        photoPreview.appendChild(previewItem);
                    };
                    
                    reader.readAsDataURL(file);
                }
            });
        });

        // Remove photo
        photoPreview.addEventListener('click', function(e) {
            if (e.target.closest('.remove-photo')) {
                const index = parseInt(e.target.closest('.remove-photo').dataset.index);
                const previewItem = e.target.closest('.preview-item');
                
                // Remove from preview
                previewItem.remove();
                
                // Update file input (create new FileList without the removed file)
                const dt = new DataTransfer();
                const files = Array.from(photoInput.files);
                
                files.forEach((file, i) => {
                    if (i !== index) {
                        dt.items.add(file);
                    }
                });
                
                photoInput.files = dt.files;
            }
        });
    }

    // Helper Functions
    function getStarRating(type) {
        const rating = document.querySelector(`[data-rating="${type}"]`);
        return rating ? parseInt(rating.dataset.value || 0) : 0;
    }

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

        // Add to page
        document.body.appendChild(notification);

        // Show notification
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        // Remove notification
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    function getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'error-warning',
            warning: 'alert-triangle',
            info: 'information'
        };
        return icons[type] || 'information';
    }

    // Initialize character count on page load
    updateCharacterCount();

    function updateCharacterCount() {
        const reviewTextarea = document.getElementById('reviewText');
        const charCountElement = document.getElementById('charCount');
        
        if (reviewTextarea && charCountElement) {
            const count = reviewTextarea.value.length;
            charCountElement.textContent = count;
            
            if (count > 450) {
                charCountElement.style.color = '#e17055';
            } else {
                charCountElement.style.color = '#636e72';
            }
        }
    }

    console.log('My Purchases functionality initialized');
});