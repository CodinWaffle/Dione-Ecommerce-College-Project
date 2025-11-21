// Account Settings Dropdown Handler
document.addEventListener("DOMContentLoaded", function () {
  const dropdownBtn = document.getElementById("accountDropdownBtn");
  const dropdownMenu = document.getElementById("accountDropdown");
  const dropdownItems = document.querySelectorAll(".dropdown-item");
  const dropdownLabel = document.getElementById("dropdownLabel");

  if (!dropdownBtn || !dropdownMenu) return;

  // Toggle dropdown visibility
  dropdownBtn.addEventListener("click", function (e) {
    e.stopPropagation();
    dropdownBtn.classList.toggle("open");
    dropdownMenu.classList.toggle("show");
  });

  // Handle section switching
  dropdownItems.forEach((item) => {
    item.addEventListener("click", function (e) {
      e.preventDefault();
      const sectionId = this.getAttribute("data-section");

      // Only switch sections if on my_account page
      const isMyAccountPage = window.location.pathname.includes("/my-account");

      if (isMyAccountPage) {
        // Remove active class from all items
        dropdownItems.forEach((i) => i.classList.remove("active"));

        // Add active class to clicked item
        this.classList.add("active");

        // Update dropdown label
        const labelText = this.querySelector("span").textContent;
        dropdownLabel.textContent = labelText;

        // Close dropdown
        dropdownBtn.classList.remove("open");
        dropdownMenu.classList.remove("show");

        // Hide all sections
        const sections = document.querySelectorAll(".account-section");
        sections.forEach((section) => {
          section.style.display = "none";
        });

        // Show selected section
        const selectedSection = document.getElementById(`${sectionId}-section`);
        if (selectedSection) {
          selectedSection.style.display = "block";
        }

        // Scroll to content
        const mainContent = document.querySelector(".main-content");
        if (mainContent) {
          mainContent.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      }
    });
  });

  // Close dropdown when clicking outside
  document.addEventListener("click", function (e) {
    if (!e.target.closest(".account-dropdown-container")) {
      dropdownBtn.classList.remove("open");
      dropdownMenu.classList.remove("show");
    }
  });

  // Set initial active section to Profile on my_account page
  if (window.location.pathname.includes("/my-account")) {
    const profileSection = document.getElementById("profile-section");
    const addressesSection = document.getElementById("addresses-section");
    const notificationsSection = document.getElementById(
      "notifications-section"
    );

    if (profileSection) {
      profileSection.style.display = "block";
    }
    if (addressesSection) {
      addressesSection.style.display = "none";
    }
    if (notificationsSection) {
      notificationsSection.style.display = "none";
    }
  }
});
