// Form validation and interaction handlers
document.addEventListener("DOMContentLoaded", function () {
  // Initialize Cash on Delivery as default payment method
  const codRadio = document.getElementById("payment-cod");
  if (codRadio) {
    codRadio.checked = true;
    console.log("✓ Cash on Delivery set as default payment method");
  }

  // Initialize form interactions
  initializeFormValidation();
  initializeDeliveryNote();
  initializeGiftMessage();
  initializePaymentMethods();

  // Load Philippines address data for dropdowns
  loadPhilippinesAddressData();

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

  // Auto-format card number
  const cardNumberInput = document.getElementById("card-number");
  if (cardNumberInput) {
    cardNumberInput.addEventListener("input", formatCardNumber);
  }

  // Auto-format expiry date
  const expiryInput = document.getElementById("expiry");
  if (expiryInput) {
    expiryInput.addEventListener("input", formatExpiry);
  }

  // Auto-format GCash number
  const gcashNumberInput = document.getElementById("gcash-number");
  if (gcashNumberInput) {
    gcashNumberInput.addEventListener("input", formatGCashNumber);
  }

  // Add event listeners for buttons with data-action attributes
  document.addEventListener("click", function (event) {
    const action = event.target.getAttribute("data-action");
    if (action) {
      event.preventDefault();
      switch (action) {
        case "openAddressModal":
          openAddressModal();
          break;
        case "closeAddressModal":
          closeAddressModal();
          break;
        case "completeOrder":
          completeOrder();
          break;
      }
    }
  });
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
  // This function is deprecated - use completeOrder() instead
  completeOrder();
}

async function completeOrder() {
  console.log("completeOrder function called");

  // Find the complete order button
  const button = document.querySelector("[data-action='completeOrder']");
  if (!button) {
    console.error("Complete order button not found");
    return;
  }

  // Prevent duplicate submissions when multiple listeners fire
  if (button.dataset.processing === "true") {
    console.warn(
      "Order submission already in progress, ignoring duplicate click"
    );
    return;
  }

  // First check if shipping address exists
  const addressField = document.getElementById("address");
  const cityField = document.getElementById("city");
  const phoneField = document.getElementById("phone");

  if (
    !addressField ||
    !cityField ||
    !phoneField ||
    !addressField.value.trim() ||
    !cityField.value.trim() ||
    !phoneField.value.trim()
  ) {
    showNotification("Please add your shipping address first.", "error");
    return;
  }

  // Validate all required fields that are visible (not in hidden modals)
  const allRequiredFields = document.querySelectorAll(
    "input[required], select[required]"
  );

  // Filter out modal fields that are hidden
  const visibleRequiredFields = Array.from(allRequiredFields).filter(
    (field) => {
      // Skip fields inside hidden modals
      const modal = field.closest(".modal");
      if (modal && modal.style.display === "none") {
        return false;
      }

      // Include hidden form fields that are required for submission
      if (
        field.type === "hidden" ||
        (field.style.display === "none" &&
          field.parentElement.style.display === "none")
      ) {
        return true; // Include hidden form fields
      }

      // Check if any parent is hidden (except the hidden form container)
      let parent = field.parentElement;
      while (parent && parent !== document.body) {
        if (
          parent.style.display === "none" &&
          !parent.querySelector('input[type="hidden"]')
        ) {
          return false;
        }
        parent = parent.parentElement;
      }

      return true;
    }
  );

  let isValid = true;

  visibleRequiredFields.forEach((field) => {
    if (!validateField({ target: field })) {
      isValid = false;
    }
  });

  // Check email field specifically
  const emailField = document.getElementById("email");
  if (!validateField({ target: emailField })) {
    isValid = false;
  }

  // Validate payment method selection
  const selectedPaymentMethod = document.querySelector(
    'input[name="payment-method"]:checked'
  );
  if (!selectedPaymentMethod) {
    showNotification("Please select a payment method.", "error");
    return;
  }

  // Validate payment method specific fields
  if (selectedPaymentMethod.value === "credit-card") {
    const cardNumber = document.getElementById("card-number").value.trim();
    const expiry = document.getElementById("expiry").value.trim();
    const cvc = document.getElementById("security-code").value.trim();
    const cardholderName = document
      .getElementById("cardholder-name")
      .value.trim();

    if (!cardNumber || !expiry || !cvc || !cardholderName) {
      showNotification("Please fill in all card details.", "error");
      return;
    }
  } else if (selectedPaymentMethod.value === "gcash") {
    const gcashNumber = document.getElementById("gcash-number").value.trim();
    if (!gcashNumber) {
      showNotification("Please enter your GCash mobile number.", "error");
      return;
    }
  }

  // Validate terms and conditions checkbox
  const termsCheckbox = document.getElementById("terms");
  if (termsCheckbox && !termsCheckbox.checked) {
    showNotification("Please agree to the Terms and Conditions.", "error");
    return;
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
  const originalText = button.textContent;
  button.textContent = "PROCESSING ORDER...";
  button.disabled = true;
  button.dataset.processing = "true";

  // Collect form data including payment information
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
    region: document.getElementById("region")
      ? document.getElementById("region").value
      : "",
    barangay: document.getElementById("barangay")
      ? document.getElementById("barangay").value
      : "",
    paymentMethod: selectedPaymentMethod.value,
  };

  // Auto-save address before processing order
  try {
    await saveAddressAutomatically(formData);
  } catch (error) {
    console.warn("Address auto-save failed:", error);
    // Continue with order processing even if address save fails
  }

  // Add payment method specific data
  if (selectedPaymentMethod.value === "credit-card") {
    formData.cardNumber = document.getElementById("card-number").value;
    formData.expiry = document.getElementById("expiry").value;
    formData.cvc = document.getElementById("security-code").value;
    formData.cardholderName = document.getElementById("cardholder-name").value;
  } else if (selectedPaymentMethod.value === "gcash") {
    formData.gcashNumber = document.getElementById("gcash-number").value;
  }

  // Process order directly
  processOrder(formData)
    .then((result) => {
      showNotification("Order placed successfully!", "success");
      // Redirect to order confirmation page
      setTimeout(() => {
        window.location.href = "/order-success";
      }, 1000);
    })
    .catch((error) => {
      console.error("Order processing failed:", error);
      showNotification("Failed to process order. Please try again.", "error");
      button.textContent = originalText;
      button.disabled = false;
      button.dataset.processing = "false";
    });
}

// Auto-save address function
async function saveAddressAutomatically(formData) {
  try {
    const addressData = {
      firstName: formData.firstName,
      lastName: formData.lastName,
      address: formData.address,
      apartment: formData.apartment,
      city: formData.city,
      state: formData.state,
      zipCode: formData.zipCode,
      phone: formData.phone,
      country: formData.country,
      region: formData.region,
      barangay: formData.barangay,
    };

    await fetch("/update-address", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(addressData),
    });
  } catch (error) {
    console.error("Auto-save address error:", error);
    throw error;
  }
}

