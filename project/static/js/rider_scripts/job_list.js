// Rider Job List Page JS

document.addEventListener("DOMContentLoaded", function () {
  // Filter buttons
  const filterBtns = document.querySelectorAll(".filter-btn");
  filterBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      filterBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const filter = btn.getAttribute("data-filter");
      filterJobs(filter);
    });
  });

  // Search input
  const searchInput = document.getElementById("jobSearchInput");
  if (searchInput) {
    searchInput.addEventListener("input", function () {
      searchJobs(searchInput.value);
    });
  }
});

function filterJobs(filter) {
  if (searchInput && searchInput.value) {
    // Ensure searchInput exists before accessing .value
    searchInput.value = "";
  }

  const rows = document.querySelectorAll("#jobTableBody tr");
  rows.forEach((row) => {
    const statusCell = row.querySelector(".status-badge");
    if (!statusCell) return;
    const status = statusCell.textContent.trim().toLowerCase();
    if (filter === "today") {
      row.style.display = "";
    } else if (filter === "completed") {
      row.style.display = status === "delivered" ? "" : "none";
    } else if (filter === "cancelled") {
      row.style.display = status === "cancelled" ? "" : "none";
    } else {
      row.style.display = "";
    }
  });
}

function searchJobs(query) {
  query = query.trim().toLowerCase();
  const rows = document.querySelectorAll("#jobTableBody tr");
  const activeFilter = document
    .querySelector(".filter-btn.active")
    .getAttribute("data-filter");

  rows.forEach((row) => {
    // Check if the row is visible according to the current filter
    const status = row
      .querySelector(".status-badge")
      .textContent.trim()
      .toLowerCase();
    let isVisibleByFilter =
      activeFilter === "today" ||
      (activeFilter === "completed" && status === "delivered") ||
      (activeFilter === "cancelled" && status === "cancelled");

    const cells = row.querySelectorAll("td");
    let match = false;
    cells.forEach((cell) => {
      if (cell.textContent.toLowerCase().includes(query)) {
        match = true;
      }
    });
    row.style.display = isVisibleByFilter && match ? "" : "none";
  });
}
