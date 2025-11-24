/**
 * Seller Settings Page JavaScript
 */
document.addEventListener("DOMContentLoaded", function () {
  // Profile Photo & Cover Photo Upload
  initPhotoUploads();

  // Form Submissions
  initFormSubmissions();

  // Password Strength Meter
  initPasswordStrengthMeter();

  // Two-Factor Authentication Toggle
  initTwoFactorToggle();

  // Theme Selection
  initThemeSelection();

  // Color Picker
  initColorPicker();

  // Initialize sidebar dropdown functionality
  initSidebarDropdowns();

  // Initial sidebar overflow check
  handleSidebarOverflow();

  // Check sidebar content on load complete (for images and other resources)
  window.addEventListener("load", handleSidebarOverflow);

  // Show active tab based on URL
  showActiveTabFromUrl();
});

/**
 * Handle sidebar overflow without showing scrollbars
 * This ensures all content is accessible when dropdowns are expanded
 */
function handleSidebarOverflow() {
  const sidebar = document.querySelector(".sidebar");
  const sidebarNav = document.querySelector(".sidebar-nav");
  const sidebarHeader = document.querySelector(".sidebar-header");
  const sidebarFooter = document.querySelector(".sidebar-footer");

  if (sidebar && sidebarNav) {
    // Calculate total content height including dropdowns
    const sidebarContentHeight =
      sidebarNav.scrollHeight +
      (sidebarHeader ? sidebarHeader.offsetHeight : 0) +
      (sidebarFooter ? sidebarFooter.offsetHeight : 0);

    // Check if the content exceeds viewport height
    if (sidebarContentHeight > window.innerHeight) {
      // Ensure sidebar is scrollable
      sidebar.style.overflowY = "auto";

      // Calculate how much we need to scroll to show active elements
      const activeDropdown = document.querySelector(".dropdown-menu.show");
      const activeItem = document.querySelector(
        ".nav-item.active, .dropdown-item.active"
      );

      if (activeItem) {
        // Smooth scroll to active item with offset for visibility
        setTimeout(() => {
          const itemTop = activeItem.offsetTop;
          const offset = window.innerHeight / 3;
          sidebar.scrollTop = Math.max(0, itemTop - offset);
        }, 100);
      }
    }
  }
}

/**
 * Initialize sidebar dropdown functionality
 */
function initSidebarDropdowns() {
  const dropdownToggles = document.querySelectorAll(".dropdown-toggle");

  // Initial check for sidebar overflow on page load
  handleSidebarOverflow();

  // Also check on window resize
  window.addEventListener("resize", handleSidebarOverflow);

  dropdownToggles.forEach((toggle) => {
    // Initialize dropdown state on page load
    const isActive = toggle.classList.contains("active");
    const dropdownMenu = toggle.nextElementSibling;

    if (isActive && dropdownMenu) {
      dropdownMenu.classList.add("show");
    }

    // Add click event listener
    toggle.addEventListener("click", function () {
      const dropdownMenu = this.nextElementSibling;

      if (dropdownMenu) {
        // Toggle dropdown visibility
        dropdownMenu.classList.toggle("show");

        // Handle potential overflow when dropdown opens/closes
        setTimeout(handleSidebarOverflow, 300);

        // If using icons that rotate, toggle that too
        const dropdownIcon = this.querySelector(".dropdown-icon");
        if (dropdownIcon) {
          if (dropdownMenu.classList.contains("show")) {
            dropdownIcon.style.transform = "translateY(-50%) rotate(180deg)";
          } else {
            dropdownIcon.style.transform = "translateY(-50%) rotate(0)";
          }
        }
      }
    });
  });

  // Close dropdown when clicking outside
  document.addEventListener("click", function (e) {
    dropdownToggles.forEach((toggle) => {
      const dropdownMenu = toggle.nextElementSibling;
      if (!dropdownMenu) return;
      // If the menu is open and click is outside both toggle and menu, close it
      if (
        dropdownMenu.classList.contains("show") &&
        !toggle.contains(e.target) &&
        !dropdownMenu.contains(e.target)
      ) {
        dropdownMenu.classList.remove("show");
        // Reset icon rotation if present
        const dropdownIcon = toggle.querySelector(".dropdown-icon");
        if (dropdownIcon) {
          dropdownIcon.style.transform = "translateY(-50%) rotate(0)";
        }
      }
    });
  });
}