async function processOrder(formData) {
  try {
    const response = await fetch("/place-order", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.error || "Order processing failed");
    }

    return result;
  } catch (error) {
    console.error("Error processing order:", error);
    throw error;
  }
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

// Payment method handling
function initializePaymentMethods() {
  const paymentMethods = document.querySelectorAll(
    'input[name="payment-method"]'
  );

  paymentMethods.forEach((method) => {
    method.addEventListener("change", function () {
      handlePaymentMethodChange(this.value);
    });
  });

  // Initialize with default selection
  const defaultMethod = document.querySelector(
    'input[name="payment-method"]:checked'
  );
  if (defaultMethod) {
    handlePaymentMethodChange(defaultMethod.value);
  }
}

function handlePaymentMethodChange(selectedMethod) {
  // Hide all method content
  const allMethodContent = document.querySelectorAll(".method-content");
  allMethodContent.forEach((content) => {
    content.style.display = "none";
  });

  // Remove active class from all payment methods
  const allMethods = document.querySelectorAll(".payment-method");
  allMethods.forEach((method) => {
    method.classList.remove("active");
  });

  // Show selected method content and add active class
  const selectedMethodElement = document.querySelector(
    `[data-method="${selectedMethod}"]`
  );
  if (selectedMethodElement) {
    selectedMethodElement.classList.add("active");

    const content = selectedMethodElement.querySelector(".method-content");
    if (content) {
      content.style.display = "block";
    }
  }
}

