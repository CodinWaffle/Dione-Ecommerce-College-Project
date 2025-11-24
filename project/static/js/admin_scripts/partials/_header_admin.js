document.addEventListener("DOMContentLoaded", function () {
  // Initialize lucide icons (if available)
  try {
    if (window.lucide && typeof lucide.createIcons === "function") {
      lucide.createIcons();
    }
  } catch (e) {
    // ignore
  }

  // Scope selectors to the admin header to avoid interfering with other headers
  const dropdownWrap = document.querySelector(
    ".admin-header .user-profile-dropdown"
  );
  const toggle = document.querySelector(".admin-header .user-profile-toggle");
  const menu = document.querySelector(".admin-header .user-dropdown-menu");

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

  // Close dropdown when clicking outside (scoped)
  document.addEventListener("click", function (event) {
    if (menu && menu.classList.contains("active")) {
      if (
        !menu.contains(event.target) &&
        !(toggle && toggle.contains(event.target))
      ) {
        closeMenu();
      }
    }
  });
});
