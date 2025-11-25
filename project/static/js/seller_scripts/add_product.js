// Sub-items data based on subcategory
const subItems = {
  Tops: [
    "T-Shirts",
    "Blouses",
    "Button-downs",
    "Tank Tops",
    "Crop Tops",
    "Tube Tops",
    "Tunics",
    "Wrap Tops",
    "Peplum Tops",
    "Bodysuits",
    "Sweaters",
    "Cardigans",
    "Sweatshirts Hoodies",
  ],
  Bottoms: [
    "Jeans",
    "Pants & Trousers",
    "Leggings & Jeggings",
    "Skirts",
    "Shorts",
    "Culottes & Capris",
  ],
  Dresses: [
    "Casual Dresses",
    "Work/Office Dresses",
    "Shirt Dresses",
    "Wrap Dresses",
    "Maxi Dresses",
    "Midi Dresses",
    "Mini Dresses",
    "Bodycon",
    "A-Line",
    "Cocktail",
    "Evening Gowns",
    "Sundresses",
  ],
  Outerwear: [
    "Jackets",
    "Coats",
    "Blazers",
    "Vests & Gilets",
    "Capes & Ponchos",
    "Cardigans",
  ],
  Activewear: [
    "Sports Bras",
    "Active Tops",
    "Leggings & Yoga Pants",
    "Joggers & Track Pants",
    "Biker Shorts",
    "Hoodies & Sweatshirts",
    "Tracksuits & Co-ords",
  ],
  Sleepwear: [
    "Pajama Sets",
    "Nightgowns & Chemises",
    "Robes & Kimonos",
    "Sleep Shirts",
    "Lounge Tops",
    "Lounge Pants & Shorts",
    "Matching Loungewear Sets",
  ],
  Undergarments: [
    "Bras",
    "Panties",
    "Shapewear",
    "Slips & Camisoles",
    "Lingerie Sets",
    "Hosiery",
  ],
  Swimwear: [
    "Bikinis",
    "One-piece Swimsuits",
    "Tankinis",
    "Monokinis/Cut-out Suits",
    "Cover-Ups",
    "Rash Guards & Swim Tops",
  ],
  Occasionwear: [
    "Formal Wear",
    "Party Wear",
    "Wedding Wear",
    "Festive Wear",
    "Cultural/Traditional Wear",
  ],
  Heels: [
    "Stilettos",
    "Pumps",
    "Block Heels",
    "Wedge Heels",
    "Kitten Heels",
    "Platform Heels",
    "Ankle Strap Heels",
    "Mules",
    "Peep Toe Heels",
    "Slingbacks",
  ],
  Flats: [
    "Ballet Flats",
    "Loafers",
    "Moccasins",
    "Espadrilles",
    "Flat Sandals",
  ],
  Sandals: [
    "Strappy Sandals",
    "Gladiators Sandals",
    "Slide Sandals",
    "Slingback Sandals",
  ],
  Sneakers: [
    "Casual Sneakers",
    "Fashion/Lifestyle Sneakers",
    "Chunky/Platform Sneakers",
    "Slip-on Sneakers",
  ],
  Boots: [
    "Ankle Boots",
    "Knee-High Boots",
    "Over-the-Knee/ Thigh-High Boots",
    "Chelsea Boots",
    "Combat Boots",
  ],
  Slippers: ["Indoor Slippers", "Flip-Flops", "Slip-on Comfort Sandals"],
  DressShoes: ["Party Shoes", "Wedding Shoes", "Formal Dress Shoes"],
  Bags: [
    "Handbags",
    "Shoulder Bags",
    "Tote Bags",
    "Crossbody Bags",
    "Clutches/Evening Bags",
    "Backpacks",
    "Wallets & Pouches",
  ],
  Jewelry: [
    "Necklaces & Pendants",
    "Earrings",
    "Bracelets & Bangles",
    "Rings",
    "Anklets",
    "Brooches & Pins",
  ],
  HairAccessories: [
    "Hairbands/Headbands",
    "Hair Clips & Barrets",
    "Scrunchies",
    "Hair Scarves & Wraps",
    "Hair Claws",
  ],
  Belts: [
    "Waist Belts",
    "Skinny Belts",
    "Wide Belts/Statement Belts",
    "Chain Belts",
  ],
  Scarves: ["Slik Scarves", "Shawls", "Wraps/Stoles", "Bandanas"],
  Hats: [
    "Sun Hats",
    "Fedoras",
    "Beanies",
    "Baseball Caps",
    "Berets",
    "Bucket Hats",
  ],
  Eyewear: ["Sunglasses", "Eyeglasses Frames", "Reading Glasses"],
  Watches: ["Dress Watches", "Casual Watches", "Smartwatches"],
  Gloves: ["Fashion Gloves", "Winter Gloves", "Evening Gloves"],
  Others: [
    "Keychains",
    "Phone Cases",
    "Tech Accessories",
    "Umbrellas",
    "Luggage & Travel Accessories",
  ],
};

// Subcategories data based on category
const subcategories = {
  clothing: [
    "Tops",
    "Bottoms",
    "Dresses",
    "Outerwear",
    "Activewear",
    "Sleepwear",
    "Undergarments",
    "Swimwear",
    "Occasionwear",
  ],
  shoes: [
    "Heels",
    "Flats",
    "Sandals",
    "Sneakers",
    "Boots",
    "Slippers & Comfort Wear",
    "Occasion / Dress Shoes",
  ],
  accessories: [
    "Bags",
    "Jewelry",
    "Hair Accessories",
    "Belts",
    "Scarves & Wraps",
    "Hats & Caps",
    "Eyewear",
    "Watches",
    "Gloves",
    "Others",
  ],
};