function formatCardNumber(event) {
  let value = event.target.value.replace(/\s/g, "").replace(/[^0-9]/gi, "");
  let formattedValue = value.match(/.{1,4}/g)?.join(" ") || value;
  event.target.value = formattedValue;
}

function formatExpiry(event) {
  let value = event.target.value.replace(/\D/g, "");

  if (value.length >= 2) {
    value = value.substring(0, 2) + "/" + value.substring(2, 4);
  }

  event.target.value = value;
}

function formatGCashNumber(event) {
  let value = event.target.value.replace(/\D/g, "");

  // Format as 09XX XXX XXXX
  if (value.length > 0) {
    if (value.length <= 4) {
      value = value;
    } else if (value.length <= 7) {
      value = value.substring(0, 4) + " " + value.substring(4);
    } else {
      value =
        value.substring(0, 4) +
        " " +
        value.substring(4, 7) +
        " " +
        value.substring(7, 11);
    }
  }

  event.target.value = value;
}

// Address Modal Functions
async function openAddressModal() {
  console.log("openAddressModal function called");

  const modal = document.getElementById("addressModal");
  if (!modal) {
    console.error("Address modal not found");
    return;
  }

  // Pre-fill text inputs with existing data
  const textInputs = {
    "modal-firstName": document.getElementById("firstName").value,
    "modal-lastName": document.getElementById("lastName").value,
    "modal-address": document.getElementById("address").value,
    "modal-apartment": document.getElementById("apartment").value,
    "modal-zipCode": document.getElementById("zipCode").value,
    "modal-phone": document.getElementById("phone").value,
    "modal-country": document.getElementById("country").value,
  };

  // Pre-fill text inputs
  Object.keys(textInputs).forEach((id) => {
    const input = document.getElementById(id);
    if (input) {
      input.value = textInputs[id] || "";
    }
  });

  const regionValue = document.getElementById("region").value;
  const stateValue = document.getElementById("state").value;
  const cityValue = document.getElementById("city").value;
  const barangayValue = document.getElementById("barangay").value;

  await loadPhilippinesAddressData();

  const regionSelect = document.getElementById("modal-region");
  const stateSelect = document.getElementById("modal-state");
  const citySelect = document.getElementById("modal-city");
  const barangaySelect = document.getElementById("modal-barangay");

  if (regionValue && selectOptionByValue(regionSelect, regionValue)) {
    await populateProvinces(true);
    if (stateValue && selectOptionByValue(stateSelect, stateValue)) {
      await populateCities(true);
      if (cityValue && selectOptionByValue(citySelect, cityValue)) {
        await populateBarangays(true);
        if (barangayValue) {
          selectOptionByValue(barangaySelect, barangayValue);
        }
      }
    }
  }

  // Clear any previous autofill indicators
  clearAutofillIndicators();
  clearAddressErrors();

  modal.style.display = "flex";
}

function closeAddressModal() {
  const modal = document.getElementById("addressModal");
  modal.style.display = "none";
}

function selectOptionByValue(select, value) {
  if (!select || !value) return false;
  const normalized = value.trim().toLowerCase();
  for (let i = 0; i < select.options.length; i++) {
    if (select.options[i].value.trim().toLowerCase() === normalized) {
      select.selectedIndex = i;
      return true;
    }
  }
  return false;
}

