// Force photo upload to work - Simple and direct approach
console.log("🚀 Force photo upload fix loading...");

// Wait for DOM to be ready
function waitForDOM(callback) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', callback);
    } else {
        callback();
    }
}

// Simple photo upload handler
function handlePhotoUpload(photoBox) {
    const input = photoBox.querySelector('input[type="file"]');
    if (!input) {
        console.error("No file input found");
        return;
    }
    
    console.log("Setting up photo upload for:", photoBox);
    
    // Click handler
    photoBox.onclick = function(e) {
        console.log("Photo box clicked!");
        e.preventDefault();
        e.stopPropagation();
        
        // Don't trigger on images or remove buttons
        if (e.target.tagName === 'IMG' || e.target.classList.contains('remove-photo')) {
            return;
        }
        
        input.click();
    };
    
    // File change handler
    input.onchange = function(e) {
        const file = this.files[0];
        console.log("File selected:", file);
        
        if (!file) return;
        
        // Validate
        if (!file.type.startsWith('image/')) {
            alert('Please select an image file');
            this.value = '';
            return;
        }
        
        if (file.size > 5 * 1024 * 1024) {
            alert('File too large. Max 5MB');
            this.value = '';
            return;
        }
        
        // Create preview
        const reader = new FileReader();
        reader.onload = function(event) {
            // Clear existing
            const existingImg = photoBox.querySelector('img.upload-thumb');
            const existingBtn = photoBox.querySelector('.remove-photo');
            if (existingImg) existingImg.remove();
            if (existingBtn) existingBtn.remove();
            
            // Create image
            const img = document.createElement('img');
            img.className = 'upload-thumb';
            img.src = event.target.result;
            img.style.cssText = 'width:100%;height:100%;object-fit:cover;border-radius:8px;position:absolute;top:0;left:0;';
            
            // Create remove button
            const removeBtn = document.createElement('button');
            removeBtn.type = 'button';
            removeBtn.className = 'remove-photo';
            removeBtn.innerHTML = '×';
            removeBtn.style.cssText = 'position:absolute;top:2px;right:2px;width:20px;height:20px;background:rgba(239,68,68,0.9);color:white;border:none;border-radius:50%;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:14px;z-index:10;';
            
            removeBtn.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                input.value = '';
                img.remove();
                removeBtn.remove();
                const placeholder = photoBox.querySelector('.photo-upload-content');
                if (placeholder) placeholder.style.display = '';
                photoBox.style.position = '';
            };
            
            // Add to photo box
            const placeholder = photoBox.querySelector('.photo-upload-content');
            if (placeholder) placeholder.style.display = 'none';
            photoBox.style.position = 'relative';
            photoBox.appendChild(img);
            photoBox.appendChild(removeBtn);
            
            console.log("Photo preview created!");
        };
        
        reader.readAsDataURL(file);
    };
}

// Initialize all photo boxes
function initPhotoBoxes() {
    const photoBoxes = document.querySelectorAll('.photo-upload-box');
    console.log("Found photo boxes:", photoBoxes.length);
    
    photoBoxes.forEach((box, index) => {
        console.log(`Setting up photo box ${index + 1}`);
        handlePhotoUpload(box);
    });
    
    if (photoBoxes.length === 0) {
        console.warn("No photo boxes found, retrying...");
        setTimeout(initPhotoBoxes, 1000);
    }
}

// Run initialization
waitForDOM(function() {
    console.log("DOM ready, initializing photo boxes...");
    initPhotoBoxes();
    
    // Also try after delays
    setTimeout(initPhotoBoxes, 500);
    setTimeout(initPhotoBoxes, 1000);
    setTimeout(initPhotoBoxes, 2000);
});

// Global function for manual initialization
window.forceInitPhotoBoxes = initPhotoBoxes;

console.log("✅ Force photo upload fix loaded");