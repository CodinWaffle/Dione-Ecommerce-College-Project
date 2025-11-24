document.addEventListener("DOMContentLoaded", function () {
  // Add transition class to main content area
  const mainContent = document.querySelector(".content-wrapper");
  if (mainContent) {
    mainContent.classList.add("content-wrapper");
  }

  // Add click handlers to all sidebar navigation links
  const sidebarLinks = document.querySelectorAll(".sidebar a[href]");
  sidebarLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      // Only handle internal links
      if (this.href.startsWith(window.location.origin)) {
        e.preventDefault();
        const mainContent = document.querySelector(".content-wrapper");

        // Start transition out
        mainContent.classList.add("loading");

        // Navigate after animation
        setTimeout(() => {
          window.location.href = this.href;
        }, 300);
      }
    });
  });

  // Remove loading class when page loads
  window.addEventListener("load", function () {
    const mainContent = document.querySelector(".content-wrapper");
    if (mainContent) {
      mainContent.classList.remove("loading");
    }
  });
});
