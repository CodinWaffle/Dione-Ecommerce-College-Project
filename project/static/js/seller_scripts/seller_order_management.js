document.addEventListener("DOMContentLoaded", function () {
  // Initialize Lucide icons
  if (window.lucide && typeof lucide.createIcons === "function") {
    lucide.createIcons();
  }

  // Tab navigation (nav-tabs inside .order-management-header)
  const navTabs = document.querySelectorAll(
    ".order-management-header .nav-tab"
  );
  navTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      document
        .querySelector(".order-management-header .nav-tab.active")
        ?.classList.remove("active");
      tab.classList.add("active");
      filterOrders();
    });
  });

  // Filter elements
  const searchInput = document.getElementById("orderSearch");
  const dateFrom = document.getElementById("dateFrom");
  const dateTo = document.getElementById("dateTo");
  const sortBy = document.getElementById("sortBy");
  const statusFilter = document.getElementById("statusFilter");

  function filterOrders() {
    const searchTerm = searchInput?.value?.toLowerCase() || "";
    const selectedStatus =
      document.querySelector(".order-management-header .nav-tab.active")
        ?.dataset?.status || "all";
    const fromDate = new Date(dateFrom.value);
    const toDate = new Date(dateTo.value);
    const statusValue = statusFilter?.value || "";
    const sortValue = sortBy?.value || "";

    const orderCards = document.querySelectorAll(
      ".orders-container .order-card"
    );
    orderCards.forEach((card) => {
      const orderText = card.textContent.toLowerCase();
      const orderStatus =
        card.querySelector(".status-badge")?.textContent?.toLowerCase() || "";
      const orderDateStr =
        card.querySelector(".order-date strong")?.textContent || "";
      let orderDate = new Date(orderDateStr);
      if (isNaN(orderDate)) orderDate = new Date(); // fallback
      let visible = true;
      if (searchTerm && !orderText.includes(searchTerm)) visible = false;
      if (selectedStatus !== "all" && orderStatus !== selectedStatus)
        visible = false;
      if (statusValue && orderStatus !== statusValue) visible = false;
      if (orderDate < fromDate || orderDate > toDate) visible = false;
      card.style.display = visible ? "" : "none";
    });
    // Optionally: sort order cards here
  }

  searchInput?.addEventListener("input", filterOrders);
  sortBy?.addEventListener("change", filterOrders);
  dateFrom?.addEventListener("change", filterOrders);
  dateTo?.addEventListener("change", filterOrders);
  statusFilter?.addEventListener("change", filterOrders);

  // Initial filter
  filterOrders();
});
