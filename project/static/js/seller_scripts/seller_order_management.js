document.addEventListener("DOMContentLoaded", function () {
  if (window.lucide && typeof lucide.createIcons === "function") {
    lucide.createIcons();
  }

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

  const searchInput = document.getElementById("orderSearch");
  const dateFrom = document.getElementById("dateFrom");
  const dateTo = document.getElementById("dateTo");
  const sortBy = document.getElementById("sortBy");
  const statusFilter = document.getElementById("statusFilter");

  const STATUS_BUCKETS = {
    pending: (status) => ["pending", "confirmed"].includes(status),
    shipped: (status) => status === "shipping",
    "in-transit": (status) => status === "in_transit",
    cancelled: (status) => status === "cancelled",
    completed: (status) => ["delivered", "completed"].includes(status),
  };

  function matchesBucket(bucketKey, statusValue) {
    if (!bucketKey || bucketKey === "all") return true;
    const matcher = STATUS_BUCKETS[bucketKey];
    return matcher ? matcher(statusValue) : statusValue === bucketKey;
  }

  function filterOrders() {
    const searchTerm = searchInput?.value?.toLowerCase() || "";
    const activeTab = document.querySelector(
      ".order-management-header .nav-tab.active"
    );
    const selectedStatus = activeTab?.dataset?.status || "all";
    const fromDate = dateFrom?.value ? new Date(dateFrom.value) : null;
    const toDate = dateTo?.value ? new Date(dateTo.value) : null;
    const statusValue = statusFilter?.value || "";

    const orderCards = document.querySelectorAll(
      ".orders-container .order-card"
    );
    orderCards.forEach((card) => {
      const orderStatus = (card.dataset.status || "").toLowerCase();
      const orderText = card.textContent.toLowerCase();
      const orderDateStr =
        card.querySelector(".order-date strong")?.textContent?.trim() || "";
      let orderDate = orderDateStr ? new Date(orderDateStr) : null;
      if (orderDate && isNaN(orderDate)) orderDate = null;

      let visible = true;
      if (searchTerm && !orderText.includes(searchTerm)) visible = false;
      if (!matchesBucket(selectedStatus, orderStatus)) visible = false;
      if (statusValue && !matchesBucket(statusValue, orderStatus))
        visible = false;
      if (fromDate && (!orderDate || orderDate < fromDate)) visible = false;
      if (toDate && (!orderDate || orderDate > toDate)) visible = false;
      card.style.display = visible ? "" : "none";
    });

    if (typeof sortBy?.value === "string" && sortBy.value) {
      sortOrderCards(sortBy.value);
    }
  }

  function sortOrderCards(sortValue) {
    const container = document.querySelector(".orders-container");
    if (!container || !sortValue) return;
    const cards = Array.from(container.querySelectorAll(".order-card"));

    const sorters = {
      "date-desc": (a, b) => getCardDate(b) - getCardDate(a),
      "date-asc": (a, b) => getCardDate(a) - getCardDate(b),
      "price-desc": (a, b) => getCardTotal(b) - getCardTotal(a),
      "price-asc": (a, b) => getCardTotal(a) - getCardTotal(b),
      "name-asc": (a, b) => getCardName(a).localeCompare(getCardName(b)),
      "name-desc": (a, b) => getCardName(b).localeCompare(getCardName(a)),
    };

    const sorter = sorters[sortValue];
    if (!sorter) return;

    cards.sort(sorter).forEach((card) => container.appendChild(card));
  }

  function getCardDate(card) {
    const text = card.querySelector(".order-date strong")?.textContent || "";
    const date = text ? new Date(text) : new Date(0);
    return isNaN(date) ? new Date(0) : date;
  }

  function getCardTotal(card) {
    const priceText = card.querySelector(".price")?.textContent || "0";
    const sanitized = priceText.replace(/[^0-9.]/g, "");
    return Number.parseFloat(sanitized) || 0;
  }

  function getCardName(card) {
    return (
      card.querySelector(".product-name")?.textContent?.trim().toLowerCase() ||
      ""
    );
  }

  searchInput?.addEventListener("input", filterOrders);
  sortBy?.addEventListener("change", filterOrders);
  dateFrom?.addEventListener("change", filterOrders);
  dateTo?.addEventListener("change", filterOrders);
  statusFilter?.addEventListener("change", filterOrders);

  document.addEventListener("orderStatusUpdated", () => {
    filterOrders();
  });

  filterOrders();
});