// Filters data based on category and subcategory
const filters = {
  clothing: {
    Tops: {
      Fit: ["Slim Fit", "Regular Fit", "Relaxed Fit", "Oversized"],
      SleeveLength: [
        "Sleeveless",
        "Short Sleeves",
        "3/4 Sleeves",
        "Long Sleeves",
      ],
      Neckline: [
        "Crew Neck",
        "Round Neck",
        "V-Neck",
        "Scoop Neck",
        "Square Neck",
        "Sweetheart Neck",
        "Boat Neck",
        "Off-Shoulder",
        "One-Shoulder",
        "Halter Neck",
        "Keyhole Neck",
        "Turtleneck",
        "Cowl Neck",
        "Asymmetric Neckline",
        "Collared Neck",
        "Plunge Neck",
        "Jewel Neck",
      ],
      Length: ["Crop", "Regular", "Longline"],
    },
    Bottoms: {
      Fit: ["Skinny", "Straight", "Wide-Leg", "Bootcut", "Relaxed"],
      Rise: ["High Rise", "Mid Rise", "Low Rise"],
      Length: ["Full", "Ankle", "Capri", "Shorts"],
    },
    Dresses: {
      Length: ["Mini Dress", "Midi Dress", "Maxi Dress"],
      Fit: ["Bodycon", "A-line", "Flowy"],
      Occasion: ["Casual", "Work", "Cocktail", "Evening", "Wedding"],
    },
    Outerwear: {
      Thickness: ["Light", "Medium", "Heavy"],
      Style: ["Casual", "Formal"],
      Length: ["Cropped", "Hip", "Longline"],
    },
    Activewear: {
      Function: ["Yoga", "Running", "Gym", "Athleisure"],
      Support: ["Low", "Medium", "High"],
      Material: ["Moisture-Wicking", "Stretch", "Breathable"],
    },
    Sleepwear: {
      Style: ["Two-piece", "One-piece", "Loungewear", "Robe"],
      Fabric: ["Cotton", "Satin", "Silk", "Fleece"],
    },
    Undergarments: {
      Type: ["Bras", "Panties", "Shapewear", "Lingerie"],
      Coverage: ["Full", "Mid", "Minimal"],
      Padding: ["Padded", "Non-padded"],
    },
  },
  shoes: {
    Heels: {
      "Heel Type": [
        "Stilettos",
        "Pumps",
        "Block Heels",
        "Wedge Heels",
        "Kitten Heels",
        "Platform Heels",
        "Ankle Strap Heels",
        "Mules",
        "Peep Toe Heels",
        "Slingbacks",
      ],
      Height: ['Low (1-2")', 'Medium (2-3")', 'High (3-4")', 'Very High (4"+)'],
    },
    Flats: {
      Style: ["Ballet Flats", "Loafers", "Moccasins", "Oxfords", "Espadrilles"],
      "Toe Shape": ["Round Toe", "Pointed Toe", "Square Toe", "Almond Toe"],
    },
    Sandals: {
      Style: ["Slide Sandals", "Gladiator", "Strappy", "Sport Sandals"],
      Sole: ["Flat", "Platform", "Wedge"],
    },
    Sneakers: {
      Style: ["Low-top", "High-top", "Slip-on", "Running", "Fashion"],
      Purpose: ["Casual", "Athletic", "Training"],
    },
    Boots: {
      Height: ["Ankle", "Mid-calf", "Knee-high", "Over-the-knee"],
      Style: ["Combat", "Chelsea", "Western", "Rain"],
    },
  },
  accessories: {
    Bags: {
      Type: [
        "Handbags",
        "Shoulder Bags",
        "Tote Bags",
        "Crossbody Bags",
        "Clutches / Evening Bags",
        "Backpacks",
        "Wallets & Pouches",
      ],
      Size: ["Small", "Medium", "Large"],
    },
    Jewelry: {
      Type: ["Necklaces", "Earrings", "Bracelets", "Rings", "Anklets"],
      Style: ["Minimalist", "Statement", "Vintage", "Modern"],
    },
  },
};

// Material options based on category
const materials = {
  clothing: [
    "Cotton",
    "Linen",
    "Silk",
    "Wool",
    "Cashmere",
    "Hemp",
    "Polyester",
    "Nylon",
    "Acrylic",
    "Rayon (Viscose)",
    "Spandex / Lycra / Elastane",
    "Cotton-Polyester (blend)",
    "Wool-Acrylic (blend)",
    "Rayon-Spandex (blend)",
    "Velvet",
    "Chiffon",
    "Organza",
    "Tulle",
    "Satin",
    "Tweed",
    "Denim",
    "Leather / Faux Leather",
    "Suede",
  ],
  shoes: ["Leather", "Faux Leather", "Suede", "Canvas", "Rubber", "Knit"],
};

// Current page tracking
const currentPage = 1;
const totalPages = 2;

function getHiddenPhotoInput(index) {
  if (Number(index) === 0) {
    return document.getElementById("primaryImageField");
  }
  if (Number(index) === 1) {
    return document.getElementById("secondaryImageField");
  }
  return null;
}

function persistProductFormDraft() {
  if (
    window.ProductFormFlow &&
    typeof window.ProductFormFlow.saveFormData === "function"
  ) {
    window.ProductFormFlow.saveFormData("productForm");
  }
}

function updatePhotoPreview(box, dataUrl) {
  const preview = box.querySelector(".photo-preview");
  const img = preview ? preview.querySelector("img") : null;
  const removeBtn = preview ? preview.querySelector(".remove-photo") : null;
  const labelEl = box.querySelector(".photo-label");
  if (!preview || !img) return;
  if (dataUrl) {
    img.src = dataUrl;
    preview.classList.add("active");
    if (removeBtn) removeBtn.style.display = "flex";
    if (labelEl) labelEl.style.display = "none";
  } else {
    img.src = "#";
    preview.classList.remove("active");
    if (removeBtn) removeBtn.style.display = "none";
    if (labelEl) labelEl.style.display = "";
  }
}