/**
 * Show the active settings tab based on the URL parameter
 */
function showActiveTabFromUrl() {
  // Get current URL and extract the tab parameter
  const urlParams = new URLSearchParams(window.location.search);
  let activeTab = urlParams.get("tab");

  // If no tab parameter in the search params, check if it's in the path
  if (!activeTab) {
    const pathParts = window.location.pathname.split("/");
    const lastPathPart = pathParts[pathParts.length - 1];
    if (
      ["profile", "store", "security", "notifications", "appearance"].includes(
        lastPathPart
      )
    ) {
      activeTab = lastPathPart;
    }
  }

  // Default to profile if no tab is specified
  if (!activeTab) {
    activeTab = "profile";
  }

  // Hide all tabs first
  const allTabs = document.querySelectorAll(".settings-tab");
  allTabs.forEach((tab) => {
    tab.classList.remove("active");
  });

  // Show the selected tab
  const selectedTab = document.getElementById(`${activeTab}-tab`);
  if (selectedTab) {
    selectedTab.classList.add("active");
  }

  // Update page title based on active tab
  const tabTitles = {
    profile: "Profile Settings",
    store: "Store Settings",
    security: "Security Settings",
    notifications: "Notification Settings",
    appearance: "Appearance Settings",
  };

  document.title = tabTitles[activeTab] || "Settings";
}
/**
 * Initialize profile and cover photo uploads
 */
function initPhotoUploads() {
  // Profile Photo Upload in Profile tab
  setupPhotoUpload(
    "edit-profile-photo",
    "profile-photo-input",
    "profile-photo-preview",
    "profile"
  );

  // Cover Photo Upload in Profile tab
  setupPhotoUpload(
    "edit-cover-photo",
    "cover-photo-input",
    "cover-photo-preview",
    "cover"
  );

  // Store Logo (Profile Photo) Upload in Store tab
  setupPhotoUpload(
    "edit-store-photo",
    "store-photo-input",
    "store-photo-preview",
    "profile"
  );

  // Store Banner (Cover Photo) Upload in Store tab
  setupPhotoUpload(
    "edit-store-cover-photo",
    "store-cover-photo-input",
    "store-cover-photo-preview",
    "cover"
  );
}

/**
 * Helper function to set up photo upload functionality
 * @param {string} buttonId - ID of the button that triggers file selection
 * @param {string} inputId - ID of the file input element
 * @param {string} previewId - ID of the preview element
 * @param {string} type - Type of photo ('profile' or 'cover')
 */
function setupPhotoUpload(buttonId, inputId, previewId, type) {
  const photoBtn = document.getElementById(buttonId);
  const photoInput = document.getElementById(inputId);
  const photoPreview = document.getElementById(previewId);

  if (photoBtn && photoInput && photoPreview) {
    photoBtn.addEventListener("click", function () {
      photoInput.click();
    });

    photoInput.addEventListener("change", function () {
      if (this.files && this.files[0]) {
        const reader = new FileReader();
        reader.onload = function (e) {
          photoPreview.style.backgroundImage = `url('${e.target.result}')`;

          // If this is a store photo, update the corresponding profile photo preview as well
          if (previewId === "store-photo-preview") {
            const profilePhotoPreview = document.getElementById(
              "profile-photo-preview"
            );
            if (profilePhotoPreview) {
              profilePhotoPreview.style.backgroundImage = `url('${e.target.result}')`;
            }
          } else if (previewId === "store-cover-photo-preview") {
            const coverPhotoPreview = document.getElementById(
              "cover-photo-preview"
            );
            if (coverPhotoPreview) {
              coverPhotoPreview.style.backgroundImage = `url('${e.target.result}')`;
            }
          } else if (previewId === "profile-photo-preview") {
            const storePhotoPreview = document.getElementById(
              "store-photo-preview"
            );
            if (storePhotoPreview) {
              storePhotoPreview.style.backgroundImage = `url('${e.target.result}')`;
            }
          } else if (previewId === "cover-photo-preview") {
            const storeCoverPhotoPreview = document.getElementById(
              "store-cover-photo-preview"
            );
            if (storeCoverPhotoPreview) {
              storeCoverPhotoPreview.style.backgroundImage = `url('${e.target.result}')`;
            }
          }

          // Here you would normally upload the file to the server
          uploadPhoto(this.files[0], type);
        }.bind(this);
        reader.readAsDataURL(this.files[0]);
      }
    });
  }
}