function saveAddress() {
  const modalForm = document.getElementById("addressForm");
  const formData = new FormData(modalForm);

  // Get values from dropdowns
  const regionSelect = document.getElementById("modal-region");
  const stateSelect = document.getElementById("modal-state");
  const citySelect = document.getElementById("modal-city");
  const barangaySelect = document.getElementById("modal-barangay");

  // Validate required fields including new region and barangay
  const requiredFields = [
    { name: "firstName", element: document.getElementById("modal-firstName") },
    { name: "lastName", element: document.getElementById("modal-lastName") },
    { name: "address", element: document.getElementById("modal-address") },
    { name: "region", element: regionSelect },
    { name: "state", element: stateSelect },
    { name: "city", element: citySelect },
    { name: "barangay", element: barangaySelect },
    { name: "zipCode", element: document.getElementById("modal-zipCode") },
    { name: "phone", element: document.getElementById("modal-phone") },
    { name: "country", element: document.getElementById("modal-country") },
  ];

  let isValid = true;

  requiredFields.forEach((field) => {
    const value = field.element.value?.trim();
    if (!value) {
      isValid = false;
      if (field.element) {
        field.element.style.borderColor = "#dc3545";
      }
    } else {
      if (field.element) {
        field.element.style.borderColor = "";
      }
    }
  });

  if (!isValid) {
    showNotification("Please fill in all required fields", "error");
    return;
  }

  // Prepare comprehensive data for backend
  const addressData = {
    firstName: formData.get("firstName"),
    lastName: formData.get("lastName"),
    address: formData.get("address"),
    apartment: formData.get("apartment"),
    region: regionSelect.value,
    state: stateSelect.value,
    city: citySelect.value,
    barangay: barangaySelect.value,
    zipCode: formData.get("zipCode"),
    phone: formData.get("phone"),
    country: formData.get("country"),
  };

  // Update hidden form fields
  Object.keys(addressData).forEach((key) => {
    const input = document.getElementById(key);
    if (input) {
      input.value = addressData[key] || "";
    }
  });

  // Update address display with comprehensive data
  updateAddressDisplay(addressData);

  // Save to backend
  saveAddressToBackend(addressData);

  closeAddressModal();
}

async function saveAddressToBackend(addressData) {
  try {
    const response = await fetch("/update-address", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(addressData),
    });

    if (response.ok) {
      showNotification("Address updated successfully", "success");
    } else {
      showNotification("Failed to save address", "error");
    }
  } catch (error) {
    console.error("Error saving address:", error);
    showNotification("Error saving address", "error");
  }
}

function updateAddressDisplay(addressData) {
  const addressDisplay = document.getElementById("shipping-address-display");

  const hierarchy = [
    addressData.region,
    addressData.state,
    addressData.city,
    addressData.barangay,
  ].filter(Boolean);

  const addressHTML = `
    <div class="address-details">
      <div class="address-name">${addressData.firstName} ${
    addressData.lastName
  }</div>
      <div class="address-line">${addressData.address}</div>
      ${
        addressData.apartment
          ? `<div class="address-line">${addressData.apartment}</div>`
          : ""
      }
      ${
        hierarchy.length
          ? `<div class="address-line">${hierarchy.join(", ")}</div>`
          : ""
      }
      <div class="address-line">${addressData.country} ${
    addressData.zipCode
  }</div>
      <div class="address-phone">${addressData.phone}</div>
    </div>
  `;

  addressDisplay.innerHTML = addressHTML;
}

// Philippines Address Data Management
let regionsData = [];
const provinceCache = new Map();
const cityCache = new Map();
const barangayCache = new Map();
let regionsLoadPromise = null;

async function loadPhilippinesAddressData() {
  if (regionsLoadPromise) {
    await regionsLoadPromise;
    populateRegions();
    return;
  }

  regionsLoadPromise = (async () => {
    try {
      const response = await fetch("https://psgc.gitlab.io/api/regions/");
      if (!response.ok) throw new Error("Failed to load regions");
      regionsData = await response.json();
    } catch (error) {
      console.error("Error loading Philippines address data:", error);
      showNotification("Unable to load PH regions. Please retry.", "error");
    }
  })();

  await regionsLoadPromise;
  populateRegions();
}