function setupPhotoUploads() {
  const boxes = document.querySelectorAll(".photo-upload-box");
  if (!boxes.length) {
    console.warn("No photo upload boxes found");
    return;
  }
  console.log(`Setting up ${boxes.length} photo upload boxes`);
  boxes.forEach((box) => {
    const input = box.querySelector(".photo-input");
    const removeBtn = box.querySelector(".remove-photo");
    const idx = Number(box.dataset.index || 0);
    const hiddenInput = getHiddenPhotoInput(idx);

    if (hiddenInput && hiddenInput.value) {
      updatePhotoPreview(box, hiddenInput.value);
    } else {
      updatePhotoPreview(box, "");
    }

    const handleFileSelection = (file) => {
      if (!file) return;
      if (!file.type.startsWith("image/")) {
        alert("Please upload an image file.");
        if (input) {
          input.value = "";
        }
        return;
      }
      const reader = new FileReader();
      reader.onload = (e) => {
        const dataUrl = e.target?.result;
        if (hiddenInput) {
          hiddenInput.value = dataUrl || "";
        }
        updatePhotoPreview(box, dataUrl);
        persistProductFormDraft();
      };
      reader.readAsDataURL(file);
    };

    if (input) {
      input.addEventListener("change", (event) => {
        const file = event.target.files && event.target.files[0];
        handleFileSelection(file);
      });
    }

    if (removeBtn) {
      removeBtn.addEventListener("click", (event) => {
        event.preventDefault();
        if (input) {
          input.value = "";
        }
        if (hiddenInput) {
          hiddenInput.value = "";
        }
        updatePhotoPreview(box, "");
        persistProductFormDraft();
      });
    }

    const label = box.querySelector(".photo-label");
    const previewArea = box.querySelector(".photo-preview");
    const makeClickable = (target) => {
      if (!target) return;
      target.addEventListener("click", (event) => {
        // Don't trigger if clicking the remove button
        if (event.target?.classList?.contains("remove-photo") || 
            event.target?.closest(".remove-photo")) {
          return;
        }
        event.preventDefault();
        event.stopPropagation();
        console.log("Photo upload area clicked, triggering file input");
        if (input) {
          input.click();
        } else {
          console.error("No file input found for photo upload box");
        }
      });
      
      // Add visual feedback
      target.style.cursor = "pointer";
    };
    
    // Make the entire box clickable
    makeClickable(box);
    
    // Make the label clickable (this should already work with the 'for' attribute)
    if (label) {
      makeClickable(label);
    }
    
    // Make the preview area clickable when image is shown
    if (previewArea) {
      makeClickable(previewArea);
      
      // Also make the preview image itself clickable
      const previewImg = previewArea.querySelector("img");
      if (previewImg) {
        makeClickable(previewImg);
      }
      
      // Make the overlay clickable too
      const overlay = previewArea.querySelector(".photo-overlay");
      if (overlay) {
        makeClickable(overlay);
      }
    }

    // Make the upload box and label keyboard accessible (Enter/Space triggers file picker)
    const makeAccessibleButton = (el) => {
      if (!el) return;
      try {
        el.setAttribute("tabindex", "0");
        el.setAttribute("role", "button");
      } catch (e) {}
      el.addEventListener("keydown", (evt) => {
        const key = evt.key || evt.keyCode;
        if (key === "Enter" || key === " " || key === 13 || key === 32) {
          evt.preventDefault();
          input?.click();
        }
      });
    };
    makeAccessibleButton(box);
    makeAccessibleButton(label);
    makeAccessibleButton(previewArea);

    // Make the preview image itself keyboard accessible and visibly clickable
    if (previewArea) {
      const previewImg = previewArea.querySelector("img");
      if (previewImg) {
        // Visual affordance
        previewImg.style.cursor = "pointer";
        // Accessibility: make focusable and respond to Enter/Space
        previewImg.setAttribute("tabindex", "0");
        previewImg.setAttribute("role", "button");
        previewImg.setAttribute("aria-label", "Upload photo");
        previewImg.addEventListener("keydown", (evt) => {
          const code = evt.key || evt.keyCode;
          if (code === "Enter" || code === " " || code === 13 || code === 32) {
            evt.preventDefault();
            input?.click();
          }
        });
      }
    }

    const toggleDragState = (state) => {
      if (!box) return;
      if (state) {
        box.classList.add("dragover");
      } else {
        box.classList.remove("dragover");
      }
    };

    ["dragenter", "dragover"].forEach((eventName) => {
      box.addEventListener(
        eventName,
        (event) => {
          event.preventDefault();
          toggleDragState(true);
        },
        false
      );
    });

    ["dragleave", "dragend"].forEach((eventName) => {
      box.addEventListener(
        eventName,
        (event) => {
          event.preventDefault();
          toggleDragState(false);
        },
        false
      );
    });

    box.addEventListener(
      "drop",
      (event) => {
        event.preventDefault();
        toggleDragState(false);
        const file =
          (event.dataTransfer &&
            event.dataTransfer.files &&
            event.dataTransfer.files[0]) ||
          null;
        handleFileSelection(file);
      },
      false
    );
  });
}

// DOM Elements
const pages = document.querySelectorAll(".form-page");
const progressSteps = document.querySelectorAll(".progress-step");
const backBtn = document.getElementById("backBtn");
const nextBtn = document.getElementById("nextBtn");
const submitBtn = document.getElementById("submitBtn");

// Declare variables (support both old and new element IDs for compatibility)
const categorySelect = document.getElementById("category");
const subcategorySelect = document.getElementById("subcategory");
const filtersContainer = document.getElementById("dynamicFiltersContainer"); // Use correct ID
const filtersSection = document.getElementById("filtersSection");
const subItemsContainer = document.getElementById("subItemsContainer");

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  setupCategoryChange();
  setupPhotoUploads();

  // Enhance form UI: mark required fields (except model info) and prepare error placeholders
  setupRequiredUI();

  // Close all filter dropdowns by default
  document
    .querySelectorAll(".filter-group .filter-content")
    .forEach((content) => {
      content.style.display = "none";
    });

  // Add click event to filter headers to toggle dropdown
  document
    .querySelectorAll(".filter-group .filter-header")
    .forEach((header) => {
      header.addEventListener("click", function () {
        const content = this.nextElementSibling;
        if (content) {
          content.style.display =
            content.style.display === "none" || content.style.display === ""
              ? "block"
              : "none";
        }
      });
    });
});