/**
 * Handle photo upload to server
 * @param {File} file - The file to upload
 * @param {string} type - Either 'profile' or 'cover'
 */
function uploadPhoto(file, type) {
  // Create form data for upload
  const formData = new FormData();
  formData.append("photo", file);
  formData.append("type", type);

  // Show loading indicator
  showToast(
    `Uploading ${
      type === "profile"
        ? "profile photo/store logo"
        : "cover photo/store banner"
    }...`,
    "info"
  );

  // Send to server
  fetch("/seller/upload-photo", {
    method: "POST",
    body: formData,
    // Don't set Content-Type header, let the browser set it with the boundary parameter
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Sync photos between tabs to ensure consistency
        syncPhotoBetweenTabs(type, data.photoUrl);

        showToast(
          `${
            type === "profile"
              ? "Profile photo/Store logo"
              : "Cover photo/Store banner"
          } updated successfully!`,
          "success"
        );
      } else {
        showToast(`Failed to upload ${type} photo: ${data.message}`, "error");
      }
    })
    .catch((error) => {
      console.error("Error uploading photo:", error);
      showToast(`Error uploading ${type} photo. Please try again.`, "error");
    });
}

/**
 * Initialize form submissions
 */
function initFormSubmissions() {
  // Personal Information Form
  const personalInfoForm = document.getElementById("personal-info-form");
  if (personalInfoForm) {
    personalInfoForm.addEventListener("submit", function (e) {
      e.preventDefault();

      const formData = {
        first_name: document.getElementById("first-name").value,
        last_name: document.getElementById("last-name").value,
        email: document.getElementById("email").value,
        phone: document.getElementById("phone").value,
        city: document.getElementById("city").value,
        country: document.getElementById("country").value,
        bio: document.getElementById("bio").value,
      };

      saveSettings("personal_info", formData);
    });
  }

  // Store Information Form
  const storeInfoForm = document.getElementById("store-info-form");
  if (storeInfoForm) {
    storeInfoForm.addEventListener("submit", function (e) {
      e.preventDefault();

      const formData = {
        store_name: document.getElementById("store-name").value,
        store_description: document.getElementById("store-description").value,
        store_url: document.getElementById("store-url").value,
        business_type: document.getElementById("business-type").value,
        business_address: document.getElementById("business-address").value,
        ships_domestic: document.getElementById("shipping-domestic").checked,
        ships_international: document.getElementById("shipping-international")
          .checked,
      };

      saveSettings("store_info", formData);
    });
  }

  // Password Change Form
  const passwordChangeForm = document.getElementById("password-change-form");
  if (passwordChangeForm) {
    passwordChangeForm.addEventListener("submit", function (e) {
      e.preventDefault();

      const currentPassword = document.getElementById("current-password").value;
      const newPassword = document.getElementById("new-password").value;
      const confirmPassword = document.getElementById("confirm-password").value;

      if (newPassword !== confirmPassword) {
        showToast("New passwords do not match", "error");
        return;
      }

      const formData = {
        current_password: currentPassword,
        new_password: newPassword,
      };

      saveSettings("password", formData);
    });
  }

  // Notification Settings Form
  const notificationSettingsForm = document.getElementById(
    "notification-settings-form"
  );
  if (notificationSettingsForm) {
    notificationSettingsForm.addEventListener("submit", function (e) {
      e.preventDefault();

      const formData = {
        order_notifications: document.getElementById("order-notifications")
          .checked,
        message_notifications: document.getElementById("message-notifications")
          .checked,
        review_notifications: document.getElementById("review-notifications")
          .checked,
        inventory_notifications: document.getElementById(
          "inventory-notifications"
        ).checked,
        platform_notifications: document.getElementById(
          "platform-notifications"
        ).checked,
        sms_order_notifications: document.getElementById(
          "sms-order-notifications"
        ).checked,
        sms_critical_notifications: document.getElementById(
          "sms-critical-notifications"
        ).checked,
      };

      saveSettings("notifications", formData);
    });
  }

  // Appearance Settings Form
  const appearanceSettingsForm = document.getElementById(
    "appearance-settings-form"
  );
  if (appearanceSettingsForm) {
    appearanceSettingsForm.addEventListener("submit", function (e) {
      e.preventDefault();

      const formData = {
        theme: document.getElementById("selected-theme").value,
        accent_color: document.getElementById("accent-color").value,
        store_layout: document.getElementById("store-layout").value,
        products_per_page: document.getElementById("products-per-page").value,
        custom_css: document.getElementById("custom-css").value,
      };

      saveSettings("appearance", formData);
    });
  }
}

