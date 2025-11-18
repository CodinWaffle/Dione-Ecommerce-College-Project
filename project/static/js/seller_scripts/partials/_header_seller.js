document.addEventListener("DOMContentLoaded", function () {
  // Initialize lucide icons (if available)
  try {
    if (window.lucide && typeof lucide.createIcons === "function") {
      lucide.createIcons();
    }
  } catch (e) {
    // ignore
  }

  // User profile dropdown functionality
  const dropdownWrap = document.querySelector(".user-profile-dropdown");
  const toggle = document.querySelector(".user-profile-toggle");
  const menu = document.querySelector(".user-dropdown-menu");

  function closeMenu() {
    if (menu) {
      menu.classList.remove("active");
      menu.setAttribute("aria-hidden", "true");
    }
  }

  if (toggle && menu) {
    toggle.addEventListener("click", function (e) {
      e.stopPropagation();
      menu.classList.toggle("active");
      const isActive = menu.classList.contains("active");
      menu.setAttribute("aria-hidden", isActive ? "false" : "true");
    });
  }

  // Close dropdown when clicking outside
  document.addEventListener("click", function (event) {
    if (menu && menu.classList.contains("active")) {
      if (!menu.contains(event.target) && !toggle.contains(event.target)) {
        closeMenu();
      }
    }
  });
});
