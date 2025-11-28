// Dropdown functionality
function toggleDropdown(button) {
    const dropdownItem = button.closest('.dropdown-item');
    const isActive = dropdownItem.classList.contains('active');
    
    // Close all other dropdowns
    document.querySelectorAll('.dropdown-item.active').forEach(item => {
        if (item !== dropdownItem) {
            item.classList.remove('active');
        }
    });
    
    // Toggle current dropdown
    if (isActive) {
        dropdownItem.classList.remove('active');
    } else {
        dropdownItem.classList.add('active');
    }
    
    // Add visual feedback
    button.style.transform = 'scale(0.98)';
    setTimeout(() => {
        button.style.transform = '';
    }, 150);
}

// Store action functions
function followStore(storeId) {
    const followBtn = event.target.closest('.follow-btn');
    const isFollowing = followBtn.classList.contains('following');
    
    if (isFollowing) {
        followBtn.classList.remove('following');
        followBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M22 11l-3-3m0 0l-3 3m3-3v12"></path>
            </svg>
            Follow
        `;
    } else {
        followBtn.classList.add('following');
        followBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 6L9 17l-5-5"></path>
            </svg>
            Following
        `;
    }
    
    // Add visual feedback
    followBtn.style.transform = 'scale(0.95)';
    setTimeout(() => {
        followBtn.style.transform = '';
    }, 150);
    
    // Here you would make an API call to follow/unfollow the store
    console.log(`${isFollowing ? 'Unfollowed' : 'Followed'} store ID: ${storeId}`);
}

function chatWithStore(storeId) {
    const chatBtn = event.target.closest('.chat-btn');
    
    // Add visual feedback
    chatBtn.style.transform = 'scale(0.95)';
    setTimeout(() => {
        chatBtn.style.transform = '';
    }, 150);
    
    // Here you would typically open a chat widget or redirect to chat
    console.log(`Opening chat with store ID: ${storeId}`);
    alert('Opening chat with store...');
}

// Initialize dropdowns on page load
document.addEventListener('DOMContentLoaded', function() {
    // Add click event listeners to all dropdown headers
    document.querySelectorAll('.dropdown-header').forEach(header => {
        header.addEventListener('click', function() {
            toggleDropdown(this);
        });
    });
    
    console.log('Product dropdown details initialized');
});



// Product card interactions are now handled by _product_card.js

// No longer needed - dropdowns converted to static content

// Enhanced product card interactions are now handled by _product_card.js

// View More Products functionality
function viewMoreProducts() {
    // Add visual feedback
    const viewMoreBtn = document.querySelector('.view-more-btn');
    viewMoreBtn.style.transform = 'scale(0.95)';
    setTimeout(() => {
        viewMoreBtn.style.transform = '';
    }, 150);
    
    // Here you would typically navigate to a products listing page
    console.log('Navigating to more products...');
    // Example: window.location.href = '/products/tops';
    alert('Redirecting to view more similar products...');
}