function populateRegions() {
  const regionSelect = document.getElementById("modal-region");
  if (!regionSelect || !regionsData.length) return;

  regionSelect.innerHTML = '<option value="">Select Region</option>';

  [...regionsData]
    .sort((a, b) => a.name.localeCompare(b.name))
    .forEach((region) => {
      const option = document.createElement("option");
      option.value = region.name;
      option.textContent = region.name;
      option.dataset.regionCode = region.code;
      regionSelect.appendChild(option);
    });
}

async function populateProvinces() {
  const regionSelect = document.getElementById("modal-region");
  const provinceSelect = document.getElementById("modal-state");
  const citySelect = document.getElementById("modal-city");
  const barangaySelect = document.getElementById("modal-barangay");

  if (!regionSelect || !provinceSelect) return;

  provinceSelect.innerHTML = '<option value="">Select Province</option>';
  if (citySelect)
    citySelect.innerHTML = '<option value="">Select City/Municipality</option>';
  if (barangaySelect)
    barangaySelect.innerHTML = '<option value="">Select Barangay</option>';

  const selectedOption = regionSelect.options[regionSelect.selectedIndex];
  if (!selectedOption || !selectedOption.dataset.regionCode) return;

  const regionCode = selectedOption.dataset.regionCode;
  try {
    let provinces = provinceCache.get(regionCode);
    if (!provinces) {
      const response = await fetch(
        `https://psgc.gitlab.io/api/regions/${regionCode}/provinces/`
      );
      if (!response.ok) throw new Error("Failed to load provinces");
      provinces = await response.json();
      provinceCache.set(regionCode, provinces);
    }

    provinces
      .slice()
      .sort((a, b) => a.name.localeCompare(b.name))
      .forEach((province) => {
        const option = document.createElement("option");
        option.value = province.name;
        option.textContent = province.name;
        option.dataset.provinceCode = province.code;
        provinceSelect.appendChild(option);
      });
  } catch (error) {
    console.error("Error loading provinces:", error);
    showNotification("Unable to load provinces. Please retry.", "error");
  }
}

async function populateCities() {
  const provinceSelect = document.getElementById("modal-state");
  const citySelect = document.getElementById("modal-city");
  const barangaySelect = document.getElementById("modal-barangay");

  if (!provinceSelect || !citySelect) return;

  citySelect.innerHTML = '<option value="">Select City/Municipality</option>';
  if (barangaySelect)
    barangaySelect.innerHTML = '<option value="">Select Barangay</option>';

  const selectedProvinceOption =
    provinceSelect.options[provinceSelect.selectedIndex];
  if (!selectedProvinceOption || !selectedProvinceOption.dataset.provinceCode)
    return;

  const provinceCode = selectedProvinceOption.dataset.provinceCode;
  try {
    let cities = cityCache.get(provinceCode);
    if (!cities) {
      const response = await fetch(
        `https://psgc.gitlab.io/api/provinces/${provinceCode}/cities-municipalities/`
      );
      if (!response.ok) throw new Error("Failed to load cities/municipalities");
      cities = await response.json();
      cityCache.set(provinceCode, cities);
    }

    cities
      .slice()
      .sort((a, b) => a.name.localeCompare(b.name))
      .forEach((city) => {
        const option = document.createElement("option");
        option.value = city.name;
        option.textContent = city.name;
        option.dataset.cityCode = city.code;
        citySelect.appendChild(option);
      });
  } catch (error) {
    console.error("Error loading cities:", error);
    showNotification("Unable to load cities. Please retry.", "error");
  }
}

