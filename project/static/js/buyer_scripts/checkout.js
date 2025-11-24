// Form validation and interaction handlers
document.addEventListener("DOMContentLoaded", function () {
  // Initialize form interactions
  initializeFormValidation();
  initializeDeliveryNote();
  initializeGiftMessage();

  // Auto-format phone number
  const phoneInput = document.getElementById("phone");
  if (phoneInput) {
    phoneInput.addEventListener("input", formatPhoneNumber);
  }

  // Auto-format zip code
  const zipInput = document.getElementById("zipCode");
  if (zipInput) {
    zipInput.addEventListener("input", formatZipCode);
  }
});

function initializeFormValidation() {
  const form = document.querySelector(".checkout-form");
  const inputs = form.querySelectorAll("input[required], select[required]");

  inputs.forEach((input) => {
    input.addEventListener("blur", validateField);
    input.addEventListener("input", clearFieldError);
  });
}

function validateField(event) {
  const field = event.target;
  const value = field.value.trim();

  // Remove existing error styling
  field.classList.remove("error");

  // Basic validation
  if (field.hasAttribute("required") && !value) {
    showFieldError(field, "This field is required");
    return false;
  }

  // Email validation
  if (field.type === "email" && value) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      showFieldError(field, "Please enter a valid email address");
      return false;
    }
  }

  // Phone validation
  if (field.type === "tel" && value) {
    const phoneRegex = /^$$\d{3}$$ \d{3}-\d{4}$/;
    if (!phoneRegex.test(value)) {
      showFieldError(field, "Please enter a valid phone number");
      return false;
    }
  }

  return true;
}

function showFieldError(field, message) {
  field.classList.add("error");

  // Remove existing error message
  const existingError = field.parentNode.querySelector(".error-message");
  if (existingError) {
    existingError.remove();
  }

  // Add error message
  const errorDiv = document.createElement("div");
  errorDiv.className = "error-message";
  errorDiv.textContent = message;
  field.parentNode.appendChild(errorDiv);
}

function clearFieldError(event) {
  const field = event.target;
  field.classList.remove("error");

  const errorMessage = field.parentNode.querySelector(".error-message");
  if (errorMessage) {
    errorMessage.remove();
  }
}

function formatPhoneNumber(event) {
  let value = event.target.value.replace(/\D/g, "");

  if (value.length >= 6) {
    value = `(${value.slice(0, 3)}) ${value.slice(3, 6)}-${value.slice(6, 10)}`;
  } else if (value.length >= 3) {
    value = `(${value.slice(0, 3)}) ${value.slice(3)}`;
  }

  event.target.value = value;
}

function formatZipCode(event) {
  let value = event.target.value.replace(/\D/g, "");

  if (value.length > 5) {
    value = `${value.slice(0, 5)}-${value.slice(5, 9)}`;
  }

  event.target.value = value;
}

function initializeDeliveryNote() {
  const addNoteLink = document.querySelector(".add-note-link");

  if (addNoteLink) {
    addNoteLink.addEventListener("click", function (e) {
      e.preventDefault();
      showDeliveryNoteField();
    });
  }
}

function showDeliveryNoteField() {
  const deliveryNoteDiv = document.querySelector(".delivery-note");

  // Check if field already exists
  if (deliveryNoteDiv.querySelector("textarea")) {
    return;
  }

  const textarea = document.createElement("textarea");
  textarea.id = "deliveryNote";
  textarea.placeholder =
    "Add delivery instructions (e.g., company name, gate code, etc.)";
  textarea.rows = 3;
  textarea.style.cssText = `
        width: 100%;
        padding: 12px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
        margin-top: 8px;
        resize: vertical;
        font-family: inherit;
    `;

  deliveryNoteDiv.appendChild(textarea);
  textarea.focus();
}

function initializeGiftMessage() {
  const giftCheckboxes = document.querySelectorAll(
    "#giftMessage, #giftMessageMobile"
  );

  giftCheckboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", function () {
      if (this.checked) {
        showGiftMessageField(this);
      } else {
        hideGiftMessageField(this);
      }

      // Sync both checkboxes
      giftCheckboxes.forEach((cb) => {
        if (cb !== this) {
          cb.checked = this.checked;
        }
      });
    });
  });
}

