// Variant Photo Upload Handler
// Handles photo upload functionality for product variant tables

(function () {
  console.log("🔧 Variant photo upload handler loading...");

  // Setup photo upload for all photo boxes
  function initializePhotoUploads() {
    const photoBoxes = document.querySelectorAll(".photo-upload-box");
    console.log(`Found ${photoBoxes.length} photo boxes to initialize`);

    photoBoxes.forEach((photoBox, index) => {
      setupPhotoBox(photoBox, index);
    });
  }

  function setupPhotoBox(photoBox, index = 0) {
    if (!photoBox || photoBox.dataset.photoSetup === "true") {
      console.log("Photo box already set up or invalid:", photoBox);
      return;
    }

    console.log(`Setting up photo box ${index}:`, photoBox);

    let input = photoBox.querySelector('input[type="file"]');
    if (!input) {
      // Create file input if it doesn't exist
      input = document.createElement("input");
      input.type = "file";
      input.accept = "image/*";
      input.style.display = "none";
      photoBox.appendChild(input);
      console.log("Created new file input for photo box");
    }

    // Mark as set up to prevent duplicate handlers
    photoBox.dataset.photoSetup = "true";

    // Add click handler to photo box
    photoBox.addEventListener("click", function (e) {
      console.log("Photo box clicked!");

      // Don't trigger on existing images or remove buttons
      if (
        e.target.tagName === "IMG" ||
        e.target.classList.contains("remove-photo") ||
        e.target.closest(".remove-photo")
      ) {
        return;
      }

      e.preventDefault();
      e.stopPropagation();
      input.click();
    });

    // Add change handler to file input
    input.addEventListener("change", function (e) {
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

      // Show loading state
      showLoadingState(photoBox);

      // Create preview
      const reader = new FileReader();
      reader.onload = function (ev) {
        displayImagePreview(photoBox, ev.target.result, file.name);
      };

      reader.onerror = function () {
        console.error("Error reading file");
        hideLoadingState(photoBox);
        alert("Error reading the selected image file.");
      };

      reader.readAsDataURL(file);
    });

    console.log(`Photo box ${index} setup complete`);
  }

  function showLoadingState(photoBox) {
    let progressEl = photoBox.querySelector(".upload-progress");
    if (!progressEl) {
      progressEl = document.createElement("div");
      progressEl.className = "upload-progress";
      progressEl.innerHTML = '<div class="progress-bar"></div>';
      progressEl.style.cssText = `
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(162, 89, 247, 0.1);
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 8px;
                z-index: 1;
            `;
      photoBox.appendChild(progressEl);
    }
    progressEl.style.display = "flex";

    // Animate progress bar
    const progressBar = progressEl.querySelector(".progress-bar");
    if (progressBar) {
      progressBar.style.cssText = `
                width: 30px;
                height: 30px;
                border: 3px solid #a259f7;
                border-top-color: transparent;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            `;
    }
  }

  function hideLoadingState(photoBox) {
    const progressEl = photoBox.querySelector(".upload-progress");
    if (progressEl) {
      progressEl.style.display = "none";
    }
  }

  function displayImagePreview(photoBox, imageSrc, fileName) {
    console.log("Displaying image preview for:", fileName);

    // Hide loading state
    hideLoadingState(photoBox);

    // Clear existing content except the file input
    const input = photoBox.querySelector('input[type="file"]');
    photoBox.innerHTML = "";
    photoBox.appendChild(input);

    // Set photo box style for image display
    photoBox.style.cssText = `
            width: 50px;
            height: 50px;
            position: relative;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            cursor: pointer;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto;
        `;

    // Create image element
    const img = document.createElement("img");
    img.className = "upload-thumb";
    img.src = imageSrc;
    img.alt = "Variant photo";
    img.title = "Click to change photo";
    img.style.cssText = `
            width: 100%; 
            height: 100%; 
            object-fit: cover; 
            border-radius: 6px; 
            display: block;
        `;

    // Create remove button
    const removeBtn = document.createElement("button");
    removeBtn.type = "button";
    removeBtn.className = "remove-photo";
    removeBtn.innerHTML = '<i class="ri-close-line"></i>';
    removeBtn.title = "Remove photo";
    removeBtn.style.cssText = `
            position: absolute;
            top: -2px;
            right: -2px;
            width: 18px;
            height: 18px;
            background: rgba(239, 68, 68, 0.9);
            color: white;
            border: none;
            border-radius: 50%;
            font-size: 10px;
            line-height: 1;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 2;
            transition: all 0.2s ease;
        `;

    // Add hover effect to remove button
    removeBtn.addEventListener("mouseenter", function () {
      this.style.background = "rgba(239, 68, 68, 1)";
      this.style.transform = "scale(1.1)";
    });

    removeBtn.addEventListener("mouseleave", function () {
      this.style.background = "rgba(239, 68, 68, 0.9)";
      this.style.transform = "scale(1)";
    });

    // Add remove functionality
    removeBtn.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      removePhoto(photoBox);
    });

    // Append elements
    photoBox.appendChild(img);
    photoBox.appendChild(removeBtn);

    console.log("Image preview displayed successfully");

    // Optional: Show success feedback
    showUploadFeedback(photoBox, "success");
  }

  function removePhoto(photoBox) {
    console.log("Removing photo from box:", photoBox);

    // Clear the file input
    const input = photoBox.querySelector('input[type="file"]');
    if (input) {
      input.value = "";
    }

    // Reset photo box to original state
    photoBox.innerHTML = "";
    photoBox.appendChild(input);

    // Reset photo box styling
    photoBox.style.cssText = `
            width: 50px;
            height: 50px;
            position: relative;
            border: 2px dashed #e5e7eb;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto;
            background: #f9fafb;
            transition: all 0.2s ease;
        `;

    // Add back the upload icon
    const uploadIcon = document.createElement("div");
    uploadIcon.className = "photo-upload-content";
    uploadIcon.innerHTML =
      '<i class="ri-image-add-line" style="font-size: 1.2rem; color: #a259f7"></i>';
    photoBox.appendChild(uploadIcon);

    console.log("Photo removed successfully");

    // Show removal feedback
    showUploadFeedback(photoBox, "removed");
  }

  function showUploadFeedback(photoBox, type) {
    const messages = {
      success: "✓ Uploaded",
      removed: "✗ Removed",
    };

    const colors = {
      success: "#10b981",
      removed: "#ef4444",
    };

    const feedback = document.createElement("div");
    feedback.className = "upload-feedback";
    feedback.textContent = messages[type];
    feedback.style.cssText = `
            position: absolute;
            top: -25px;
            left: 50%;
            transform: translateX(-50%);
            background: ${colors[type]};
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 10px;
            white-space: nowrap;
            z-index: 100;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;

    photoBox.style.position = "relative";
    photoBox.appendChild(feedback);

    // Animate in
    setTimeout(() => {
      feedback.style.opacity = "1";
    }, 100);

    // Remove after delay
    setTimeout(() => {
      feedback.style.opacity = "0";
      setTimeout(() => {
        if (feedback.parentNode) {
          feedback.parentNode.removeChild(feedback);
        }
      }, 300);
    }, 2000);
  }

  // Setup function for new variant rows
  function setupNewVariantRow(row) {
    const photoBoxes = row.querySelectorAll(".photo-upload-box");
    photoBoxes.forEach((photoBox, index) => {
      setupPhotoBox(photoBox, index);
    });
  }

  // Initialize when DOM is loaded
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      setTimeout(initializePhotoUploads, 500);
    });
  } else {
    setTimeout(initializePhotoUploads, 500);
  }

  // Re-initialize when new rows are added
  document.addEventListener("click", function (e) {
    if (e.target.id === "addVariantBtn" || e.target.closest("#addVariantBtn")) {
      setTimeout(initializePhotoUploads, 100);
    }
  });

  // Add CSS animations
  if (!document.querySelector("#variant-photo-styles")) {
    const style = document.createElement("style");
    style.id = "variant-photo-styles";
    style.textContent = `
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .photo-upload-box:hover {
                border-color: #a259f7;
                background: #faf5ff;
            }
            
            .photo-upload-box.grey:hover {
                border-color: #a259f7;
                background: #faf5ff;
            }
            
            .upload-thumb {
                transition: transform 0.2s ease;
            }
            
            .photo-upload-box:hover .upload-thumb {
                transform: scale(1.02);
            }
        `;
    document.head.appendChild(style);
  }

  // Export functions for external use
  window.variantPhotoUpload = {
    initializePhotoUploads,
    setupPhotoBox,
    setupNewVariantRow,
  };

  console.log("✅ Variant photo upload handler loaded successfully");
})();