function setupRequiredUI() {
  const form = document.getElementById("productForm");
  if (!form) return;

  const selector =
    'input[type="text"], input[type="number"], input[type="email"], input[type="tel"], input[type="file"], textarea, select';
  const controls = Array.from(form.querySelectorAll(selector));
  const skipIds = [
    "modelHeight",
    "wearingSize",
    "discountPercentage",
    "discountType",
    "voucherType",
  ];
  // Do not mark photo inputs/hidden fields as required (remove asterisk)
  skipIds.push(
    "primaryImageField",
    "secondaryImageField",
    "photoInput0",
    "photoInput1"
  );
  // Do not mark photo inputs/hidden fields as required (remove asterisk)
  skipIds.push(
    "primaryImageField",
    "secondaryImageField",
    "photoInput0",
    "photoInput1"
  );

  controls.forEach((el) => {
    // For fields in skip list, ensure they don't have required attribute
    if (skipIds.includes(el.id)) {
      el.removeAttribute("required");
      return;
    }

    if (el.type === "checkbox" || el.type === "radio") return;

    // Only mark as required if not in skip list
    if (!el.hasAttribute("required")) {
      el.setAttribute("required", "");
    }

    // Add red asterisk to label if present and not already there
    if (el.id) {
      const lbl = form.querySelector(`label[for="${el.id}"]`);
      if (lbl) {
        // Check if asterisk already exists (either as span or in text)
        const hasAsteriskSpan = lbl.querySelector(".required-asterisk");
        const hasAsteriskText = lbl.textContent.trim().endsWith("*");

        if (!hasAsteriskSpan && !hasAsteriskText) {
          const span = document.createElement("span");
          span.className = "required-asterisk";
          span.textContent = " *";
          lbl.appendChild(span);
        }
      }
    }

    // Add error placeholder in the logical spot (below the input box).
    // For inputs wrapped in .input-with-prefix / .input-with-suffix, place the
    // error after the wrapper so it appears below the visual input box.
    let containerEl = el.parentElement;
    if (
      containerEl &&
      (containerEl.classList.contains("input-with-prefix") ||
        containerEl.classList.contains("input-with-suffix") ||
        containerEl.classList.contains("file-upload-area"))
    ) {
      // use the parent .form-group as the container
      if (containerEl.parentElement) containerEl = containerEl.parentElement;
    }

    let err = containerEl.querySelector(".field-error");
    if (!err) {
      err = document.createElement("div");
      err.className = "field-error";
      err.style.display = "none";
      err.textContent = "Please input this field";
      // insert as the last child of the container (.form-group) so the
      // error appears directly below the input box within the same group
      containerEl.appendChild(err);
    }

    // hide error on input
    el.addEventListener("input", () => {
      err.style.display = "none";
      el.classList.remove("invalid-field");
    });
  });
}

