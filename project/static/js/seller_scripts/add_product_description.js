// Function to store form data in sessionStorage
function storeFormData(formId, data) {
  sessionStorage.setItem(formId, JSON.stringify(data));
}

// Function to get stored form data
function getStoredFormData(formId) {
  const data = sessionStorage.getItem(formId);
  return data ? JSON.parse(data) : null;
}

document.addEventListener("DOMContentLoaded", function () {
  // Load any previously stored data
  const storedData = getStoredFormData("productDescriptionForm");
  if (storedData) {
    document.getElementById("description").value = storedData.description || "";
    document.getElementById("materials").value = storedData.materials || "";
    document.getElementById("detailsFit").value = storedData.detailsFit || "";
  }

  // Utility: show or remove an error message for an element
  function showErrorFor(element, message) {
    // For file inputs, show error under the .file-upload-area container
    let container =
      element.closest(".file-upload-area") || element.parentElement;
    // If a .form-group wrapper exists, prefer it for placement
    const formGroup = element.closest(".form-group");
    if (formGroup) container = formGroup;

    // Mark invalid state
    element.classList.add("input-error");
    if (container) container.classList.add("input-error");

    // Find existing error node
    let err = container.querySelector(".error-message");
    if (!err) {
      err = document.createElement("div");
      err.className = "error-message";
      container.appendChild(err);
    }
    err.textContent = message;
  }

  function clearErrorFor(element) {
    let container =
      element.closest(".file-upload-area") || element.parentElement;
    const formGroup = element.closest(".form-group");
    if (formGroup) container = formGroup;

    element.classList.remove("input-error");
    if (container) container.classList.remove("input-error");
    const err = container && container.querySelector(".error-message");
    if (err) err.remove();
  }

  function validatePage2() {
    let valid = true;
    const sizeGuideInputs = document.querySelectorAll(
      'input[name="sizeGuide[]"]'
    );
    const description = document.getElementById("description");
    const materials = document.getElementById("materials");
    const detailsFit = document.getElementById("detailsFit");
    // Clear previous errors
    description && clearErrorFor(description);
    materials && clearErrorFor(materials);
    detailsFit && clearErrorFor(detailsFit);
    // clear errors for any sizeguide inputs
    if (sizeGuideInputs && sizeGuideInputs.length) {
      sizeGuideInputs.forEach((el) => clearErrorFor(el));
    }

    // File input: must have at least one selected size guide file
    let hasSizeGuide = false;
    if (sizeGuideInputs && sizeGuideInputs.length) {
      sizeGuideInputs.forEach((inp) => {
        if (inp.files && inp.files.length > 0) hasSizeGuide = true;
      });
    }
    if (!hasSizeGuide) {
      // show error on the first sizeguide input or container
      const first =
        sizeGuideInputs && sizeGuideInputs.length ? sizeGuideInputs[0] : null;
      showErrorFor(first || description, "Please upload a size guide photo.");
      valid = false;
    }

    // Textareas: must not be empty (trimmed)
    if (!description || description.value.trim() === "") {
      showErrorFor(description, "Please enter a product description.");
      valid = false;
    }

    if (!materials || materials.value.trim() === "") {
      showErrorFor(materials, "Please enter materials and care instructions.");
      valid = false;
    }

    if (!detailsFit || detailsFit.value.trim() === "") {
      showErrorFor(detailsFit, "Please enter the product details and fit.");
      valid = false;
    }

    return valid;
  }

  // Wire up input/change listeners to clear errors as the user types/selects
  ["description", "materials", "detailsFit"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("input", function () {
        if (this.value.trim() !== "") clearErrorFor(this);
      });
    }
  });

  // Helper to attach change handler to file inputs to toggle .has-file and clear errors
  function setupFileInput(input) {
    const parentLabel = input.closest(".cert-upload-box, .sizeguide-box");
    // initialize state
    if (input.files && input.files.length > 0) {
      if (parentLabel) parentLabel.classList.add("has-file");
    }
    input.addEventListener("change", function () {
      if (this.files && this.files.length > 0) {
        if (parentLabel) parentLabel.classList.add("has-file");
        clearErrorFor(this);
      } else {
        if (parentLabel) parentLabel.classList.remove("has-file");
      }
    });
  }

  // Initialize any existing certification or sizeguide inputs
  document
    .querySelectorAll('input[name="certifications[]"]')
    .forEach(setupFileInput);
  document
    .querySelectorAll('input[name="sizeGuide[]"]')
    .forEach(setupFileInput);

  // Utility to add a new upload slot to a container (returns the created input)
  function addUploadSlot(container, inputName, boxClass) {
    const label = document.createElement("label");
    label.className = boxClass;

    const input = document.createElement("input");
    input.type = "file";
    input.name = inputName;
    input.accept = "image/*";

    const placeholder = document.createElement("div");
    placeholder.className =
      boxClass === "cert-upload-box"
        ? "cert-upload-placeholder"
        : "sizeguide-placeholder";
    const icon = document.createElement("i");
    icon.className = "ri-image-line";
    const small = document.createElement("small");
    small.textContent = "Upload photo";
    placeholder.appendChild(icon);
    placeholder.appendChild(small);

    label.appendChild(input);
    label.appendChild(placeholder);

    // insert before the add button if present, otherwise append
    const addBtn = container.querySelector(".cert-add-box, .sizeguide-add-box");
    if (addBtn) container.insertBefore(label, addBtn);
    else container.appendChild(label);

    setupFileInput(input);
    return input;
  }

  // Handle cert add button
  const certContainer = document.getElementById("certificationsContainer");
  const certAddBtn = document.getElementById("certAddBtn");
  if (certAddBtn && certContainer) {
    certAddBtn.addEventListener("click", function () {
      const current = certContainer.querySelectorAll(".cert-upload-box").length;
      if (current >= 5) return;
      const input = addUploadSlot(
        certContainer,
        "certifications[]",
        "cert-upload-box"
      );
      // open file dialog for new input
      input.click();
      // disable add button when reach max
      const after = certContainer.querySelectorAll(".cert-upload-box").length;
      if (after >= 5) {
        certAddBtn.disabled = true;
        certAddBtn.classList.add("disabled");
      }
    });
    // initialize disabled state
    if (certContainer.querySelectorAll(".cert-upload-box").length >= 5) {
      certAddBtn.disabled = true;
      certAddBtn.classList.add("disabled");
    }
  }

  // Handle sizeguide add button
  const sizeguideContainer = document.getElementById("sizeguideContainer");
  const sizeguideAddBtn = document.getElementById("sizeguideAddBtn");
  if (sizeguideAddBtn && sizeguideContainer) {
    sizeguideAddBtn.addEventListener("click", function () {
      const current =
        sizeguideContainer.querySelectorAll(".sizeguide-box").length;
      if (current >= 5) return;
      const input = addUploadSlot(
        sizeguideContainer,
        "sizeGuide[]",
        "sizeguide-box"
      );
      input.click();
      // disable add when reach max
      const after =
        sizeguideContainer.querySelectorAll(".sizeguide-box").length;
      if (after >= 5) {
        sizeguideAddBtn.disabled = true;
        sizeguideAddBtn.classList.add("disabled");
      }
    });
    // initialize disabled state
    if (sizeguideContainer.querySelectorAll(".sizeguide-box").length >= 5) {
      sizeguideAddBtn.disabled = true;
      sizeguideAddBtn.classList.add("disabled");
    }
  }

  // Back button handler
  document.getElementById("backBtn").addEventListener("click", function () {
    window.location.href = "/seller/add_product";
  });

  // Next button handler: validate before navigating
  document.getElementById("nextBtn").addEventListener("click", function (e) {
    e.preventDefault();
    const isValid = validatePage2();
    if (!isValid) {
      // focus first invalid field for accessibility
      const firstInvalid = document.querySelector(".input-error");
      if (firstInvalid) {
        const el =
          firstInvalid.querySelector("input, textarea") || firstInvalid;
        if (el && typeof el.focus === "function") el.focus();
      }
      return;
    }

    // Store form data and proceed
    const formData = {
      description: document.getElementById("description").value,
      materials: document.getElementById("materials").value,
      detailsFit: document.getElementById("detailsFit").value,
    };

    storeFormData("productDescriptionForm", formData);
    window.location.href = "/seller/add_product_stocks";
  });
});
