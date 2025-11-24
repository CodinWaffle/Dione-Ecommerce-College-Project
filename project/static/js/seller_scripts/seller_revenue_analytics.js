// Sample data generation and dashboard logic
const generateSampleData = () => {
  const transactions = [];
  const products = [
    "Wireless Headphones",
    "Smart Watch",
    "Laptop Stand",
    "USB-C Cable",
    "Phone Case",
    "Bluetooth Speaker",
    "Keyboard",
    "Mouse Pad",
    "Webcam",
    "Monitor",
  ];
  const statuses = ["completed", "pending", "cancelled"];

  for (let i = 0; i < 50; i++) {
    const grossRevenue = Math.floor(Math.random() * 5000) + 500;
    const platformFee = grossRevenue * 0.15; // 15% commission
    const voucherAmount =
      Math.random() > 0.6 ? Math.floor(Math.random() * 500) : 0;
    const netEarnings = grossRevenue - platformFee - voucherAmount;

    const date = new Date();
    date.setDate(date.getDate() - Math.floor(Math.random() * 30));

    transactions.push({
      date: date.toISOString().split("T")[0],
      orderId: `ORD-${String(10000 + i).padStart(5, "0")}`,
      product: products[Math.floor(Math.random() * products.length)],
      grossRevenue: grossRevenue,
      platformFee: platformFee,
      voucher: voucherAmount,
      netEarnings: netEarnings,
      status: statuses[Math.floor(Math.random() * statuses.length)],
    });
  }

  return transactions.sort((a, b) => new Date(b.date) - new Date(a.date));
};

// Format currency
const formatCurrency = (amount) => {
  return new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
    minimumFractionDigits: 2,
  }).format(amount);
};

// Calculate summary statistics
const calculateSummary = (transactions) => {
  const totalRevenue = transactions.reduce((sum, t) => sum + t.grossRevenue, 0);
  const totalCommission = transactions.reduce(
    (sum, t) => sum + t.platformFee,
    0
  );
  const totalVouchers = transactions.reduce((sum, t) => sum + t.voucher, 0);
  const netEarnings = totalRevenue - totalCommission - totalVouchers;
  const voucherCount = transactions.filter((t) => t.voucher > 0).length;

  return {
    totalRevenue,
    totalCommission,
    totalVouchers,
    netEarnings,
    voucherCount,
    commissionRate: 15,
  };
};

// Update summary cards
const updateSummaryCards = (summary) => {
  document.getElementById("totalRevenue").textContent = formatCurrency(
    summary.totalRevenue
  );
  document.getElementById("platformCommission").textContent = formatCurrency(
    summary.totalCommission
  );
  document.getElementById("voucherDeductions").textContent = formatCurrency(
    summary.totalVouchers
  );
  document.getElementById("netEarnings").textContent = formatCurrency(
    summary.netEarnings
  );
  document.getElementById("voucherCount").textContent = summary.voucherCount;
  document.getElementById(
    "commissionRate"
  ).textContent = `${summary.commissionRate}%`;

  // Random percentage changes for demo
  document.getElementById("revenueChange").textContent = `${(
    Math.random() * 20 +
    5
  ).toFixed(1)}%`;
  document.getElementById("earningsChange").textContent = `${(
    Math.random() * 15 +
    3
  ).toFixed(1)}%`;
};

// Chart.js implementation for revenue breakdown chart
let revenueChartInstance = null;
const createRevenueChart = (transactions) => {
  const canvas = document.getElementById("revenueChart");
  // REMOVE manual canvas.width/height for Chart.js responsive fix
  const ctx = canvas.getContext("2d");
  // Group by date
  const dateGroups = {};
  transactions.forEach((t) => {
    if (!dateGroups[t.date]) {
      dateGroups[t.date] = {
        gross: 0,
        fee: 0,
        voucher: 0,
        net: 0,
      };
    }
    dateGroups[t.date].gross += t.grossRevenue;
    dateGroups[t.date].fee += t.platformFee;
    dateGroups[t.date].voucher += t.voucher;
    dateGroups[t.date].net += t.netEarnings;
  });
  const dates = Object.keys(dateGroups).sort().slice(-7);
  const gross = dates.map((date) => dateGroups[date].gross);
  const fee = dates.map((date) => dateGroups[date].fee);
  const voucher = dates.map((date) => dateGroups[date].voucher);
  const net = dates.map((date) => dateGroups[date].net);

  if (revenueChartInstance) revenueChartInstance.destroy();
  revenueChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: dates.map((d) =>
        new Date(d).toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
        })
      ),
      datasets: [
        {
          label: "Gross Revenue",
          data: gross,
          borderColor: "#3b82f6",
          backgroundColor: "#3b82f6",
          fill: false,
          tension: 0.3,
        },
        {
          label: "Platform Fee",
          data: fee,
          borderColor: "#ef4444",
          backgroundColor: "#ef4444",
          fill: false,
          tension: 0.3,
        },
        {
          label: "Voucher Cost",
          data: voucher,
          borderColor: "#f59e0b",
          backgroundColor: "#f59e0b",
          fill: false,
          tension: 0.3,
        },
        {
          label: "Net Earnings",
          data: net,
          borderColor: "#10b981",
          backgroundColor: "#10b981",
          fill: false,
          tension: 0.3,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: { mode: "index", intersect: false },
      },
      interaction: { mode: "nearest", axis: "x", intersect: false },
      scales: {
        x: { display: true, title: { display: false } },
        y: { display: true, title: { display: false } },
      },
    },
  });
};