// Category and Subcategory Handling
// Variation options based on category
const variationOptions = {
  clothing: {
    sizes: [
      { value: "xs", label: "XS" },
      { value: "s", label: "S" },
      { value: "m", label: "M" },
      { value: "l", label: "L" },
      { value: "xl", label: "XL" },
      { value: "xxl", label: "XXL" },
      { value: "xxxl", label: "XXXL" },
      { value: "onesize", label: "One Size" },
    ],
    colors: [
      { value: "black", label: "Black", hex: "#000000" },
      { value: "white", label: "White", hex: "#FFFFFF" },
      { value: "off_white", label: "Off White", hex: "#FAF9F6" },
      { value: "beige", label: "Beige", hex: "#F5F5DC" },
      { value: "cream", label: "Cream", hex: "#FFFDD0" },
      { value: "tan", label: "Tan", hex: "#D2B48C" },
      { value: "brown", label: "Brown", hex: "#8B4513" },
      { value: "camel", label: "Camel", hex: "#C19A6B" },
      { value: "gray", label: "Gray", hex: "#808080" },
      { value: "charcoal", label: "Charcoal", hex: "#36454F" },
      { value: "navy", label: "Navy", hex: "#000080" },
      { value: "blue", label: "Blue", hex: "#1E90FF" },
      { value: "baby_blue", label: "Baby Blue", hex: "#89CFF0" },
      { value: "denim", label: "Denim", hex: "#1560BD" },
      { value: "red", label: "Red", hex: "#FF0000" },
      { value: "maroon", label: "Maroon", hex: "#800000" },
      { value: "burgundy", label: "Burgundy", hex: "#800020" },
      { value: "pink", label: "Pink", hex: "#FFC0CB" },
      { value: "blush", label: "Blush", hex: "#F9C6C9" },
      { value: "rose", label: "Rose", hex: "#EBA0A0" },
      { value: "mauve", label: "Mauve", hex: "#E0B0FF" },
      { value: "purple", label: "Purple", hex: "#800080" },
      { value: "lavender", label: "Lavender", hex: "#E6E6FA" },
      { value: "lilac", label: "Lilac", hex: "#C8A2C8" },
      { value: "green", label: "Green", hex: "#228B22" },
      { value: "sage", label: "Sage", hex: "#B2AC88" },
      { value: "olive", label: "Olive", hex: "#808000" },
      { value: "mint", label: "Mint", hex: "#98FF98" },
      { value: "yellow", label: "Yellow", hex: "#FFFF00" },
      { value: "mustard", label: "Mustard", hex: "#FFDB58" },
      { value: "gold", label: "Gold", hex: "#FFD700" },
      { value: "orange", label: "Orange", hex: "#FFA500" },
      { value: "rust", label: "Rust", hex: "#B7410E" },
      { value: "coral", label: "Coral", hex: "#FF7F50" },
      { value: "peach", label: "Peach", hex: "#FFE5B4" },
      { value: "brownish_pink", label: "Brownish Pink", hex: "#C08081" },
      { value: "teal", label: "Teal", hex: "#008080" },
      { value: "turquoise", label: "Turquoise", hex: "#40E0D0" },
      { value: "aqua", label: "Aqua", hex: "#00FFFF" },
      { value: "silver", label: "Silver", hex: "#C0C0C0" },
      { value: "champagne", label: "Champagne", hex: "#F7E7CE" },
      { value: "rose_gold", label: "Rose Gold", hex: "#B76E79" },
      { value: "burgundy", label: "Burgundy", hex: "#800020" },
      { value: "wine", label: "Wine", hex: "#722F37" },
      { value: "ivory", label: "Ivory", hex: "#FFFFF0" },
    ],
  },
  shoes: {
    sizes: [
      { value: "US 5", label: "US 5" },
      { value: "US 6", label: "US 6" },
      { value: "US 7", label: "US 7" },
      { value: "US 8", label: "US 8" },
      { value: "US 9", label: "US 9" },
      { value: "US 10", label: "US 10" },
      { value: "US 11", label: "US 11" },
      { value: "US 12", label: "US 12" },
    ],
    colors: [
      { value: "black", label: "Black", hex: "#000000" },
      { value: "white", label: "White", hex: "#FFFFFF" },
      { value: "beige", label: "Beige", hex: "#F5F5DC" },
      { value: "brown", label: "Brown", hex: "#8B4513" },
      { value: "tan", label: "Tan", hex: "#D2B48C" },
      { value: "nude", label: "Nude", hex: "#E3BC9A" },
      { value: "gray", label: "Gray", hex: "#808080" },
      { value: "navy", label: "Navy", hex: "#000080" },
      { value: "red", label: "Red", hex: "#FF0000" },
      { value: "burgundy", label: "Burgundy", hex: "#800020" },
      { value: "pink", label: "Pink", hex: "#FFC0CB" },
      { value: "blush", label: "Blush", hex: "#F9C6C9" },
      { value: "purple", label: "Purple", hex: "#800080" },
      { value: "lavender", label: "Lavender", hex: "#E6E6FA" },
      { value: "blue", label: "Blue", hex: "#1E90FF" },
      { value: "denim", label: "Denim", hex: "#1560BD" },
      { value: "green", label: "Green", hex: "#228B22" },
      { value: "olive", label: "Olive", hex: "#808000" },
      { value: "khaki", label: "Khaki", hex: "#C3B091" },
      { value: "gold", label: "Gold", hex: "#FFD700" },
      { value: "silver", label: "Silver", hex: "#C0C0C0" },
      { value: "champagne", label: "Champagne", hex: "#F7E7CE" },
      { value: "cream", label: "Cream", hex: "#FFFDD0" },
      { value: "camel", label: "Camel", hex: "#C19A6B" },
      { value: "off_white", label: "Off White", hex: "#FAF9F6" },
    ],
  },
  accessories: {
    sizes: [
      // 👜 BAG SIZES
      { value: "mini", label: "Mini" },
      { value: "small", label: "Small" },
      { value: "medium", label: "Medium" },
      { value: "large", label: "Large" },
      { value: "extra_large", label: "Extra Large" },

      // 👒 HAT SIZES
      { value: "one_size", label: "One Size" },
      { value: "small_hat", label: "Small (54–55 cm)" },
      { value: "medium_hat", label: "Medium (56–57 cm)" },
      { value: "large_hat", label: "Large (58–59 cm)" },
      { value: "extra_large_hat", label: "Extra Large (60+ cm)" },

      // 👓 SUNGLASSES
      { value: "narrow_frame", label: "Narrow Frame" },
      { value: "medium_frame", label: "Medium Frame" },
      { value: "wide_frame", label: "Wide Frame" },
      { value: "oversized", label: "Oversized" },

      // 💍 JEWELRY
      { value: "adjustable", label: "Adjustable" },
      { value: "ring_5", label: "Ring Size 5 (15.7 mm)" },
      { value: "ring_6", label: "Ring Size 6 (16.5 mm)" },
      { value: "ring_7", label: "Ring Size 7 (17.3 mm)" },
      { value: "ring_8", label: "Ring Size 8 (18.2 mm)" },
      { value: "ring_9", label: "Ring Size 9 (19.0 mm)" },
      { value: "bracelet_small", label: "Bracelet Small (16 cm)" },
      { value: "bracelet_medium", label: "Bracelet Medium (18 cm)" },
      { value: "bracelet_large", label: "Bracelet Large (20 cm)" },
      { value: "necklace_choker", label: "Choker (35–40 cm)" },
      { value: "necklace_short", label: "Short (40–45 cm)" },
      { value: "necklace_medium", label: "Medium (50–55 cm)" },
      { value: "necklace_long", label: "Long (60–70 cm)" },

      // 🧣 SCARVES / BELTS
      { value: "short", label: "Short" },
      { value: "regular", label: "Regular" },
      { value: "long", label: "Long" },
      { value: "extra_long", label: "Extra Long" },
      { value: "slim_belt", label: "Slim Belt (2–3 cm width)" },
      { value: "medium_belt", label: "Medium Belt (3–4 cm width)" },
      { value: "wide_belt", label: "Wide Belt (5+ cm width)" },
      { value: "belt_xs", label: "Belt XS (24–26 in)" },
      { value: "belt_s", label: "Belt S (27–29 in)" },
      { value: "belt_m", label: "Belt M (30–32 in)" },
      { value: "belt_l", label: "Belt L (33–35 in)" },
      { value: "belt_xl", label: "Belt XL (36–38 in)" },
    ],
    colors: [
      { value: "black", label: "Black", hex: "#000000" },
      { value: "white", label: "White", hex: "#FFFFFF" },
      { value: "off_white", label: "Off White", hex: "#FAF9F6" },
      { value: "beige", label: "Beige", hex: "#F5F5DC" },
      { value: "cream", label: "Cream", hex: "#FFFDD0" },
      { value: "tan", label: "Tan", hex: "#D2B48C" },
      { value: "camel", label: "Camel", hex: "#C19A6B" },
      { value: "brown", label: "Brown", hex: "#8B4513" },
      { value: "gray", label: "Gray", hex: "#808080" },
      { value: "charcoal", label: "Charcoal", hex: "#36454F" },
      { value: "gold", label: "Gold", hex: "#FFD700" },
      { value: "silver", label: "Silver", hex: "#C0C0C0" },
      { value: "rose_gold", label: "Rose Gold", hex: "#B76E79" },
      { value: "champagne", label: "Champagne", hex: "#F7E7CE" },
      { value: "bronze", label: "Bronze", hex: "#CD7F32" },
      { value: "pearl", label: "Pearl", hex: "#F8F6F0" },
      { value: "navy", label: "Navy", hex: "#000080" },
      { value: "blue", label: "Blue", hex: "#1E90FF" },
      { value: "sky_blue", label: "Sky Blue", hex: "#87CEEB" },
      { value: "red", label: "Red", hex: "#FF0000" },
      { value: "burgundy", label: "Burgundy", hex: "#800020" },
      { value: "wine", label: "Wine", hex: "#722F37" },
      { value: "pink", label: "Pink", hex: "#FFC0CB" },
      { value: "blush", label: "Blush", hex: "#F9C6C9" },
      { value: "rose", label: "Rose", hex: "#EBA0A0" },
      { value: "purple", label: "Purple", hex: "#800080" },
      { value: "lavender", label: "Lavender", hex: "#E6E6FA" },
      { value: "green", label: "Green", hex: "#228B22" },
      { value: "olive", label: "Olive", hex: "#808000" },
      { value: "sage", label: "Sage", hex: "#B2AC88" },
      { value: "teal", label: "Teal", hex: "#008080" },
      { value: "mint", label: "Mint", hex: "#98FF98" },
      { value: "yellow", label: "Yellow", hex: "#FFFF00" },
      { value: "mustard", label: "Mustard", hex: "#FFDB58" },
      { value: "orange", label: "Orange", hex: "#FFA500" },
      { value: "coral", label: "Coral", hex: "#FF7F50" },
      { value: "peach", label: "Peach", hex: "#FFE5B4" },
      { value: "clear", label: "Clear / Transparent", hex: "#E0E0E0" },
      { value: "multicolor", label: "Multicolor", hex: "#CCCCCC" },
    ],
  },
};