async function populateBarangays() {
  const citySelect = document.getElementById("modal-city");
  const barangaySelect = document.getElementById("modal-barangay");

  if (!citySelect || !barangaySelect) return;

  barangaySelect.innerHTML = '<option value="">Select Barangay</option>';

  const selectedCityOption = citySelect.options[citySelect.selectedIndex];
  if (!selectedCityOption || !selectedCityOption.dataset.cityCode) return;

  const cityCode = selectedCityOption.dataset.cityCode;
  try {
    let barangays = barangayCache.get(cityCode);
    if (!barangays) {
      const response = await fetch(
        `https://psgc.gitlab.io/api/cities-municipalities/${cityCode}/barangays/`
      );
      if (!response.ok) throw new Error("Failed to load barangays");
      barangays = await response.json();
      barangayCache.set(cityCode, barangays);
    }

    barangays
      .slice()
      .sort((a, b) => a.name.localeCompare(b.name))
      .forEach((barangay) => {
        const option = document.createElement("option");
        option.value = barangay.name;
        option.textContent = barangay.name;
        barangaySelect.appendChild(option);
      });
  } catch (error) {
    console.error("Error loading barangays:", error);
    showNotification("Unable to load barangays. Please retry.", "error");
  }
}

// Philippines Address API Functions
let zipLookupTimeout;

async function handleZipCodeChange(input) {
  const zipCode = input.value.trim();
  const countrySelect = document.getElementById("modal-country");

  // Clear any existing timeout
  clearTimeout(zipLookupTimeout);

  // Only lookup for Philippines ZIP codes
  if (countrySelect.value !== "Philippines" || zipCode.length < 4) {
    clearAutofillIndicators();
    return;
  }

  // Debounce the API call
  zipLookupTimeout = setTimeout(() => {
    lookupPhilippinesAddress(zipCode);
  }, 500);
}

async function lookupPhilippinesAddress(zipCode) {
  const loadingIndicator = document.getElementById("zip-loading");
  const regionSelect = document.getElementById("modal-region");
  const stateSelect = document.getElementById("modal-state");
  const citySelect = document.getElementById("modal-city");
  const barangaySelect = document.getElementById("modal-barangay");

  try {
    // Show loading indicator
    loadingIndicator.style.display = "flex";

    // Philippines ZIP code lookup with comprehensive address data
    const addressData = await getPhilippinesAddressData(zipCode);

    if (addressData) {
      // Auto-fill all address dropdowns
      if (addressData.region) {
        // Find and select region
        for (let i = 0; i < regionSelect.options.length; i++) {
          if (regionSelect.options[i].value === addressData.region) {
            regionSelect.selectedIndex = i;
            regionSelect.classList.add("autofilled");
            document.getElementById("region-autofill").style.display = "block";
            break;
          }
        }
        // Populate provinces after region selection
        populateProvinces();
      }

      if (addressData.province) {
        // Wait a bit for provinces to populate
        setTimeout(() => {
          for (let i = 0; i < stateSelect.options.length; i++) {
            if (stateSelect.options[i].value === addressData.province) {
              stateSelect.selectedIndex = i;
              stateSelect.classList.add("autofilled");
              document.getElementById("state-autofill").style.display = "block";
              break;
            }
          }
          // Populate cities after province selection
          populateCities();

          // Auto-select city and barangay
          if (addressData.city) {
            setTimeout(() => {
              for (let i = 0; i < citySelect.options.length; i++) {
                if (citySelect.options[i].value === addressData.city) {
                  citySelect.selectedIndex = i;
                  citySelect.classList.add("autofilled");
                  document.getElementById("city-autofill").style.display =
                    "block";
                  break;
                }
              }
              // Populate barangays after city selection
              populateBarangays();

              // Auto-select barangay
              if (addressData.barangay) {
                setTimeout(() => {
                  for (let i = 0; i < barangaySelect.options.length; i++) {
                    if (
                      barangaySelect.options[i].value === addressData.barangay
                    ) {
                      barangaySelect.selectedIndex = i;
                      barangaySelect.classList.add("autofilled");
                      document.getElementById(
                        "barangay-autofill"
                      ).style.display = "block";
                      break;
                    }
                  }
                }, 100);
              }
            }, 100);
          }
        }, 100);
      }

      // Remove any error messages
      clearAddressErrors();

      showNotification(`Complete address found for ZIP ${zipCode}`, "success");
    } else {
      // ZIP code not found
      clearAutofillIndicators();
      showAddressError(
        "ZIP code not found. Please select address details manually."
      );
    }
  } catch (error) {
    console.error("Error looking up address:", error);
    clearAutofillIndicators();
    showAddressError("Unable to lookup address. Please select manually.");
  } finally {
    // Hide loading indicator
    loadingIndicator.style.display = "none";
  }
}
async function getPhilippinesAddressData(zipCode) {
  try {
    const response = await fetch(`/lookup-address/${zipCode}`);
    const result = await response.json();

    if (result.success) {
      return result.data;
    } else {
      return null;
    }
  } catch (error) {
    console.error("Error fetching address data:", error);
    return null;
  }
}

