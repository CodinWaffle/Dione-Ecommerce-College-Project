// Follow Button functionality
const followBtn = document.getElementById('followBtn');
let isFollowing = false;

followBtn.addEventListener('click', () => {
    isFollowing = !isFollowing;
    
    if (isFollowing) {
        followBtn.classList.add('following');
        followBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 6L9 17l-5-5"></path>
            </svg>
            <span>Following</span>
        `;
    } else {
        followBtn.classList.remove('following');
        followBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="m22 11-3-3m0 0-3 3m3-3v8"></path>
            </svg>
            <span>Follow</span>
        `;
    }
    
    // Add visual feedback
    followBtn.style.transform = 'scale(0.95)';
    setTimeout(() => {
        followBtn.style.transform = '';
    }, 150);
});

// Chat Now Button functionality
const chatBtn = document.getElementById('chatBtn');

chatBtn.addEventListener('click', () => {
    // Add visual feedback
    chatBtn.style.transform = 'scale(0.95)';
    setTimeout(() => {
        chatBtn.style.transform = '';
    }, 150);
    
    // Here you would typically open a chat widget or redirect to chat
    alert('Opening chat with Fashion Forward Boutique...');
    console.log('Chat initiated with store');
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