function setupCategoryChange() {
  if (!categorySelect || !subcategorySelect) {
    console.error("[v0] Category or Subcategory select element not found!");
    return;
  }

  categorySelect.addEventListener("change", function () {
    const category = this.value;
    subcategorySelect.innerHTML =
      '<option value="">Select subcategory</option>';

    if (category && subcategories[category]) {
      subcategorySelect.disabled = false;
      subcategories[category].forEach((sub) => {
        const option = document.createElement("option");
        option.value = sub;
        option.textContent = sub;
        subcategorySelect.appendChild(option);
      });

      // Clear filters when category changes
      if (filtersContainer) {
        filtersContainer.innerHTML = "";
      }
      const noFiltersMsg = document.getElementById("noFiltersMessage");
      if (noFiltersMsg) noFiltersMsg.style.display = "block";

      if (subItemsContainer) subItemsContainer.style.display = "block";
    } else {
      subcategorySelect.disabled = true;
      if (filtersSection) filtersSection.style.display = "none";

      if (subItemsContainer) subItemsContainer.style.display = "none";
    }
  });

  subcategorySelect.addEventListener("change", function () {
    const category = categorySelect.value;
    const subcategory = this.value;
    console.log(
      "[v0] Subcategory changed to:",
      subcategory,
      "Category:",
      category
    );

    if (category && subcategory) {
      loadFilters(category, subcategory);

      // Map subcategories to their actual HTML div IDs
      // The HTML has specific IDs that don't follow a simple pattern
      const subItemsDivMap = {
        Occasionwear: "occasionwear-items",
        "Slippers & Comfort Wear": "slippers-items",
        "Occasion / Dress Shoes": "dress-shoes-items",
        Others: "others-accessories-items",
      };

      // Check if this subcategory has a sub-items div
      const divId = subItemsDivMap[subcategory];

      if (divId) {
        // Show the sub-items container
        if (subItemsContainer) {
          subItemsContainer.style.display = "block";
        }

        // Hide all sub-items divs first
        document.querySelectorAll("[id$='-items']").forEach((el) => {
          el.style.display = "none";
        });

        // Show the matching sub-items div
        const subItemsDiv = document.getElementById(divId);
        console.log(
          "[v0] Looking for sub-items div:",
          divId,
          "Found:",
          !!subItemsDiv
        );
        if (subItemsDiv) {
          subItemsDiv.style.display = "block";
        }
      } else {
        // No sub-items div for this subcategory, hide container
        // If there are mapped subItems data for this subcategory, render them dynamically
        if (subItems && subItems[subcategory] && subItemsContainer) {
          renderSubItems(subcategory);
          subItemsContainer.style.display = "block";
        } else if (subItemsContainer) {
          subItemsContainer.style.display = "none";
        }
      }
    } else {
      if (filtersSection) filtersSection.style.display = "none";
      if (subItemsContainer) subItemsContainer.style.display = "none";
    }
  });
}

