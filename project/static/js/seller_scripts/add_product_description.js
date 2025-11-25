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
    const description = document.getElementById("description");
    const materials = document.getElementById("materials");
    const detailsFit = document.getElementById("detailsFit");
    // Clear previous errors
    description && clearErrorFor(description);
    materials && clearErrorFor(materials);
    detailsFit && clearErrorFor(detailsFit);
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
    // helper to update visual preview inside the label
    function setPreviewFromFile(file) {
      if (!parentLabel) return;
      const placeholder = parentLabel.querySelector(
        ".cert-upload-placeholder, .sizeguide-placeholder"
      );
      // remove existing thumb if present
      const existing = parentLabel.querySelector("img.upload-thumb");
      if (existing) existing.remove();

      if (file && file.type && file.type.startsWith("image/")) {
        const reader = new FileReader();
        reader.onload = function (e) {
          const img = document.createElement("img");
          img.className = "upload-thumb";
          img.src = e.target.result;
          img.alt = "Upload preview";
          // hide placeholder content
          if (placeholder) placeholder.style.display = "none";
          parentLabel.appendChild(img);
        };
        reader.readAsDataURL(file);
        parentLabel.classList.add("has-file");
      } else {
        // no file -> show placeholder
        if (placeholder) placeholder.style.display = "flex";
        parentLabel.classList.remove("has-file");
      }
    }

    // initialize state
    if (input.files && input.files.length > 0) {
      setPreviewFromFile(input.files[0]);
    }

    input.addEventListener("change", function () {
      if (this.files && this.files.length > 0) {
        setPreviewFromFile(this.files[0]);
        clearErrorFor(this);
      } else {
        setPreviewFromFile(null);
      }
    });
  }

  // Initialize any existing certification or sizeguide inputs
  document
    .querySelectorAll(
      'input[name="certifications[]"], input[name="sizeGuide[]"]'
    )
    .forEach(setupFileInput);
  // Size guide inputs removed

  // Utility to add a new upload slot to a container (returns the created input)
  function addUploadSlot(
    container,
    inputName,
    boxClass,
    placeholderClass = "cert-upload-placeholder"
  ) {
    const label = document.createElement("label");
    label.className = boxClass;

    const input = document.createElement("input");
    input.type = "file";
    input.name = inputName;
    input.accept = "image/*";

    const placeholder = document.createElement("div");
    placeholder.className = placeholderClass;
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
        // Sizeguide add button handling
        const sizeguideContainer =
          document.getElementById("sizeguideContainer");
        const sizeguideAddBtn = document.getElementById("sizeguideAddBtn");
        if (sizeguideAddBtn && sizeguideContainer) {
          sizeguideAddBtn.addEventListener("click", function () {
            const current =
              sizeguideContainer.querySelectorAll(".sizeguide-box").length;
            if (current >= 5) return;
            const input = addUploadSlot(
              sizeguideContainer,
              "sizeGuide[]",
              "sizeguide-box",
              "sizeguide-placeholder"
            );
            // open file dialog for new input
            input.click();
            // disable add button when reach max
            const after =
              sizeguideContainer.querySelectorAll(".sizeguide-box").length;
            if (after >= 5) {
              sizeguideAddBtn.disabled = true;
              sizeguideAddBtn.classList.add("disabled");
            }
          });
          // initialize disabled state
          if (
            sizeguideContainer.querySelectorAll(".sizeguide-box").length >= 5
          ) {
            sizeguideAddBtn.disabled = true;
            sizeguideAddBtn.classList.add("disabled");
          }
        }
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
    // Collect size guide and certification preview images (data URLs if available)
    function collectPreviewList(containerSelector, imgSelector) {
      const container = document.querySelector(containerSelector);
      if (!container) return [];
      const imgs = Array.from(container.querySelectorAll(imgSelector));
      return imgs
        .map((img) => img.src)
        .filter(
          (s) => (s && s.indexOf("data:") === 0) || (s && s.indexOf("/") === 0)
        );
    }

    // sizeGuide inputs are inside #sizeguideContainer
    formData.sizeGuide = collectPreviewList(
      "#sizeguideContainer",
      "img.upload-thumb"
    );
    // certifications inputs are inside #certificationsContainer
    formData.certifications = collectPreviewList(
      "#certificationsContainer",
      "img.upload-thumb"
    );

    storeFormData("productDescriptionForm", formData);
    window.location.href = "/seller/add_product_stocks";
  });
});
