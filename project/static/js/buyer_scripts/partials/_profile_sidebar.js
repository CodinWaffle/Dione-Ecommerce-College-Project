// Profile Sidebar JavaScript
document.addEventListener("DOMContentLoaded", () => {
  const expandableItems = document.querySelectorAll(".nav-item.expandable");
  const subItems = document.querySelectorAll(".sub-item");

  /* ---------------------------------------------------
     1. DROPDOWN MENU (My Account expandable)
  --------------------------------------------------- */
  expandableItems.forEach((item) => {
    item.addEventListener("click", function (e) {
      // Prevent submenu click from collapsing menu
      if (e.target.classList.contains("sub-item")) return;

      e.preventDefault();
      this.classList.toggle("expanded");

      const subMenu = this.nextElementSibling;
      if (subMenu && subMenu.classList.contains("sub-menu")) {
        subMenu.classList.toggle("open");
      }
    });
  });

  /* ---------------------------------------------------
     2. SWITCH SECTIONS (Profile / Addresses / Notifications / Privacy)
  --------------------------------------------------- */
  subItems.forEach((item) => {
    item.addEventListener("click", function (e) {
      e.preventDefault();

      const section = this.dataset.section;
      if (!section) return;

      // Remove active on all and set it on clicked one
      subItems.forEach((i) => i.classList.remove("active"));
      this.classList.add("active");

      showSection(section);
    });
  });

  /* ---------------------------------------------------
     3. FUNCTION – SHOW THE SELECTED SECTION
  --------------------------------------------------- */
  function showSection(name) {
    const allSections = document.querySelectorAll(".account-section");
    allSections.forEach((sec) => (sec.style.display = "none"));

    const target = document.getElementById(`${name}-section`);
    if (target) target.style.display = "block";
  }

  /* ---------------------------------------------------
     4. INITIALIZATION – Default section = Profile
  --------------------------------------------------- */
  const currentPath = window.location.pathname;

  // If user is on any account-related page, open dropdown
  if (
    currentPath.includes("my_account") ||
    currentPath.includes("addresses") ||
    currentPath.includes("notifications")
  ) {
    const accountItem = document.querySelector(".nav-item.expandable");
    const submenu = document.querySelector(".sub-menu");

    if (accountItem && submenu) {
      accountItem.classList.add("expanded");
      submenu.classList.add("open");
    }
  }

  // Default visible section
  showSection("profile");

  // Default active menu item
  const defaultItem = document.querySelector(
    '.sub-item[data-section="profile"]'
  );
  if (defaultItem) defaultItem.classList.add("active");
});

/* ---------------------------------------------------
   5. OPTIONAL: Toggle menu via icon/button
--------------------------------------------------- */
function toggleMenu(event) {
  if (event) event.preventDefault();

  const expandable = event.target.closest(".nav-item.expandable");
  if (!expandable) return;

  expandable.classList.toggle("expanded");

  const subMenu = expandable.nextElementSibling;
  if (subMenu && subMenu.classList.contains("sub-menu")) {
    subMenu.classList.toggle("open");
  }
}