// Render sub-items dynamically into `subItemsContainer` when no hard-coded block exists
function renderSubItems(subcategory) {
  if (!subItemsContainer) return;
  const items = subItems[subcategory];
  if (!items || !items.length) {
    subItemsContainer.innerHTML = "";
    return;
  }

  // Build a simple grid of checkbox options
  const wrapper = document.createElement("div");
  wrapper.className = "sub-items-grid dynamic";

  items.forEach((labelText, idx) => {
    const opt = document.createElement("div");
    opt.className = "sub-item-option";

    const idSafe = `subitem-${subcategory}-${idx}`
      .toLowerCase()
      .replace(/[^a-z0-9\-]+/g, "-");
    const input = document.createElement("input");
    input.type = "checkbox";
    input.id = idSafe;
    input.name = "subitem";
    input.value = labelText;

    const label = document.createElement("label");
    label.htmlFor = idSafe;
    label.textContent = labelText;

    opt.appendChild(input);
    opt.appendChild(label);
    wrapper.appendChild(opt);
  });

  // Replace container contents but keep any header or structural wrappers
  // If the container already has existing child nodes for static content, remove them
  // and insert the dynamic wrapper
  subItemsContainer.innerHTML = "";
  subItemsContainer.appendChild(wrapper);
}

function loadFilters(category, subcategory) {
  console.log("[v0] Loading filters for:", category, subcategory);

  // Hide all filter sections first
  document.querySelectorAll(".filter-type-container").forEach((container) => {
    container.style.display = "none";
  });

  // Map subcategories to filter section IDs
  const filterSectionMap = {
    Tops: "topsFilters",
    Bottoms: "bottomsFilters",
    Dresses: "dressesFilters",
    Outerwear: "outerwearFilters",
    Activewear: "activewearFilters",
    Sleepwear: "sleepwearFilters",
    Undergarments: "undergarmentsFilters",
    Swimwear: "swimwearFilters",
    Occasionwear: "occasionwearFilters",
    Heels: "heelsFilters",
    Flats: "flatsFilters",
    Sandals: "sandalsSlidesFilters",
    Sneakers: "sneakersFilters",
    Boots: "bootsFilters",
    "Slippers & Comfort Wear": "comfortWearFilters",
    "Occasion / Dress Shoes": "occasionShoesFilters",
    Bags: "bagsFilters",
    Jewelry: "jewelryFilters",
    "Hair Accessories": "hairAccessoriesFilters",
    Belts: "beltFilters",
    "Scarves & Wraps": "scarvesFilters",
    "Hats & Caps": "hatsFilters",
    Eyewear: "eyewearFilters",
    Watches: "watchesFilters",
    Gloves: "glovesFilters",
    Others: "otherAccessoriesFilters",
  };

  // Show the correct filter section if mapping exists
  const filterSectionId = filterSectionMap[subcategory];

  const shoesSubcategories = [
    "Heels",
    "Flats",
    "Sandals",
    "Sneakers",
    "Boots",
    "Slippers & Comfort Wear",
    "Occasion / Dress Shoes",
  ];

  const accessoriesSubcategories = [
    "Bags",
    "Jewelry",
    "Hair Accessories",
    "Belts",
    "Scarves & Wraps",
    "Hats & Caps",
    "Eyewear",
    "Watches",
    "Gloves",
    "Others",
  ];

  if (shoesSubcategories.includes(subcategory)) {
    // Show parent shoesFilters
    const shoesParent = document.getElementById("shoesFilters");
    if (shoesParent) shoesParent.style.display = "block";
    // Hide all child filter sections inside shoesFilters
    shoesParent &&
      shoesParent
        .querySelectorAll(".filter-type-container")
        .forEach((child) => {
          child.style.display = "none";
        });
    // Show only the correct child
    if (filterSectionId) {
      const childSection = document.getElementById(filterSectionId);
      console.log(
        "[v0] Looking for filter section:",
        filterSectionId,
        "Found:",
        !!childSection
      );
      if (childSection) {
        childSection.style.display = "block";
        if (filtersSection) filtersSection.style.display = "block";
        const noFilters = document.getElementById("noFiltersMessage");
        if (noFilters) noFilters.style.display = "none";
        return;
      }
    }
  } else if (accessoriesSubcategories.includes(subcategory)) {
    // Show parent accessoriesFilters
    const accessoriesParent = document.getElementById("accessoriesFilters");
    if (accessoriesParent) accessoriesParent.style.display = "block";
    // Hide all child filter sections inside accessoriesFilters
    accessoriesParent &&
      accessoriesParent
        .querySelectorAll(".filter-type-container")
        .forEach((child) => {
          child.style.display = "none";
        });
    // Show only the correct child
    if (filterSectionId) {
      const childSection = document.getElementById(filterSectionId);
      console.log(
        "[v0] Looking for filter section:",
        filterSectionId,
        "Found:",
        !!childSection
      );
      if (childSection) {
        childSection.style.display = "block";
        if (filtersSection) filtersSection.style.display = "block";
        const noFilters = document.getElementById("noFiltersMessage");
        if (noFilters) noFilters.style.display = "none";
        return;
      }
    }
  } else if (filterSectionId) {
    const section = document.getElementById(filterSectionId);
    console.log(
      "[v0] Looking for filter section:",
      filterSectionId,
      "Found:",
      !!section
    );
    if (section) {
      section.style.display = "block";
      if (filtersSection) filtersSection.style.display = "block";
      const noFilters = document.getElementById("noFiltersMessage");
      if (noFilters) noFilters.style.display = "none";
      return;
    }
  }

  // If a prebuilt filter section wasn't found in the DOM, try to render
  // filters dynamically from the `filters` object defined above. This
  // provides a fallback so filters still appear even if the template only
  // includes a small subset of hard-coded filter sections (e.g. Activewear).
  if (filters[category] && filters[category][subcategory] && filtersContainer) {
    // Clear existing dynamic filters
    filtersContainer.innerHTML = "";

    const filterData = filters[category][subcategory];
    const wrapper = document.createElement("div");
    wrapper.className = "filter-parent-dynamic";

    Object.keys(filterData).forEach((filterName) => {
      const options = filterData[filterName];

      const group = document.createElement("div");
      group.className = "filter-group";

      const header = document.createElement("button");
      header.className = "filter-header";
      header.type = "button";
      const title = document.createElement("div");
      title.className = "filter-title";
      title.textContent = filterName;
      const caret = document.createElement("i");
      caret.className = "ri-arrow-down-s-line";
      header.appendChild(title);
      header.appendChild(caret);

      const content = document.createElement("div");
      content.className = "filter-content";
      content.style.display = "none";

      const optionsContainer = document.createElement("div");
      optionsContainer.className = "filter-options";

      options.forEach((opt, idx) => {
        const optionWrap = document.createElement("div");
        optionWrap.className = "filter-option";

        const input = document.createElement("input");
        input.type = "checkbox";
        // create a stable id from names
        const idSafe = (filterName + "-" + opt)
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, "-");
        input.id = idSafe + "-dyn-" + idx;
        input.name = filterName;
        input.value = opt;

        const label = document.createElement("label");
        label.htmlFor = input.id;
        label.textContent = opt;

        optionWrap.appendChild(input);
        optionWrap.appendChild(label);
        optionsContainer.appendChild(optionWrap);
      });

      content.appendChild(optionsContainer);
      group.appendChild(header);
      group.appendChild(content);

      // toggle behavior for dynamic header
      header.addEventListener("click", function () {
        content.style.display =
          content.style.display === "none" ? "block" : "none";
      });

      wrapper.appendChild(group);
    });

    filtersContainer.appendChild(wrapper);
    if (filtersSection) filtersSection.style.display = "block";
    const noFilters = document.getElementById("noFiltersMessage");
    if (noFilters) noFilters.style.display = "none";
    return;
  }

  // If no filter section for subcategory, show message
  if (filtersSection) filtersSection.style.display = "block";
  const noFilters = document.getElementById("noFiltersMessage");
  if (noFilters) noFilters.style.display = "block";
}