// Chart.js implementation for earnings trend chart
let trendChartInstance = null;
const createTrendChart = (transactions) => {
  const canvas = document.getElementById("trendChart");
  // REMOVE manual canvas.width/height for Chart.js responsive fix
  const ctx = canvas.getContext("2d");
  // Group by date
  const dateGroups = {};
  transactions.forEach((t) => {
    if (!dateGroups[t.date]) {
      dateGroups[t.date] = 0;
    }
    dateGroups[t.date] += t.netEarnings;
  });
  const dates = Object.keys(dateGroups).sort().slice(-7);
  const earnings = dates.map((date) => dateGroups[date]);

  if (trendChartInstance) trendChartInstance.destroy();
  trendChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: dates.map((d) =>
        new Date(d).toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
        })
      ),
      datasets: [
        {
          label: "Net Earnings",
          data: earnings,
          borderColor: "#3b82f6",
          backgroundColor: "rgba(59,130,246,0.3)",
          fill: true,
          tension: 0.3,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: { mode: "index", intersect: false },
      },
      interaction: { mode: "nearest", axis: "x", intersect: false },
      scales: {
        x: { display: true, title: { display: false } },
        y: { display: true, title: { display: false } },
      },
    },
  });
};

// Populate transaction table
let currentPage = 1;
const itemsPerPage = 10;
let filteredTransactions = [];

