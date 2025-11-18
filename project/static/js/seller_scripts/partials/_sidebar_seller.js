document.addEventListener("DOMContentLoaded", function () {
  // Initialize lucide icons
  try {
    if (window.lucide && typeof lucide.createIcons === "function") {
      lucide.createIcons();
    }
  } catch (e) {
    console.warn("Lucide icons not loaded");
  }

  // Sidebar toggle functionality
  const sidebar = document.getElementById("sidebar");
  const sidebarToggle = document.getElementById("sidebarToggle");
  const mainContent = document.querySelector(".main-content");

  if (sidebarToggle) {
    sidebarToggle.addEventListener("click", function () {
      sidebar.classList.toggle("collapsed");
      if (mainContent) {
        mainContent.classList.toggle("expanded");
      }
    });
  }

  // Handle dropdown toggles
  const dropdownToggles = document.querySelectorAll(".dropdown-toggle");

  dropdownToggles.forEach((toggle) => {
    toggle.addEventListener("click", function (e) {
      e.preventDefault();
      const dropdownMenu = this.nextElementSibling;

      // Toggle active state
      this.classList.toggle("active");

      // Toggle dropdown menu visibility
      if (dropdownMenu && dropdownMenu.classList.contains("dropdown-menu")) {
        dropdownMenu.classList.toggle("show");
      }
    });
  });

  // Handle navigation
  const navItems = document.querySelectorAll(".nav-item[data-page]");

  navItems.forEach((item) => {
    item.addEventListener("click", function (e) {
      // Remove active class from all nav items
      navItems.forEach((nav) => nav.classList.remove("active"));

      // Add active class to clicked item
      this.classList.add("active");

      // Handle dropdown parent active state
      const parentDropdown = this.closest(".dropdown-menu");
      if (parentDropdown) {
        const dropdownToggle = parentDropdown.previousElementSibling;
        if (dropdownToggle) {
          dropdownToggle.classList.add("active");
        }
      }
    });
  });

  // Handle dropdown items
  const dropdownItems = document.querySelectorAll(".dropdown-item[data-page]");

  dropdownItems.forEach((item) => {
    item.addEventListener("click", function (e) {
      // Remove active from all dropdown items in this menu
      const parentMenu = this.closest(".dropdown-menu");
      if (parentMenu) {
        parentMenu
          .querySelectorAll(".dropdown-item")
          .forEach((di) => di.classList.remove("active"));
      }

      // Add active to clicked item
      this.classList.add("active");
    });
  });

  // Close sidebar on mobile when clicking outside
  document.addEventListener("click", function (event) {
    if (window.innerWidth <= 768) {
      const isClickInsideSidebar = sidebar.contains(event.target);
      const isClickOnToggle =
        sidebarToggle && sidebarToggle.contains(event.target);

      if (!isClickInsideSidebar && !isClickOnToggle) {
        sidebar.classList.remove("show");
      }
    }
  });

  // Responsive handling
  function handleResize() {
    if (window.innerWidth > 768) {
      sidebar.classList.remove("show");
    }
  }

  window.addEventListener("resize", handleResize);
});