// Form Submission
function handleSubmit() {
  const formData = new FormData(document.getElementById("productForm"));

  // Collect all form data
  const productData = {
    productName: formData.get("productName"),
    price: formData.get("price"),
    category: formData.get("category"),
    subcategory: formData.get("subcategory"),
    subItems: formData.get("subItems"),
    modelHeight: formData.get("modelHeight"),
    wearingSize: formData.get("wearingSize"),
    description: formData.get("description"),
    materials: formData.get("materials"),
    detailsFit: formData.get("detailsFit"),
    certifications: Array.from(
      document.querySelectorAll('input[name="certifications"]:checked')
    ).map((cb) => cb.value),
    sku: formData.get("sku"),
    barcode: formData.get("barcode"),
    totalStock: formData.get("totalStock"),
    lowStockThreshold: formData.get("lowStockThreshold"),
    trackInventory: document.getElementById("trackInventory").checked,
    allowBackorder: document.getElementById("allowBackorder").checked,
    supplier: formData.get("supplier"),
    leadTime: formData.get("leadTime"),
    warehouseLocation: formData.get("warehouseLocation"),
    reorderPoint: formData.get("reorderPoint"),
  };

  console.log("Product Data:", productData);

  // Show success message
  alert(
    "Product added successfully!\n\nProduct: " +
      productData.productName +
      "\nPrice: $" +
      productData.price
  );

  // Reset form (optional)
  // document.getElementById('productForm').reset();
  // currentPage = 1;
  // updatePage();
}

// Validate required fields (except model information) before navigating to next page
window.validateAndRedirect = function (redirectUrl) {
  const form = document.getElementById("productForm");
  if (!form) {
    // fallback: navigate if no form found
    window.location.href = redirectUrl;
    return;
  }

  // Select inputs we want to require: text, number, email, file, textarea, select
  const selector =
    'input[type="text"], input[type="number"], input[type="email"], input[type="tel"], input[type="file"], textarea, select';
  const allControls = Array.from(form.querySelectorAll(selector));

  // IDs to skip (model information)
  const skipIds = [
    "modelHeight",
    "wearingSize",
    "discountPercentage",
    "discountType",
    "voucherType",
  ];

  // Filter out controls that are inside the right-hand filters panel (they're not part of the product form inputs)
  const filtered = allControls.filter((el) => {
    if (skipIds.includes(el.id)) return false;
    // skip hidden inputs or disabled fields
    if (el.disabled) return false;
    // skip elements not visible
    if (!(el.offsetParent !== null)) return false;
    // skip checkboxes/radios (filters) — we only require text/number/select/textarea/file
    if (el.type === "checkbox" || el.type === "radio") return false;
    return true;
  });

  // Temporarily set required on the filtered controls and run browser validation
  // Use the required attributes added by setupRequiredUI and show inline errors
  const valid = form.checkValidity();
  if (!valid) {
    // show custom inline messages for invalid fields
    const firstInvalid = filtered.find((el) => !el.checkValidity());
    filtered.forEach((el) => {
      const group = el.closest(".form-group");
      const err = group ? group.querySelector(".field-error") : null;
      if (!el.checkValidity()) {
        if (err) {
          // derive label text if possible
          let labelText = "";
          if (el.id) {
            const lbl = form.querySelector(`label[for="${el.id}"]`);
            if (lbl) labelText = lbl.textContent.replace("", "").trim();
          }
          err.textContent = labelText
            ? `Please input ${labelText}`
            : "Please input this field";
          err.style.display = "block";
        }
        el.classList.add("invalid-field");
      } else {
        if (err) err.style.display = "none";
        el.classList.remove("invalid-field");
      }
    });

    if (firstInvalid) {
      // focus and scroll to first invalid
      firstInvalid.focus();
      firstInvalid.scrollIntoView({ behavior: "smooth", block: "center" });
    }
    return;
  }

  // clear any existing inline errors before navigating
  filtered.forEach((el) => {
    const group = el.closest(".form-group");
    const err = group ? group.querySelector(".field-error") : null;
    if (err) err.style.display = "none";
    el.classList.remove("invalid-field");
  });

  // If valid, navigate
  window.location.href = redirectUrl;
};
