// Seller Customer Management JavaScript

document.addEventListener("DOMContentLoaded", function () {
  // Sample customer data - in a real app, this would come from the server
  const customerData = generateSampleCustomers();
  const customerOrders = generateSampleOrders();
  const customerActivity = generateSampleActivity();
  const customerNotes = generateSampleNotes();

  let currentPage = 1;
  const itemsPerPage = 10;
  let filteredCustomers = [...customerData];

  // Initialize everything
  initializePage();

  // Main initialization function
  function initializePage() {
    // Initialize stats
    updateCustomerStats();

    // Initialize charts
    createCustomerGrowthChart();
    createCustomerSegmentsChart();

    // Initialize customer table
    updateCustomerTable();

    // Initialize pagination
    setupPagination();
    updatePaginationInfo();

    // Setup search functionality
    document
      .getElementById("customerSearch")
      .addEventListener("input", function () {
        searchCustomers(this.value);
      });

    // Setup filter functionality
    document
      .getElementById("customerFilter")
      .addEventListener("change", function () {
        filterCustomers(this.value);
      });

    // Setup export functionality
    document
      .getElementById("exportCustomersBtn")
      .addEventListener("click", exportCustomerData);

    // Setup customer detail modal
    setupCustomerDetailModal();

    // Setup tabs in modal
    setupModalTabs();
  }

  // Generate sample customer data
  function generateSampleCustomers() {
    const customers = [];
    const statuses = ["active", "inactive", "new"];
    const firstNames = [
      "John",
      "Jane",
      "Michael",
      "Sarah",
      "David",
      "Emma",
      "Robert",
      "Lisa",
      "Daniel",
      "Olivia",
    ];
    const lastNames = [
      "Smith",
      "Johnson",
      "Williams",
      "Jones",
      "Brown",
      "Davis",
      "Miller",
      "Wilson",
      "Moore",
      "Taylor",
    ];

    for (let i = 1; i <= 50; i++) {
      const firstName =
        firstNames[Math.floor(Math.random() * firstNames.length)];
      const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
      const name = `${firstName} ${lastName}`;
      const email = `${firstName.toLowerCase()}.${lastName.toLowerCase()}@example.com`;
      const status = statuses[Math.floor(Math.random() * statuses.length)];
      const orders = Math.floor(Math.random() * 10) + 1;
      const totalSpent = (Math.random() * 1000 + 500).toFixed(2);
      const lastOrder = new Date(2025, 9, Math.floor(Math.random() * 15) + 1);
      const joinDate = new Date(
        2025,
        Math.floor(Math.random() * 10),
        Math.floor(Math.random() * 28) + 1
      );

      customers.push({
        id: `CUST-${String(i).padStart(5, "0")}`,
        name,
        email,
        status,
        orders,
        totalSpent,
        lastOrder,
        joinDate,
        avatar: firstName[0] + lastName[0],
      });
    }

    return customers;
  }

  // Generate sample order data
  function generateSampleOrders() {
    const orderMap = {};
    const productNames = [
      "T-Shirt",
      "Jeans",
      "Dress",
      "Sweater",
      "Jacket",
      "Skirt",
      "Blouse",
      "Shorts",
      "Pants",
      "Hoodie",
    ];

    customerData.forEach((customer) => {
      const orders = [];
      const orderCount = Math.floor(Math.random() * 5) + 1;

      for (let i = 1; i <= orderCount; i++) {
        const itemCount = Math.floor(Math.random() * 3) + 1;
        const items = [];

        for (let j = 0; j < itemCount; j++) {
          items.push(
            productNames[Math.floor(Math.random() * productNames.length)]
          );
        }

        const total = (Math.random() * 200 + 50).toFixed(2);
        const date = new Date(2025, 9, Math.floor(Math.random() * 30) + 1);
        const status = ["completed", "shipped", "processing", "cancelled"][
          Math.floor(Math.random() * 4)
        ];

        orders.push({
          id: `ORD-${String(Math.floor(Math.random() * 100000)).padStart(
            6,
            "0"
          )}`,
          date,
          items,
          total,
          status,
        });
      }

      orderMap[customer.id] = orders.sort((a, b) => b.date - a.date);
    });

    return orderMap;
  }

  // Generate sample activity data
  function generateSampleActivity() {
    const activityMap = {};
    const activityTypes = [
      "order",
      "login",
      "cart",
      "wishlist",
      "review",
      "return",
    ];

    customerData.forEach((customer) => {
      const activities = [];
      const activityCount = Math.floor(Math.random() * 8) + 2;

      for (let i = 1; i <= activityCount; i++) {
        const type =
          activityTypes[Math.floor(Math.random() * activityTypes.length)];
        const date = new Date(
          2025,
          9,
          Math.floor(Math.random() * 30) + 1,
          Math.floor(Math.random() * 24),
          Math.floor(Math.random() * 60)
        );

        let description;

        switch (type) {
          case "order":
            description = `Placed an order for ${
              Math.floor(Math.random() * 5) + 1
            } items`;
            break;
          case "login":
            description = "Logged in to account";
            break;
          case "cart":
            description = "Added items to cart";
            break;
          case "wishlist":
            description = "Added an item to wishlist";
            break;
          case "review":
            description = "Left a product review";
            break;
          case "return":
            description = "Requested a return";
            break;
        }

        activities.push({
          type,
          date,
          description,
        });
      }

      activityMap[customer.id] = activities.sort((a, b) => b.date - a.date);
    });

    return activityMap;
  }

  // Generate sample notes
  function generateSampleNotes() {
    const notesMap = {};

    customerData.forEach((customer) => {
      const hasNotes = Math.random() > 0.7;

      if (hasNotes) {
        const noteCount = Math.floor(Math.random() * 3) + 1;
        const notes = [];

        for (let i = 1; i <= noteCount; i++) {
          const date = new Date(2025, 9, Math.floor(Math.random() * 30) + 1);
          const content = [
            "Customer requested information about upcoming sales.",
            "Customer mentioned they were happy with last purchase.",
            "Customer asked about exchange policy for recent order.",
            "Followed up on a return request.",
            "Customer prefers email communication only.",
          ][Math.floor(Math.random() * 5)];

          notes.push({
            id: `NOTE-${String(Math.floor(Math.random() * 100000)).padStart(
              6,
              "0"
            )}`,
            date,
            author: "You",
            content,
          });
        }

        notesMap[customer.id] = notes.sort((a, b) => b.date - a.date);
      } else {
        notesMap[customer.id] = [];
      }
    });

    return notesMap;
  }

  // Format currency
  function formatCurrency(amount) {
    return new Intl.NumberFormat("en-PH", {
      style: "currency",
      currency: "PHP",
      minimumFractionDigits: 2,
    })
      .format(amount)
      .replace("PHP", "₱");
  }

  // Format date
  function formatDate(date) {
    return new Date(date).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  }

  // Update customer stats
  function updateCustomerStats() {
    const totalCustomers = customerData.length;
    const activeCustomers = customerData.filter(
      (c) => c.status === "active"
    ).length;
    const newCustomers = customerData.filter((c) => c.status === "new").length;

    const totalSpent = customerData.reduce(
      (sum, c) => sum + parseFloat(c.totalSpent),
      0
    );
    const avgSpend = totalSpent / totalCustomers;

    const retention = (activeCustomers / totalCustomers) * 100;
    const returnRate = Math.random() * 5 + 2; // Sample return rate between 2-7%

    document.getElementById("totalCustomers").textContent = totalCustomers;
    document.getElementById("avgSpend").textContent = formatCurrency(avgSpend);
    document.getElementById("retention").textContent = `${retention.toFixed(
      1
    )}%`;
    document.getElementById("returnRate").textContent = `${returnRate.toFixed(
      1
    )}%`;

    document.getElementById("customerGrowth").textContent = `${(
      (newCustomers / totalCustomers) *
      100
    ).toFixed(1)}%`;
    document.getElementById("spendGrowth").textContent = "5.2%";
    document.getElementById("retentionChange").textContent = "2.7%";
    document.getElementById("returnChange").textContent = "1.5%";
  }

  // Create customer growth chart
  function createCustomerGrowthChart() {
    const canvas = document.getElementById("customerGrowthChart");
    const ctx = canvas.getContext("2d");

    // Generate sample data for the last 30 days
    const labels = [];
    const newCustomers = [];
    const totalCustomers = [];

    let runningTotal = 30;

    for (let i = 30; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      labels.push(
        date.toLocaleDateString("en-US", { month: "short", day: "numeric" })
      );

      const newCount = Math.floor(Math.random() * 5) + 1;
      newCustomers.push(newCount);

      runningTotal += newCount;
      totalCustomers.push(runningTotal);
    }

    drawChart(ctx, canvas, labels, totalCustomers, newCustomers);
  }

  // Create customer segments chart
  function createCustomerSegmentsChart() {
    const canvas = document.getElementById("customerSegmentsChart");
    const ctx = canvas.getContext("2d");

    // Sample segment data
    const segments = [
      { label: "New", value: 15, color: "#3b82f6" },
      { label: "Returning", value: 45, color: "#6d28d9" },
      { label: "Regular", value: 25, color: "#10b981" },
      { label: "VIP", value: 15, color: "#f59e0b" },
    ];

    drawPieChart(ctx, canvas, segments);
  }

  // Draw line chart
  function drawChart(ctx, canvas, labels, totalData, newData) {
    // Set canvas dimensions
    canvas.width = canvas.offsetWidth * 2;
    canvas.height = canvas.offsetHeight * 2;
    ctx.scale(2, 2);

    const width = canvas.width / 2;
    const height = canvas.height / 2;
    const padding = 40;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw grid
    ctx.strokeStyle = "#e5e7eb";
    ctx.lineWidth = 1;

    // Find max value for scaling
    const maxValue = Math.max(...totalData) * 1.1;
    const yStep = maxValue / 5;

    // Draw horizontal grid lines and y-axis labels
    for (let i = 0; i <= 5; i++) {
      const y = height - padding - (i / 5) * (height - padding * 2);

      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(width - padding, y);
      ctx.stroke();

      ctx.fillStyle = "#9ca3af";
      ctx.font = "10px sans-serif";
      ctx.textAlign = "right";
      ctx.fillText(Math.round(i * yStep).toString(), padding - 8, y + 4);
    }

    // Draw total customers line
    const drawLine = (data, color, fill = false) => {
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.beginPath();

      // Starting point
      const x0 = padding;
      const y0 =
        height - padding - (data[0] / maxValue) * (height - padding * 2);
      ctx.moveTo(x0, y0);

      // Connect points
      for (let i = 1; i < data.length; i++) {
        const x = padding + (i / (data.length - 1)) * (width - padding * 2);
        const y =
          height - padding - (data[i] / maxValue) * (height - padding * 2);
        ctx.lineTo(x, y);
      }

      ctx.stroke();

      if (fill) {
        // Fill area under the line
        ctx.lineTo(padding + (width - padding * 2), height - padding);
        ctx.lineTo(padding, height - padding);
        ctx.closePath();
        ctx.fillStyle = color + "20"; // Add transparency
        ctx.fill();
      }
    };

    // Draw total customers line
    drawLine(totalData, "#6d28d9", true);

    // Draw new customers line
    drawLine(newData, "#10b981");

    // Draw x-axis labels (dates)
    ctx.fillStyle = "#9ca3af";
    ctx.font = "10px sans-serif";
    ctx.textAlign = "center";

    // Draw every 5th label to avoid clutter
    for (let i = 0; i < labels.length; i += 5) {
      const x = padding + (i / (labels.length - 1)) * (width - padding * 2);
      ctx.fillText(labels[i], x, height - padding + 16);
    }

    // Draw legend
    const legendY = padding / 2;

    // Total customers
    ctx.fillStyle = "#6d28d9";
    ctx.fillRect(padding, legendY, 12, 6);
    ctx.fillStyle = "#111827";
    ctx.font = "11px sans-serif";
    ctx.textAlign = "left";
    ctx.fillText("Total Customers", padding + 18, legendY + 6);

    // New customers
    ctx.fillStyle = "#10b981";
    ctx.fillRect(padding + 120, legendY, 12, 6);
    ctx.fillStyle = "#111827";
    ctx.fillText("New Customers", padding + 138, legendY + 6);
  }

  // Draw pie chart
  function drawPieChart(ctx, canvas, segments) {
    // Set canvas dimensions
    canvas.width = canvas.offsetWidth * 2;
    canvas.height = canvas.offsetHeight * 2;
    ctx.scale(2, 2);

    const width = canvas.width / 2;
    const height = canvas.height / 2;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(centerX, centerY) - 60;

    // Calculate total value
    const total = segments.reduce((sum, segment) => sum + segment.value, 0);

    // Draw segments
    let startAngle = -Math.PI / 2; // Start at top (12 o'clock)

    segments.forEach((segment) => {
      const sliceAngle = (segment.value / total) * Math.PI * 2;

      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.arc(centerX, centerY, radius, startAngle, startAngle + sliceAngle);
      ctx.closePath();

      ctx.fillStyle = segment.color;
      ctx.fill();

      // Calculate angle for label position
      const labelAngle = startAngle + sliceAngle / 2;
      const labelRadius = radius * 0.7;
      const labelX = centerX + Math.cos(labelAngle) * labelRadius;
      const labelY = centerY + Math.sin(labelAngle) * labelRadius;

      // Draw percentage label
      ctx.fillStyle = "#fff";
      ctx.font = "bold 12px sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(
        `${Math.round((segment.value / total) * 100)}%`,
        labelX,
        labelY
      );

      startAngle += sliceAngle;
    });

    // Draw legend
    const legendX = width - 100;
    let legendY = height / 2 - (segments.length * 20) / 2;

    segments.forEach((segment) => {
      ctx.fillStyle = segment.color;
      ctx.fillRect(legendX - 20, legendY, 12, 12);

      ctx.fillStyle = "#111827";
      ctx.font = "11px sans-serif";
      ctx.textAlign = "left";
      ctx.textBaseline = "middle";
      ctx.fillText(segment.label, legendX, legendY + 6);

      legendY += 25;
    });
  }

  // Update customer table with paginated data
  function updateCustomerTable() {
    const tbody = document.getElementById("customerTableBody");
    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const pageData = filteredCustomers.slice(start, end);

    tbody.innerHTML = "";

    pageData.forEach((customer) => {
      const row = document.createElement("tr");

      const statusText =
        customer.status.charAt(0).toUpperCase() + customer.status.slice(1);

      row.innerHTML = `
        <td>${customer.id}</td>
        <td>
          <div class="customer-info">
            <div class="customer-avatar">${customer.avatar}</div>
            <div class="customer-name">${customer.name}</div>
          </div>
        </td>
        <td>${customer.email}</td>
        <td>
          <span class="status-badge ${customer.status}">${statusText}</span>
        </td>
        <td>${customer.orders}</td>
        <td>${formatCurrency(customer.totalSpent)}</td>
        <td>${formatDate(customer.lastOrder)}</td>
        <td>
            <div class="action-buttons">
                <button class="action-btn view-btn" title="View Details" data-customer-id="${
                  customer.id
                }">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                        <circle cx="12" cy="12" r="3"></circle>
                    </svg>
                </button>
                <button class="action-btn message-btn" title="Send Message" data-customer-id="${
                  customer.id
                }">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                        <polyline points="22,6 12,13 2,6"></polyline>
                    </svg>
                </button>
            </div>
        </td>
      `;

      tbody.appendChild(row);
    });

    // Add event listeners to view buttons
    document.querySelectorAll(".view-btn").forEach((btn) => {
      btn.addEventListener("click", function () {
        const customerId = this.getAttribute("data-customer-id");
        openCustomerModal(customerId);
      });
    });
  }

  // Search customers
  function searchCustomers(query) {
    query = query.toLowerCase();

    if (!query) {
      filteredCustomers = [...customerData];
    } else {
      filteredCustomers = customerData.filter(
        (customer) =>
          customer.name.toLowerCase().includes(query) ||
          customer.email.toLowerCase().includes(query) ||
          customer.id.toLowerCase().includes(query)
      );
    }

    currentPage = 1;
    updateCustomerTable();
    updatePaginationInfo();
    setupPagination();
  }

  // Filter customers
  function filterCustomers(filterType) {
    switch (filterType) {
      case "all":
        filteredCustomers = [...customerData];
        break;
      case "new":
        filteredCustomers = customerData.filter(
          (customer) => customer.status === "new"
        );
        break;
      case "returning":
        filteredCustomers = customerData.filter(
          (customer) => customer.status === "active" && customer.orders > 1
        );
        break;
      case "inactive":
        filteredCustomers = customerData.filter(
          (customer) => customer.status === "inactive"
        );
        break;
    }

    currentPage = 1;
    updateCustomerTable();
    updatePaginationInfo();
    setupPagination();
  }

  // Setup pagination
  function setupPagination() {
    const totalPages = Math.ceil(filteredCustomers.length / itemsPerPage);
    const paginationEl = document.getElementById("paginationNumbers");
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");

    paginationEl.innerHTML = "";

    // Add page numbers
    for (let i = 1; i <= totalPages; i++) {
      if (
        totalPages <= 7 ||
        i === 1 ||
        i === totalPages ||
        i === currentPage ||
        i === currentPage - 1 ||
        i === currentPage + 1
      ) {
        const pageEl = document.createElement("span");
        pageEl.classList.add("page-number");

        if (i === currentPage) {
          pageEl.classList.add("active");
        }

        pageEl.textContent = i;

        pageEl.addEventListener("click", () => {
          currentPage = i;
          updateCustomerTable();
          updatePaginationInfo();
          setupPagination();
        });

        paginationEl.appendChild(pageEl);
      } else if (
        (i === 2 && currentPage > 3) ||
        (i === totalPages - 1 && currentPage < totalPages - 2)
      ) {
        const ellipsis = document.createElement("span");
        ellipsis.classList.add("page-number");
        ellipsis.textContent = "...";
        paginationEl.appendChild(ellipsis);
      }
    }

    // Update prev/next buttons
    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage === totalPages;

    prevBtn.addEventListener("click", () => {
      if (currentPage > 1) {
        currentPage--;
        updateCustomerTable();
        updatePaginationInfo();
        setupPagination();
      }
    });

    nextBtn.addEventListener("click", () => {
      if (currentPage < totalPages) {
        currentPage++;
        updateCustomerTable();
        updatePaginationInfo();
        setupPagination();
      }
    });
  }

  // Update pagination info
  function updatePaginationInfo() {
    const totalItems = filteredCustomers.length;
    const start = (currentPage - 1) * itemsPerPage + 1;
    const end = Math.min(start + itemsPerPage - 1, totalItems);

    document.getElementById("showingCustomers").textContent =
      totalItems === 0 ? 0 : `${start}-${end}`;
    document.getElementById("totalCustomersCount").textContent = totalItems;
  }

  // Export customer data
  function exportCustomerData() {
    // In a real application, this would generate a CSV or Excel file
    alert(
      "Customer data export initiated. Your file will be ready for download shortly."
    );
  }

  // Setup customer detail modal
  function setupCustomerDetailModal() {
    const modal = document.getElementById("customerDetailModal");
    const closeBtn = document.getElementById("closeModal");

    closeBtn.addEventListener("click", () => {
      modal.classList.remove("active");
    });

    // Close modal when clicking outside
    window.addEventListener("click", (e) => {
      if (e.target === modal) {
        modal.classList.remove("active");
      }
    });

    // Add note functionality
    document.getElementById("saveNote").addEventListener("click", () => {
      const noteText = document.getElementById("newNote").value.trim();
      const customerId = modal.getAttribute("data-customer-id");

      if (noteText && customerId) {
        addCustomerNote(customerId, noteText);
        document.getElementById("newNote").value = "";
      }
    });
  }

  // Open customer modal
  function openCustomerModal(customerId) {
    const modal = document.getElementById("customerDetailModal");
    const customer = customerData.find((c) => c.id === customerId);

    if (customer) {
      // Set customer ID to modal
      modal.setAttribute("data-customer-id", customerId);

      // Update customer profile
      document.getElementById("modalCustomerAvatar").textContent =
        customer.avatar;
      document.getElementById("modalCustomerName").textContent = customer.name;
      document.getElementById("modalCustomerEmail").textContent =
        customer.email;

      const statusEl = document.getElementById("modalCustomerStatus");
      statusEl.textContent =
        customer.status.charAt(0).toUpperCase() + customer.status.slice(1);
      statusEl.className = "status-badge " + customer.status;

      // Update customer stats
      document.getElementById("modalCustomerOrders").textContent =
        customer.orders;
      document.getElementById("modalCustomerSpent").textContent =
        formatCurrency(customer.totalSpent);

      // Calculate average order value
      const avgOrder = customer.totalSpent / customer.orders;
      document.getElementById("modalCustomerAvgOrder").textContent =
        formatCurrency(avgOrder);

      document.getElementById("modalCustomerJoined").textContent = formatDate(
        customer.joinDate
      );

      // Populate orders tab
      populateCustomerOrders(customerId);

      // Populate activity tab
      populateCustomerActivity(customerId);

      // Populate notes tab
      populateCustomerNotes(customerId);

      // Reset to first tab
      document.querySelector('.tab[data-tab="orders"]').click();

      // Show modal
      modal.classList.add("active");
    }
  }

  // Setup modal tabs
  function setupModalTabs() {
    const tabs = document.querySelectorAll(".tab");
    const tabContents = document.querySelectorAll(".tab-content");

    tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        const tabId = tab.getAttribute("data-tab");

        // Update active tab
        tabs.forEach((t) => t.classList.remove("active"));
        tab.classList.add("active");

        // Show corresponding content
        tabContents.forEach((content) => {
          if (content.getAttribute("data-content") === tabId) {
            content.classList.add("active");
          } else {
            content.classList.remove("active");
          }
        });
      });
    });
  }

  // Populate customer orders
  function populateCustomerOrders(customerId) {
    const orders = customerOrders[customerId] || [];
    const tableBody = document.getElementById("customerOrdersTable");

    tableBody.innerHTML = "";

    if (orders.length === 0) {
      tableBody.innerHTML =
        '<tr><td colspan="5" class="empty-table">No orders yet</td></tr>';
      return;
    }

    orders.forEach((order) => {
      const row = document.createElement("tr");

      row.innerHTML = `
        <td>${order.id}</td>
        <td>${formatDate(order.date)}</td>
        <td>${order.items.join(", ")}</td>
        <td>${formatCurrency(order.total)}</td>
        <td><span class="status-badge ${order.status}">${
        order.status.charAt(0).toUpperCase() + order.status.slice(1)
      }</span></td>
      `;

      tableBody.appendChild(row);
    });
  }

  // Populate customer activity
  function populateCustomerActivity(customerId) {
    const activities = customerActivity[customerId] || [];
    const activityEl = document.getElementById("customerActivity");

    activityEl.innerHTML = "";

    if (activities.length === 0) {
      activityEl.innerHTML =
        '<div class="empty-state"><p>No activity recorded yet</p></div>';
      return;
    }

    activities.forEach((activity) => {
      const activityItem = document.createElement("div");
      activityItem.className = "activity-item";

      let iconSvg;

      switch (activity.type) {
        case "order":
          iconSvg =
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path><line x1="3" y1="6" x2="21" y2="6"></line><path d="M16 10a4 4 0 0 1-8 0"></path></svg>';
          break;
        case "login":
          iconSvg =
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path><polyline points="10 17 15 12 10 7"></polyline><line x1="15" y1="12" x2="3" y2="12"></line></svg>';
          break;
        case "cart":
          iconSvg =
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="21" r="1"></circle><circle cx="20" cy="21" r="1"></circle><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path></svg>';
          break;
        case "wishlist":
          iconSvg =
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>';
          break;
        case "review":
          iconSvg =
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>';
          break;
        case "return":
          iconSvg =
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="1 4 1 10 7 10"></polyline><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path></svg>';
          break;
      }

      const formattedDate = new Date(activity.date).toLocaleDateString(
        "en-US",
        {
          month: "short",
          day: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        }
      );

      activityItem.innerHTML = `
        <div class="activity-icon">${iconSvg}</div>
        <div class="activity-content">
          <div class="activity-header">
            <span class="activity-title">${
              activity.type.charAt(0).toUpperCase() + activity.type.slice(1)
            } Activity</span>
            <span class="activity-date">${formattedDate}</span>
          </div>
          <p class="activity-description">${activity.description}</p>
        </div>
      `;

      activityEl.appendChild(activityItem);
    });
  }

  // Populate customer notes
  function populateCustomerNotes(customerId) {
    const notes = customerNotes[customerId] || [];
    const notesEl = document.getElementById("customerNotes");

    notesEl.innerHTML = "";

    if (notes.length === 0) {
      notesEl.innerHTML =
        '<div class="empty-state"><p>No notes yet. Add your first note below.</p></div>';
      return;
    }

    notes.forEach((note) => {
      const noteItem = document.createElement("div");
      noteItem.className = "note-item";

      const formattedDate = formatDate(note.date);

      noteItem.innerHTML = `
        <div class="note-header">
          <span class="note-author">${note.author}</span>
          <span class="note-date">${formattedDate}</span>
        </div>
        <p class="note-content">${note.content}</p>
      `;

      notesEl.appendChild(noteItem);
    });
  }

  // Add a new note to a customer
  function addCustomerNote(customerId, content) {
    if (!customerNotes[customerId]) {
      customerNotes[customerId] = [];
    }

    const note = {
      id: `NOTE-${String(Math.floor(Math.random() * 100000)).padStart(6, "0")}`,
      date: new Date(),
      author: "You",
      content,
    };

    customerNotes[customerId].unshift(note);

    // Refresh notes display
    populateCustomerNotes(customerId);
  }
});