const populateTable = (transactions, page = 1) => {
  const tbody = document.getElementById("transactionTable");
  const start = (page - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  const pageTransactions = transactions.slice(start, end);

  tbody.innerHTML = pageTransactions
    .map(
      (t) => `
        <tr>
            <td>${new Date(t.date).toLocaleDateString("en-US", {
              month: "short",
              day: "numeric",
              year: "numeric",
            })}</td>
            <td>${t.orderId}</td>
            <td>${t.product}</td>
            <td>${formatCurrency(t.grossRevenue)}</td>
            <td class="negative">${formatCurrency(t.platformFee)}</td>
            <td class="negative">${
              t.voucher > 0 ? formatCurrency(t.voucher) : "-"
            }</td>
            <td style="color: var(--accent-green); font-weight: 600;">${formatCurrency(
              t.netEarnings
            )}</td>
            <td><span class="status-badge ${t.status}">${
        t.status.charAt(0).toUpperCase() + t.status.slice(1)
      }</span></td>
        </tr>
    `
    )
    .join("");

  // Update pagination
  document.getElementById("showingCount").textContent = Math.min(
    end,
    transactions.length
  );
  document.getElementById("totalCount").textContent = transactions.length;

  updatePagination(transactions.length, page);
};

// Update pagination
const updatePagination = (totalItems, currentPage) => {
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const paginationNumbers = document.getElementById("paginationNumbers");

  paginationNumbers.innerHTML = "";

  for (let i = 1; i <= Math.min(totalPages, 5); i++) {
    const pageBtn = document.createElement("button");
    pageBtn.className = `page-number ${i === currentPage ? "active" : ""}`;
    pageBtn.textContent = i;
    pageBtn.addEventListener("click", () => {
      currentPage = i;
      populateTable(filteredTransactions, i);
    });
    paginationNumbers.appendChild(pageBtn);
  }

  document.getElementById("prevBtn").disabled = currentPage === 1;
  document.getElementById("nextBtn").disabled = currentPage === totalPages;
};

// Search functionality
const setupSearch = (transactions) => {
  const searchInput = document.getElementById("searchInput");

  searchInput.addEventListener("input", (e) => {
    const query = e.target.value.toLowerCase();
    filteredTransactions = transactions.filter(
      (t) =>
        t.orderId.toLowerCase().includes(query) ||
        t.product.toLowerCase().includes(query) ||
        t.status.toLowerCase().includes(query)
    );
    currentPage = 1;
    populateTable(filteredTransactions, currentPage);
  });
};

// Pagination buttons
// Enhanced pagination with numbered pages
const setupPagination = () => {
  const totalPages = Math.ceil(filteredTransactions.length / itemsPerPage);
  const paginationNumbers = document.getElementById("paginationNumbers");
  const prevBtn = document.getElementById("prevBtn");
  const nextBtn = document.getElementById("nextBtn");

  paginationNumbers.innerHTML = "";

  // Create page number buttons
  for (let i = 1; i <= totalPages; i++) {
    const pageNumber = document.createElement("span");
    pageNumber.classList.add("page-number");
    if (i === currentPage) {
      pageNumber.classList.add("active");
    }
    pageNumber.textContent = i;
    pageNumber.addEventListener("click", () => {
      currentPage = i;
      populateTable(filteredTransactions, currentPage);
      updatePaginationActive();
      updatePaginationButtons();
    });
    paginationNumbers.appendChild(pageNumber);
  }

  // Show up to 5 page numbers
  const updateVisiblePageNumbers = () => {
    const pageNumbers = paginationNumbers.querySelectorAll(".page-number");
    if (pageNumbers.length <= 5) return;

    pageNumbers.forEach((page, index) => {
      const pageNum = index + 1;
      // Show first, last, current and adjacent pages
      if (
        pageNum === 1 ||
        pageNum === totalPages ||
        (pageNum >= currentPage - 1 && pageNum <= currentPage + 1)
      ) {
        page.style.display = "block";
      } else if (pageNum === currentPage - 2 || pageNum === currentPage + 2) {
        page.textContent = "...";
        page.style.pointerEvents = "none";
        page.style.display = "block";
      } else {
        page.style.display = "none";
      }
    });
  };

  const updatePaginationActive = () => {
    const pageNumbers = document.querySelectorAll(".page-number");
    pageNumbers.forEach((page, index) => {
      if (index + 1 === currentPage) {
        page.classList.add("active");
      } else {
        page.classList.remove("active");
      }
    });
  };

  const updatePaginationButtons = () => {
    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage === totalPages;

    updateVisiblePageNumbers();
  };

  prevBtn.addEventListener("click", () => {
    if (currentPage > 1) {
      currentPage--;
      populateTable(filteredTransactions, currentPage);
      updatePaginationActive();
      updatePaginationButtons();
    }
  });

  nextBtn.addEventListener("click", () => {
    if (currentPage < totalPages) {
      currentPage++;
      populateTable(filteredTransactions, currentPage);
      updatePaginationActive();
      updatePaginationButtons();
    }
  });

  updatePaginationButtons();
};

// Export functionality
const setupExport = (transactions) => {
  document.querySelector(".export-btn").addEventListener("click", () => {
    const csv = [
      [
        "Date",
        "Order ID",
        "Product",
        "Gross Revenue",
        "Platform Fee",
        "Voucher",
        "Net Earnings",
        "Status",
      ],
      ...transactions.map((t) => [
        t.date,
        t.orderId,
        t.product,
        t.grossRevenue,
        t.platformFee,
        t.voucher,
        t.netEarnings,
        t.status,
      ]),
    ]
      .map((row) => row.join(","))
      .join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "revenue-analytics.csv";
    a.click();
  });
};

// Setup date range filtering
const setupDateFilter = (transactions) => {
  const startDateInput = document.getElementById("startDate");
  const endDateInput = document.getElementById("endDate");

  // Set default date values (current month)
  const today = new Date();
  const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);

  startDateInput.valueAsDate = firstDay;
  endDateInput.valueAsDate = today;

  const handleDateFilter = () => {
    const startDate = startDateInput.valueAsDate;
    const endDate = endDateInput.valueAsDate;

    if (startDate && endDate) {
      // Add a day to include the end date fully
      const adjustedEndDate = new Date(endDate);
      adjustedEndDate.setDate(adjustedEndDate.getDate() + 1);

      const filtered = transactions.filter((t) => {
        const transactionDate = new Date(t.date);
        return (
          transactionDate >= startDate && transactionDate < adjustedEndDate
        );
      });

      filteredTransactions = filtered;
      currentPage = 1;
      populateTable(filtered, currentPage);
      setupPagination();
    }
  };

  startDateInput.addEventListener("change", handleDateFilter);
  endDateInput.addEventListener("change", handleDateFilter);

  // Initial filtering
  handleDateFilter();
};

// Initialize dashboard
const init = () => {
  const transactions = generateSampleData();
  filteredTransactions = transactions;

  const summary = calculateSummary(transactions);
  updateSummaryCards(summary);

  createRevenueChart(transactions);
  createTrendChart(transactions);

  setupDateFilter(transactions);
  populateTable(filteredTransactions, currentPage);
  setupSearch(transactions);
  setupPagination();
  setupExport(transactions);

  // Filter change handlers
  document.getElementById("breakdownFilter").addEventListener("change", () => {
    createRevenueChart(transactions);
  });

  document.getElementById("trendFilter").addEventListener("change", () => {
    createTrendChart(transactions);
  });
};

// Start the dashboard
init();