function showGiftMessageField(checkbox) {
  const container = checkbox.closest(".form-section, .mobile-shipping-section");

  // Check if field already exists
  if (container.querySelector(".gift-message-field")) {
    return;
  }

  const fieldDiv = document.createElement("div");
  fieldDiv.className = "gift-message-field";
  fieldDiv.style.marginTop = "16px";

  const label = document.createElement("label");
  label.textContent = "Gift message";
  label.style.cssText = `
        display: block;
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 6px;
        color: #333;
    `;

  const textarea = document.createElement("textarea");
  textarea.placeholder = "Enter your gift message here...";
  textarea.rows = 3;
  textarea.style.cssText = `
        width: 100%;
        padding: 12px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
        resize: vertical;
        font-family: inherit;
    `;

  fieldDiv.appendChild(label);
  fieldDiv.appendChild(textarea);

  const checkboxGroup = checkbox.closest(".checkbox-group");
  checkboxGroup.parentNode.insertBefore(fieldDiv, checkboxGroup.nextSibling);
}

function hideGiftMessageField(checkbox) {
  const container = checkbox.closest(".form-section, .mobile-shipping-section");
  const giftField = container.querySelector(".gift-message-field");

  if (giftField) {
    giftField.remove();
  }
}

function proceedToNextStep() {
  // Validate all required fields
  const requiredFields = document.querySelectorAll(
    "input[required], select[required]"
  );
  let isValid = true;

  requiredFields.forEach((field) => {
    if (!validateField({ target: field })) {
      isValid = false;
    }
  });

  // Check email field specifically
  const emailField = document.getElementById("email");
  if (!validateField({ target: emailField })) {
    isValid = false;
  }

  if (!isValid) {
    // Scroll to first error
    const firstError = document.querySelector(".error");
    if (firstError) {
      firstError.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    showNotification("Please fill in all required fields correctly.", "error");
    return;
  }

  // Show loading state
  const button = document.querySelector(".next-step-btn");
  const originalText = button.textContent;
  button.textContent = "PROCESSING...";
  button.disabled = true;

  // Collect form data
  const formData = {
    email: document.getElementById("email").value,
    firstName: document.getElementById("firstName").value,
    lastName: document.getElementById("lastName").value,
    address: document.getElementById("address").value,
    apartment: document.getElementById("apartment").value,
    city: document.getElementById("city").value,
    state: document.getElementById("state").value,
    zipCode: document.getElementById("zipCode").value,
    phone: document.getElementById("phone").value,
    country: document.getElementById("country").value,
  };

  // Simulate processing and redirect to payment page
  setTimeout(() => {
    showNotification("Proceeding to payment...", "success");

    // Redirect to payment page after a short delay
    setTimeout(() => {
      window.location.href = "/payment";
    }, 1000);
  }, 1500);
}

function showNotification(message, type = "info") {
  // Remove existing notifications
  const existingNotification = document.querySelector(".notification");
  if (existingNotification) {
    existingNotification.remove();
  }

  const notification = document.createElement("div");
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
    `;

  // Set background color based on type
  switch (type) {
    case "success":
      notification.style.backgroundColor = "#28a745";
      break;
    case "error":
      notification.style.backgroundColor = "#dc3545";
      break;
    default:
      notification.style.backgroundColor = "#007bff";
  }

  document.body.appendChild(notification);

  // Auto-remove after 4 seconds
  setTimeout(() => {
    if (notification.parentNode) {
      notification.style.animation = "slideOut 0.3s ease-in";
      setTimeout(() => {
        if (notification.parentNode) {
          notification.remove();
        }
      }, 300);
    }
  }, 4000);
}

// Add CSS animations
const style = document.createElement("style");
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .error {
        border-color: #dc3545 !important;
        box-shadow: 0 0 0 2px rgba(220, 53, 69, 0.25) !important;
    }
    
    .error-message {
        color: #dc3545;
        font-size: 12px;
        margin-top: 4px;
    }
`;
document.head.appendChild(style);