/**
 * Save settings to server
 * @param {string} settingType - The type of settings being saved
 * @param {Object} formData - The form data to save
 */
function saveSettings(settingType, formData) {
  // Show loading indicator
  showToast("Saving settings...", "info");

  fetch("/seller/save-settings", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      setting_type: settingType,
      data: formData,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        showToast("Settings saved successfully!", "success");
      } else {
        showToast(`Failed to save settings: ${data.message}`, "error");
      }
    })
    .catch((error) => {
      console.error("Error saving settings:", error);
      showToast("Error saving settings. Please try again.", "error");
    });
}

/**
 * Initialize password strength meter
 */
function initPasswordStrengthMeter() {
  const passwordInput = document.getElementById("new-password");
  const strengthBar = document.querySelector(".strength-bar");

  if (passwordInput && strengthBar) {
    passwordInput.addEventListener("input", function () {
      const password = this.value;
      const strength = calculatePasswordStrength(password);

      // Remove all classes
      strengthBar.classList.remove(
        "strength-weak",
        "strength-medium",
        "strength-strong",
        "strength-very-strong"
      );

      // Add appropriate class based on strength
      if (password.length === 0) {
        strengthBar.style.width = "0";
      } else if (strength < 40) {
        strengthBar.classList.add("strength-weak");
      } else if (strength < 60) {
        strengthBar.classList.add("strength-medium");
      } else if (strength < 80) {
        strengthBar.classList.add("strength-strong");
      } else {
        strengthBar.classList.add("strength-very-strong");
      }
    });
  }
}

/**
 * Calculate password strength score
 * @param {string} password - The password to evaluate
 * @returns {number} - Score from 0-100
 */
function calculatePasswordStrength(password) {
  let score = 0;

  // Length contribution (up to 30 points)
  score += Math.min(30, password.length * 3);

  // Complexity contribution
  if (/[a-z]/.test(password)) score += 10; // lowercase
  if (/[A-Z]/.test(password)) score += 15; // uppercase
  if (/[0-9]/.test(password)) score += 15; // numbers
  if (/[^a-zA-Z0-9]/.test(password)) score += 20; // special chars

  // Variety of characters (up to 10 points)
  const uniqueChars = new Set(password.split("")).size;
  score += Math.min(10, uniqueChars);

  return Math.min(100, score);
}

/**
 * Initialize two-factor authentication toggle
 */
