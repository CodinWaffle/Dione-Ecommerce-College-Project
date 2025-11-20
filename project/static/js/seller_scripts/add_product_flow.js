/**
 * Multi-step Product Form Flow Manager
 * Handles navigation between add product steps and data persistence
 */

(function () {
  "use strict";

  // Form data storage key
  const STORAGE_KEY = "product_form_data";

  // Get current step from progress bar or default to 1
  function getCurrentStep() {
    const stepEl = document.querySelector("[data-current-step]");
    return stepEl ? parseInt(stepEl.dataset.currentStep) : 1;
  }

  // Save form data to sessionStorage
  function saveFormData(formId) {
    const form = document.getElementById(formId);
    if (!form) return;

    const formData = new FormData(form);
    const data = {};

    // Convert FormData to object
    for (let [key, value] of formData.entries()) {
      if (data[key]) {
        // Handle multiple values (e.g., checkboxes)
        if (Array.isArray(data[key])) {
          data[key].push(value);
        } else {
          data[key] = [data[key], value];
        }
      } else {
        data[key] = value;
      }
    }

    // Get existing data
    let allData = {};
    try {
      allData = JSON.parse(sessionStorage.getItem(STORAGE_KEY) || "{}");
    } catch (e) {
      console.warn("Could not parse existing form data");
    }

    // Merge with existing data
    Object.assign(allData, data);

    // Save to sessionStorage
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(allData));
    console.log("Form data saved:", allData);
  }

  // Load form data from sessionStorage
  function loadFormData(formId) {
    const form = document.getElementById(formId);
    if (!form) return;

    try {
      const allData = JSON.parse(sessionStorage.getItem(STORAGE_KEY) || "{}");

      // Populate form fields
      for (let [key, value] of Object.entries(allData)) {
        const input = form.querySelector(`[name="${key}"]`);
        if (input) {
          if (input.type === "checkbox" || input.type === "radio") {
            if (Array.isArray(value)) {
              input.checked = value.includes(input.value);
            } else {
              input.checked = input.value === value;
            }
          } else {
            input.value = value;
          }
        }
      }

      console.log("Form data loaded");
    } catch (e) {
      console.warn("Could not load form data:", e);
    }
  }

  // Clear form data from sessionStorage
  function clearFormData() {
    sessionStorage.removeItem(STORAGE_KEY);
    console.log("Form data cleared");
  }

  // Handle Back button
  function handleBack() {
    const step = getCurrentStep();
    const routes = {
      2: "/seller/add_product",
      3: "/seller/add_product_description",
      4: "/seller/add_product_stocks",
    };

    if (routes[step]) {
      window.location.href = routes[step];
    }
  }

  // Handle Next button
  function handleNext(formId) {
    const step = getCurrentStep();
    const form = document.getElementById(formId);

    console.log("[Product Flow] Navigating from step:", step);

    // Skip validation for now - just save and navigate
    // TODO: Add proper validation later

    // Save current form data
    if (form) {
      saveFormData(formId);
    }

    // Navigate to next step
    const routes = {
      1: "/seller/add_product_description",
      2: "/seller/add_product_stocks",
      3: "/seller/add_product_preview",
    };

    const nextRoute = routes[step];
    console.log("[Product Flow] Navigating to:", nextRoute);

    if (nextRoute) {
      window.location.href = nextRoute;
    } else {
      console.error("[Product Flow] No route found for step:", step);
    }
  }

  // Handle form submission
  function handleSubmit(event, formId) {
    event.preventDefault();

    const form = document.getElementById(formId);
    if (!form) return;

    // Validate form
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }

    // Save current form data
    saveFormData(formId);

    // Get all form data
    const allData = JSON.parse(sessionStorage.getItem(STORAGE_KEY) || "{}");

    // Create a hidden form to submit all data
    const submitForm = document.createElement("form");
    submitForm.method = "POST";
    submitForm.action = window.location.pathname;

    // Add all data as hidden fields
    for (let [key, value] of Object.entries(allData)) {
      const input = document.createElement("input");
      input.type = "hidden";
      input.name = key;
      input.value = Array.isArray(value) ? value.join(",") : value;
      submitForm.appendChild(input);
    }

    document.body.appendChild(submitForm);
    submitForm.submit();
  }

  // Initialize on page load
  document.addEventListener("DOMContentLoaded", function () {
    console.log("[Product Flow] Initializing step:", getCurrentStep());

    // Determine form ID based on current step
    const step = getCurrentStep();
    const formIds = {
      1: "productForm",
      2: "productDescriptionForm",
      3: "productStocksForm",
      4: "productPreviewForm",
    };

    const formId = formIds[step];
    console.log("[Product Flow] Form ID:", formId);

    if (formId) {
      // Load saved data into form
      loadFormData(formId);

      // Setup Back button
      const backBtn = document.getElementById("backBtn");
      console.log("[Product Flow] Back button found:", !!backBtn);
      if (backBtn) {
        backBtn.addEventListener("click", function (e) {
          e.preventDefault();
          console.log("[Product Flow] Back button clicked");
          handleBack();
        });
      }

      // Setup Next button
      const nextBtn = document.getElementById("nextBtn");
      console.log("[Product Flow] Next button found:", !!nextBtn);
      if (nextBtn) {
        nextBtn.addEventListener("click", function (e) {
          e.preventDefault();
          console.log("[Product Flow] Next button clicked");
          handleNext(formId);
        });
      }

      // Setup Submit button
      const submitBtn = document.getElementById("submitBtn");
      const form = document.getElementById(formId);
      console.log("[Product Flow] Submit button found:", !!submitBtn);
      if (submitBtn && form) {
        form.addEventListener("submit", (e) => handleSubmit(e, formId));
      }
    }

    // Clear data on final submission success
    // (This would be triggered by the server redirecting to success page)
    if (
      window.location.href.includes("/seller/products") &&
      sessionStorage.getItem(STORAGE_KEY)
    ) {
      clearFormData();
    }
  });

  // Expose functions globally if needed
  window.ProductFormFlow = {
    saveFormData,
    loadFormData,
    clearFormData,
    getCurrentStep,
  };
})();