function handleCountryChange(select) {
  if (select.value !== "Philippines") {
    clearAutofillIndicators();
    clearAddressErrors();
  }
}

function clearAutofillIndicators() {
  const regionSelect = document.getElementById("modal-region");
  const stateSelect = document.getElementById("modal-state");
  const citySelect = document.getElementById("modal-city");
  const barangaySelect = document.getElementById("modal-barangay");

  if (regionSelect) regionSelect.classList.remove("autofilled");
  if (stateSelect) stateSelect.classList.remove("autofilled");
  if (citySelect) citySelect.classList.remove("autofilled");
  if (barangaySelect) barangaySelect.classList.remove("autofilled");

  const regionAutofill = document.getElementById("region-autofill");
  const stateAutofill = document.getElementById("state-autofill");
  const cityAutofill = document.getElementById("city-autofill");
  const barangayAutofill = document.getElementById("barangay-autofill");

  if (regionAutofill) regionAutofill.style.display = "none";
  if (stateAutofill) stateAutofill.style.display = "none";
  if (cityAutofill) cityAutofill.style.display = "none";
  if (barangayAutofill) barangayAutofill.style.display = "none";
}

function clearAddressErrors() {
  const existingError = document.querySelector(".address-lookup-error");
  if (existingError) {
    existingError.remove();
  }
}

function showAddressError(message) {
  clearAddressErrors();

  const zipContainer = document.querySelector(".zip-input-container");
  if (zipContainer) {
    const errorElement = document.createElement("small");
    errorElement.className = "address-lookup-error";
    errorElement.textContent = message;
    zipContainer.appendChild(errorElement);
  }
}

// Debug: Verify functions are available globally
console.log("Checkout.js loaded - Functions available:");
console.log("completeOrder:", typeof completeOrder);
console.log("openAddressModal:", typeof openAddressModal);
console.log("closeAddressModal:", typeof closeAddressModal);

// Test button detection and add direct event listeners as backup
document.addEventListener("DOMContentLoaded", function () {
  const editBtn = document.querySelector("[data-action='openAddressModal']");
  const completeBtn = document.querySelector("[data-action='completeOrder']");
  console.log("Edit address button found:", editBtn ? "YES" : "NO");
  console.log("Complete order button found:", completeBtn ? "YES" : "NO");

  // Add direct event listeners as backup
  if (editBtn) {
    editBtn.addEventListener("click", function (e) {
      e.preventDefault();
      console.log("Edit button clicked via direct listener");
      try {
        openAddressModal();
      } catch (error) {
        console.error("Error calling openAddressModal:", error);
      }
    });
    console.log("✓ Direct event listener added to edit button");
  }

  if (completeBtn) {
    completeBtn.addEventListener("click", function (e) {
      e.preventDefault();
      console.log("Complete order button clicked via direct listener");
      try {
        completeOrder();
      } catch (error) {
        console.error("Error calling completeOrder:", error);
      }
    });
    console.log("✓ Direct event listener added to complete order button");
  }
});

// Make functions explicitly global (in case of module scope issues)
window.completeOrder = completeOrder;
window.openAddressModal = openAddressModal;
window.closeAddressModal = closeAddressModal;

console.log("=== Checkout.js initialization complete ===");