function initTwoFactorToggle() {
  const twoFactorToggle = document.getElementById("two-factor-toggle");
  const twoFactorSetup = document.querySelector(".two-factor-setup");

  if (twoFactorToggle && twoFactorSetup) {
    twoFactorToggle.addEventListener("change", function () {
      if (this.checked) {
        // When enabling 2FA, show setup UI and request new QR code
        twoFactorSetup.classList.remove("hidden");
        generateTwoFactorQR();
      } else {
        // When disabling 2FA, confirm with user
        if (
          confirm(
            "Are you sure you want to disable two-factor authentication? This will reduce the security of your account."
          )
        ) {
          twoFactorSetup.classList.add("hidden");
          disableTwoFactor();
        } else {
          // If user cancels, revert the toggle
          this.checked = true;
        }
      }
    });
  }
}

/**
 * Generate new two-factor QR code
 */
function generateTwoFactorQR() {
  fetch("/seller/generate-2fa", {
    method: "POST",
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success && data.qr_code) {
        // Replace placeholder with actual QR code
        const qrPlaceholder = document.querySelector(".qr-code-placeholder");
        qrPlaceholder.innerHTML = `<img src="${data.qr_code}" alt="Two-Factor Authentication QR Code">`;
      } else {
        showToast("Failed to generate two-factor authentication code", "error");
      }
    })
    .catch((error) => {
      console.error("Error generating 2FA code:", error);
      showToast("Error generating two-factor authentication code", "error");
    });
}

/**
 * Disable two-factor authentication
 */
function disableTwoFactor() {
  fetch("/seller/disable-2fa", {
    method: "POST",
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        showToast("Two-factor authentication has been disabled", "success");
      } else {
        showToast("Failed to disable two-factor authentication", "error");
      }
    })
    .catch((error) => {
      console.error("Error disabling 2FA:", error);
      showToast("Error disabling two-factor authentication", "error");
    });
}

/**
 * Initialize theme selection
 */
function initThemeSelection() {
  const themeOptions = document.querySelectorAll(".theme-option");
  const selectedThemeInput = document.getElementById("selected-theme");

  if (themeOptions.length && selectedThemeInput) {
    themeOptions.forEach((option) => {
      option.addEventListener("click", function () {
        // Remove selected class from all options
        themeOptions.forEach((opt) => opt.classList.remove("selected"));

        // Add selected class to clicked option
        this.classList.add("selected");

        // Update hidden input value
        const theme = this.getAttribute("data-theme");
        selectedThemeInput.value = theme;
      });
    });
  }
}

/**
 * Initialize color picker
 */
function initColorPicker() {
  const colorPreview = document.getElementById("color-preview");
  const colorPicker = document.getElementById("color-picker");
  const accentColorInput = document.getElementById("accent-color");

  if (colorPreview && colorPicker && accentColorInput) {
    // Click on color preview opens color picker
    colorPreview.addEventListener("click", function () {
      colorPicker.click();
    });

    // Update values when color is picked
    colorPicker.addEventListener("input", function () {
      const color = this.value;
      colorPreview.style.backgroundColor = color;
      accentColorInput.value = color;
    });

    // Update values when hex input changes
    accentColorInput.addEventListener("input", function () {
      const color = this.value;
      // Only update if it's a valid hex color
      if (/^#[0-9A-F]{6}$/i.test(color)) {
        colorPreview.style.backgroundColor = color;
        colorPicker.value = color;
      }
    });
  }
}

/**
 * Show a toast notification
 * @param {string} message - Message to display
 * @param {string} type - Notification type: 'success', 'error', 'info'
 */
function showToast(message, type = "info") {
  // Check if toast container exists, create if not
  let toastContainer = document.querySelector(".toast-container");
  if (!toastContainer) {
    toastContainer = document.createElement("div");
    toastContainer.className = "toast-container";
    document.body.appendChild(toastContainer);
  }

  // Create toast element
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;

  // Add to container
  toastContainer.appendChild(toast);

  // Show the toast with animation
  setTimeout(() => {
    toast.classList.add("show");
  }, 10);

  // Remove after delay
  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => {
      toast.remove();
    }, 300); // Match the CSS transition time
  }, 3000);
}
