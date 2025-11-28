// Immediate fix for photo upload functionality
// Add this script to the add_product_stocks.html template

(function() {
    console.log("🔧 Immediate photo upload fix loading...");
    
    function setupPhotoBox(photoBox) {
        if (!photoBox) return;
        
        console.log("Setting up photo box:", photoBox);
        
        const input = photoBox.querySelector('input[type="file"]');
        if (!input) {
            console.error("No file input found in photo box");
            return;
        }
        
        // Remove any existing listeners to prevent duplicates
        const newPhotoBox = photoBox.cloneNode(true);
        photoBox.parentNode.replaceChild(newPhotoBox, photoBox);
        
        const newInput = newPhotoBox.querySelector('input[type="file"]');
        
        // Add click handler to photo box
        newPhotoBox.addEventListener("click", function(e) {
            console.log("Photo box clicked!");
            
            // Don't trigger on existing images or remove buttons
            if (e.target.tagName === "IMG" || 
                e.target.classList.contains("remove-photo") ||
                e.target.closest(".remove-photo")) {
                return;
            }
            
            e.preventDefault();
            e.stopPropagation();
            newInput.click();
        });
        
        // Add change handler to file input
        newInput.addEventListener("change", function(e) {
            console.log("File input changed:", this.files);
            
            const file = this.files && this.files[0];
            if (!file) return;
            
            // Validate file type
            if (!file.type.startsWith("image/")) {
                alert("Please select a valid image file.");
                this.value = "";
                return;
            }
            
            // Validate file size (max 5MB)
            if (file.size > 5 * 1024 * 1024) {
                alert("Image file size must be less than 5MB.");
                this.value = "";
                return;
            }
            
            // Create preview
            const reader = new FileReader();
            reader.onload = function(ev) {
                // Clear existing content
                const existingImages = newPhotoBox.querySelectorAll("img.upload-thumb");
                const existingRemove = newPhotoBox.querySelectorAll(".remove-photo");
                existingImages.forEach(img => img.remove());
                existingRemove.forEach(btn => btn.remove());
                
                // Create image
                const img = document.createElement("img");
                img.className = "upload-thumb";
                img.src = ev.target.result;
                img.alt = "Variant photo";
                img.style.cssText = `
                    width: 100%; 
                    height: 100%; 
                    object-fit: cover; 
                    border-radius: 8px; 
                    display: block;
                    position: absolute;
                    top: 0;
                    left: 0;
                `;
                
                // Create remove button
                const removeBtn = document.createElement("button");
                removeBtn.type = "button";
                removeBtn.className = "remove-photo";
                removeBtn.innerHTML = '<i class="ri-close-line"></i>';
                removeBtn.style.cssText = `
                    position: absolute;
                    top: 2px;
                    right: 2px;
                    width: 20px;
                    height: 20px;
                    background: rgba(239, 68, 68, 0.9);
                    color: white;
                    border: none;
                    border-radius: 50%;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 12px;
                    z-index: 10;
                `;
                
                removeBtn.addEventListener("click", function(removeEvent) {
                    removeEvent.preventDefault();
                    removeEvent.stopPropagation();
                    newInput.value = "";
                    img.remove();
                    removeBtn.remove();
                    const placeholder = newPhotoBox.querySelector(".photo-upload-content");
                    if (placeholder) placeholder.style.display = "";
                    newPhotoBox.style.position = "";
                });
                
                // Hide placeholder and add image
                const placeholder = newPhotoBox.querySelector(".photo-upload-content");
                if (placeholder) placeholder.style.display = "none";
                newPhotoBox.style.position = "relative";
                newPhotoBox.appendChild(img);
                newPhotoBox.appendChild(removeBtn);
                
                console.log("Photo preview created successfully");
            };
            
            reader.onerror = function() {
                console.error("Error reading file");
                alert("Error reading the selected file. Please try again.");
            };
            
            reader.readAsDataURL(file);
        });
        
        console.log("Photo box setup completed");
    }
    
    function initializeAllPhotoBoxes() {
        const photoBoxes = document.querySelectorAll(".photo-upload-box");
        console.log("Found photo boxes:", photoBoxes.length);
        
        photoBoxes.forEach((box, index) => {
            console.log(`Setting up photo box ${index + 1}`);
            setupPhotoBox(box);
        });
    }
    
    // Initialize immediately if DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeAllPhotoBoxes);
    } else {
        initializeAllPhotoBoxes();
    }
    
    // Also initialize after a delay to catch any dynamically added boxes
    setTimeout(initializeAllPhotoBoxes, 1000);
    setTimeout(initializeAllPhotoBoxes, 2000);
    
    // Make function globally available
    window.setupPhotoBox = setupPhotoBox;
    window.initializeAllPhotoBoxes = initializeAllPhotoBoxes;
    
    console.log("✅ Immediate photo upload fix loaded");
})();