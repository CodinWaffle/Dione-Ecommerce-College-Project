document.addEventListener("DOMContentLoaded", function () {
  // Initialize charts
  initRatingTimeChart();
  initRatingDistributionChart();

  // Handle modal events
  setupModalEvents();

  // Initialize table filters and search
  setupTableFilters();

  // Initialize view reviews buttons
  setupViewReviewsButtons();

  // Initialize response forms
  setupResponseForms();

  // Create notification container if it doesn't exist
  if (!document.getElementById("notification-container")) {
    const notificationContainer = document.createElement("div");
    notificationContainer.id = "notification-container";
    document.body.appendChild(notificationContainer);
  }
});

// Function to initialize the Rating Over Time chart
function initRatingTimeChart() {
  const ctx = document.getElementById("rating-time-chart");

  if (!ctx) return;

  // Sample data - replace with real data from backend
  const labels = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ];
  const averageRatings = [
    4.2, 4.3, 4.1, 4.4, 4.6, 4.5, 4.7, 4.8, 4.7, 4.9, 4.8, 4.9,
  ];
  const reviewCounts = [12, 15, 10, 18, 22, 25, 30, 32, 28, 35, 38, 42];

  // Calculate max review count for right y-axis scaling
  const maxReviewCount = Math.max(...reviewCounts);

  // Create chart using Chart.js (make sure Chart.js is included in your project)
  if (typeof Chart !== "undefined") {
    new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Average Rating",
            data: averageRatings,
            borderColor: "#6d28d9",
            backgroundColor: "rgba(109, 40, 217, 0.1)",
            borderWidth: 2,
            tension: 0.3,
            fill: true,
            yAxisID: "y",
          },
          {
            label: "Number of Reviews",
            data: reviewCounts,
            borderColor: "#10b981",
            backgroundColor: "transparent",
            borderWidth: 2,
            borderDash: [5, 5],
            tension: 0.3,
            pointRadius: 3,
            yAxisID: "y1",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: false,
            min: 0,
            max: 5,
            title: {
              display: true,
              text: "Average Rating",
            },
            grid: {
              display: true,
              drawBorder: true,
              borderDash: [5, 5],
              color: "rgba(0, 0, 0, 0.05)",
            },
          },
          y1: {
            position: "right",
            beginAtZero: true,
            max: maxReviewCount + maxReviewCount * 0.2,
            title: {
              display: true,
              text: "Number of Reviews",
            },
            grid: {
              display: false,
            },
          },
          x: {
            grid: {
              color: "rgba(0, 0, 0, 0.05)",
            },
          },
        },
        plugins: {
          tooltip: {
            mode: "index",
            intersect: false,
          },
          legend: {
            position: "top",
            labels: {
              usePointStyle: true,
              boxWidth: 6,
            },
          },
        },
      },
    });
  } else {
    console.warn("Chart.js is not loaded. Please include Chart.js library.");
  }
}

// Function to initialize the Rating Distribution chart
function initRatingDistributionChart() {
  const ctx = document.getElementById("rating-distribution-chart");

  if (!ctx) return;

  // Sample data - replace with real data from backend
  const ratingCounts = [5, 12, 28, 45, 89];
  const totalReviews = ratingCounts.reduce((a, b) => a + b, 0);
  const ratingPercentages = ratingCounts.map((count) =>
    ((count / totalReviews) * 100).toFixed(1)
  );

  if (typeof Chart !== "undefined") {
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: ["1 Star", "2 Stars", "3 Stars", "4 Stars", "5 Stars"],
        datasets: [
          {
            label: "Reviews",
            data: ratingCounts,
            backgroundColor: [
              "rgba(239, 68, 68, 0.8)",
              "rgba(245, 158, 11, 0.8)",
              "rgba(249, 115, 22, 0.8)",
              "rgba(16, 185, 129, 0.8)",
              "rgba(109, 40, 217, 0.8)",
            ],
            borderColor: [
              "rgb(239, 68, 68)",
              "rgb(245, 158, 11)",
              "rgb(249, 115, 22)",
              "rgb(16, 185, 129)",
              "rgb(109, 40, 217)",
            ],
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: "Number of Reviews",
            },
            grid: {
              display: true,
              drawBorder: true,
              borderDash: [5, 5],
              color: "rgba(0, 0, 0, 0.05)",
            },
          },
          x: {
            grid: {
              display: false,
            },
          },
        },
        plugins: {
          tooltip: {
            callbacks: {
              afterLabel: function (context) {
                const index = context.dataIndex;
                return ratingPercentages[index] + "% of total reviews";
              },
            },
          },
          legend: {
            display: false,
          },
        },
      },
    });
  }
}

// Set up modal functionality
function setupModalEvents() {
  // Get all elements that should open modals
  const modalOpeners = document.querySelectorAll("[data-modal-target]");
  const modalClosers = document.querySelectorAll("[data-modal-close]");
  const modals = document.querySelectorAll(".modal");

  // Add click events to modal openers
  modalOpeners.forEach((opener) => {
    opener.addEventListener("click", function () {
      const modalId = this.getAttribute("data-modal-target");
      const modal = document.getElementById(modalId);

      if (modal) {
        modal.classList.add("active");
        document.body.style.overflow = "hidden";
      }
    });
  });

  // Add click events to modal closers
  modalClosers.forEach((closer) => {
    closer.addEventListener("click", function () {
      const modal = this.closest(".modal");

      if (modal) {
        modal.classList.remove("active");
        document.body.style.overflow = "";
      }
    });
  });

  // Close modal when clicking outside of modal content
  modals.forEach((modal) => {
    modal.addEventListener("click", function (e) {
      if (e.target === this) {
        modal.classList.remove("active");
        document.body.style.overflow = "";
      }
    });
  });

  // Close modal on ESC key
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      modals.forEach((modal) => {
        modal.classList.remove("active");
      });
      document.body.style.overflow = "";
    }
  });
}

// Set up table filters and search functionality
function setupTableFilters() {
  const searchInput = document.querySelector(".search-input");
  const filterSelect = document.querySelector(".filter-select");
  const sortSelect = document.querySelector(".sort-filter select");
  const tableRows = document.querySelectorAll(".data-table tbody tr");

  if (!searchInput || !tableRows.length) return;

  // Search functionality
  searchInput.addEventListener("input", filterTable);

  // Filter select functionality
  if (filterSelect) {
    filterSelect.addEventListener("change", filterTable);
  }

  // Sort select functionality
  if (sortSelect) {
    sortSelect.addEventListener("change", filterTable);
  }

  // Combined filter function
  function filterTable() {
    const searchTerm = searchInput.value.toLowerCase();
    const filterValue = filterSelect ? filterSelect.value.toLowerCase() : "";

    tableRows.forEach((row) => {
      const customerName =
        row.querySelector("[data-customer]")?.textContent.toLowerCase() || "";
      const reviewText =
        row.querySelector("[data-review]")?.textContent.toLowerCase() || "";
      const productName =
        row.querySelector("[data-product]")?.textContent.toLowerCase() || "";
      const rating =
        row.querySelector("[data-rating]")?.getAttribute("data-rating") || "";
      const status =
        row.querySelector("[data-status]")?.textContent.toLowerCase() || "";

      // Combine all searchable text
      const searchableText = `${customerName} ${reviewText} ${productName}`;

      // Check if row matches search term
      const matchesSearch =
        searchTerm === "" || searchableText.includes(searchTerm);

      // Check if row matches filter
      let matchesFilter = true;

      if (filterValue && filterValue !== "all") {
        if (filterValue === "high-rating" && parseFloat(rating) < 4) {
          matchesFilter = false;
        } else if (filterValue === "low-rating" && parseFloat(rating) >= 3) {
          matchesFilter = false;
        } else if (filterValue === "pending" && status !== "pending") {
          matchesFilter = false;
        } else if (filterValue === "responded" && status !== "responded") {
          matchesFilter = false;
        } else if (filterValue === "flagged" && status !== "flagged") {
          matchesFilter = false;
        }
      }

      // Show or hide row based on filters
      if (matchesSearch && matchesFilter) {
        row.style.display = "";
      } else {
        row.style.display = "none";
      }
    });

    // Update "no results" message if needed
    updateNoResultsMessage();
  }

  // Show/hide "no results" message
  function updateNoResultsMessage() {
    const visibleRows = Array.from(tableRows).filter(
      (row) => row.style.display !== "none"
    );
    const noResultsMessage = document.querySelector(".no-results-message");

    if (noResultsMessage) {
      if (visibleRows.length === 0) {
        noResultsMessage.style.display = "block";
      } else {
        noResultsMessage.style.display = "none";
      }
    }
  }
}

// Set up view reviews buttons for product cards
function setupViewReviewsButtons() {
  const viewButtons = document.querySelectorAll(".view-reviews-btn");

  viewButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const productId = this.getAttribute("data-product-id");
      // Here you would load the reviews for this product
      // For demonstration, we'll just open a modal
      const reviewsModal = document.getElementById("product-reviews-modal");

      if (reviewsModal) {
        // You could update the modal content here based on the product ID
        const modalTitle = reviewsModal.querySelector(".modal-title");
        if (modalTitle) {
          const productName =
            this.closest(".product-card").querySelector(
              ".product-name"
            ).textContent;
          modalTitle.textContent = `Reviews for ${productName}`;
        }

        reviewsModal.classList.add("active");
        document.body.style.overflow = "hidden";
      }
    });
  });
}

// Set up response forms for reviews
function setupResponseForms() {
  const responseForms = document.querySelectorAll(".response-form");

  responseForms.forEach((form) => {
    form.addEventListener("submit", function (e) {
      e.preventDefault();

      const reviewId = this.getAttribute("data-review-id");
      const responseText = this.querySelector("textarea").value;

      if (!responseText.trim()) {
        alert("Please enter a response");
        return;
      }

      // Send the response to the server
      fetch("/seller/api/review-response", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          review_id: reviewId,
          response: responseText,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.status === "success") {
            console.log("Response saved successfully:", data);

            // Update UI to show the response was submitted
            const responseSection = this.closest(".seller-response-section");
            const existingResponse =
              responseSection.querySelector(".existing-response");

            // Show a success message
            showNotification("Response saved successfully", "success");
          } else {
            console.error("Error saving response:", data);
            showNotification(
              "Failed to save response. Please try again.",
              "error"
            );
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          showNotification(
            "Failed to save response. Please try again.",
            "error"
          );
        });

      // Update UI optimistically (before server response)
      const responseSection = this.closest(".seller-response-section");
      const existingResponse =
        responseSection.querySelector(".existing-response");

      if (existingResponse) {
        // Update existing response
        existingResponse.querySelector(".response-content").textContent =
          responseText;
        existingResponse.querySelector(".response-meta").textContent =
          "Just now";
        existingResponse.style.display = "block";
      } else {
        // Create new response element
        const newResponse = document.createElement("div");
        newResponse.className = "existing-response";
        newResponse.innerHTML = `
                    <p class="response-content">${responseText}</p>
                    <p class="response-meta">Just now</p>
                    <button class="action-btn edit-response-btn" title="Edit Response">
                        <i class="fas fa-pencil-alt"></i>
                    </button>
                `;

        // Insert before the form
        responseSection.insertBefore(newResponse, this);
      }

      // Hide the form
      this.style.display = "none";

      // Update status badge in the table if available
      const reviewRow = document.querySelector(
        `tr[data-review-id="${reviewId}"]`
      );
      if (reviewRow) {
        const statusBadge = reviewRow.querySelector(".status-badge");
        if (statusBadge) {
          statusBadge.className = "status-badge responded";
          statusBadge.textContent = "Responded";
        }
      }

      // Close modal if we're in one
      const modal = this.closest(".modal");
      if (modal) {
        // Don't close immediately so the user can see the confirmation
        setTimeout(() => {
          modal.classList.remove("active");
          document.body.style.overflow = "";
        }, 1500);
      }
    });
  });

  // Handle "Edit Response" button clicks
  document.addEventListener("click", function (e) {
    if (e.target.closest(".edit-response-btn")) {
      const responseSection = e.target.closest(".seller-response-section");
      const existingResponse =
        responseSection.querySelector(".existing-response");
      const responseForm = responseSection.querySelector(".response-form");

      if (existingResponse && responseForm) {
        // Get current response text
        const currentText =
          existingResponse.querySelector(".response-content").textContent;

        // Set form textarea value
        responseForm.querySelector("textarea").value = currentText;

        // Show form, hide existing response
        responseForm.style.display = "flex";
        existingResponse.style.display = "none";
      }
    }
  });
}

// Handle flag review form submission
document.addEventListener("click", function (e) {
  const flagForm = document.getElementById("flag-review-form");

  if (!flagForm) return;

  if (e.target.closest('[data-action="flag-review"]')) {
    const reviewId = e.target
      .closest("[data-review-id]")
      .getAttribute("data-review-id");
    flagForm.setAttribute("data-review-id", reviewId);
  }

  if (e.target.matches('#flag-review-form button[type="submit"]')) {
    e.preventDefault();

    const reviewId = flagForm.getAttribute("data-review-id");
    const flagReason = flagForm.querySelector(
      'input[name="flag-reason"]:checked'
    )?.value;
    const flagNotes = flagForm.querySelector(
      'textarea[name="flag-notes"]'
    ).value;

    if (!flagReason) {
      alert("Please select a reason for flagging this review");
      return;
    }

    // Here you would send the flag info to the server
    console.log(
      `Flagged review ${reviewId} for ${flagReason}. Notes: ${flagNotes}`
    );

    // Update UI
    const reviewRow = document.querySelector(
      `tr[data-review-id="${reviewId}"]`
    );
    if (reviewRow) {
      const statusBadge = reviewRow.querySelector(".status-badge");
      if (statusBadge) {
        statusBadge.className = "status-badge flagged";
        statusBadge.textContent = "Flagged";
      }
    }

    // Close the modal
    const modal = flagForm.closest(".modal");
    if (modal) {
      modal.classList.remove("active");
      document.body.style.overflow = "";
    }

    // Reset form
    flagForm.reset();
  }
});

// Initialize pagination
document.addEventListener("click", function (e) {
  if (
    e.target.classList.contains("page-number") &&
    !e.target.classList.contains("active")
  ) {
    const paginationNumbers = document.querySelectorAll(".page-number");

    paginationNumbers.forEach((num) => num.classList.remove("active"));
    e.target.classList.add("active");

    // Here you would fetch and display the corresponding page of reviews
    // For demonstration, we'll just log the page number
    console.log(`Navigate to page ${e.target.textContent}`);
  }

  // Previous page button
  if (e.target.closest(".pagination-btn.prev")) {
    const activePage = document.querySelector(".page-number.active");
    if (
      activePage &&
      activePage.previousElementSibling &&
      activePage.previousElementSibling.classList.contains("page-number")
    ) {
      activePage.classList.remove("active");
      activePage.previousElementSibling.classList.add("active");
      console.log(
        `Navigate to page ${activePage.previousElementSibling.textContent}`
      );
    }
  }

  // Next page button
  if (e.target.closest(".pagination-btn.next")) {
    const activePage = document.querySelector(".page-number.active");
    if (
      activePage &&
      activePage.nextElementSibling &&
      activePage.nextElementSibling.classList.contains("page-number")
    ) {
      activePage.classList.remove("active");
      activePage.nextElementSibling.classList.add("active");
      console.log(
        `Navigate to page ${activePage.nextElementSibling.textContent}`
      );
    }
  }
});

// Handle time filter changes for charts
document.addEventListener("change", function (e) {
  if (e.target.classList.contains("time-filter")) {
    const timeRange = e.target.value;
    const chartId = e.target.getAttribute("data-chart");

    if (chartId) {
      console.log(`Update ${chartId} chart with time range: ${timeRange}`);
      // Here you would fetch new data and update the chart
      // For demonstration purposes only
    }
  }
});

// Helper function to format numbers with commas
function formatNumber(number) {
  return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Export table data to CSV
document.addEventListener("click", function (e) {
  if (e.target.closest(".export-btn")) {
    const table = document.querySelector(".data-table");
    if (!table) return;

    // Get column headers
    const headers = Array.from(table.querySelectorAll("thead th")).map((th) =>
      th.textContent.trim()
    );

    // Get visible rows
    const rows = Array.from(table.querySelectorAll("tbody tr")).filter(
      (row) => row.style.display !== "none"
    );

    // Convert rows to data
    const data = rows.map((row) => {
      return Array.from(row.querySelectorAll("td")).map((td) =>
        td.textContent.trim().replace(/,/g, " ").replace(/\n/g, " ")
      );
    });

    // Create CSV content
    let csvContent = headers.join(",") + "\n";
    csvContent += data.map((row) => row.join(",")).join("\n");

    // Create a download link
    const encodedUri = encodeURI("data:text/csv;charset=utf-8," + csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute(
      "download",
      "reviews_export_" + new Date().toISOString().split("T")[0] + ".csv"
    );
    document.body.appendChild(link);

    // Download the CSV file
    link.click();

    // Clean up
    document.body.removeChild(link);
  }
});

// Notification system
function showNotification(message, type = "info") {
  const container =
    document.getElementById("notification-container") || document.body;

  // Create notification element
  const notification = document.createElement("div");
  notification.className = `notification ${type}`;
  notification.innerHTML = `
    <div class="notification-content">
      ${message}
    </div>
    <button class="notification-close">×</button>
  `;

  // Add to container
  container.appendChild(notification);

  // Add animation class after a small delay to trigger transition
  setTimeout(() => {
    notification.classList.add("show");
  }, 10);

  // Add close button functionality
  const closeBtn = notification.querySelector(".notification-close");
  closeBtn.addEventListener("click", () => {
    notification.classList.remove("show");
    setTimeout(() => {
      notification.remove();
    }, 300); // Match CSS transition duration
  });

  // Auto-dismiss after 5 seconds
  setTimeout(() => {
    if (notification.parentNode) {
      notification.classList.remove("show");
      setTimeout(() => {
        if (notification.parentNode) {
          notification.remove();
        }
      }, 300);
    }
  }, 5000);
}

// Update rating bars in product cards
function updateRatingBars() {
  const ratingBars = document.querySelectorAll(".rating-bar-fill");

  ratingBars.forEach((bar) => {
    const percentage = bar.getAttribute("data-percentage");
    if (percentage) {
      bar.style.width = percentage + "%";
    }
  });
}

// Call this function after DOM is loaded
document.addEventListener("DOMContentLoaded", updateRatingBars);

// Quick reply functionality removed as requested
/*
document.addEventListener("click", function (e) {
  if (e.target.closest('[data-action="quick-reply"]')) {
    const replyBtn = e.target.closest('[data-action="quick-reply"]');
    const reviewId = replyBtn.getAttribute("data-review-id");
    const reviewRow = document.querySelector(
      `tr[data-review-id="${reviewId}"]`
    );

    // If the quick reply form already exists, toggle it
    const existingForm = document.getElementById(
      `quick-reply-form-${reviewId}`
    );
    if (existingForm) {
      existingForm.remove();
      return;
    }

    // Create and insert a quick reply form below the review row
    const formRow = document.createElement("tr");
    formRow.className = "quick-reply-row";
    formRow.id = `quick-reply-form-${reviewId}`;

    const formCell = document.createElement("td");
    formCell.colSpan = 7;
    formCell.className = "quick-reply-cell";

    formCell.innerHTML = `
      <form class="quick-reply-form" data-review-id="${reviewId}">
        <div class="quick-reply-header">
          <h4>Reply to this review</h4>
        </div>
        <div class="quick-reply-content">
          <textarea name="quick-reply-text" placeholder="Type your response here..." required></textarea>
          <div class="response-tips">
            <h5>Tips for responding to reviews:</h5>
            <ul>
              <li>Thank the customer for their feedback</li>
              <li>Be professional and courteous</li>
              <li>Offer solutions for any issues mentioned</li>
              <li>Avoid defensive responses</li>
            </ul>
          </div>
        </div>
        <div class="quick-reply-actions">
          <button type="submit" class="action-btn primary">Send Response</button>
          <button type="button" class="action-btn secondary cancel-reply">Cancel</button>
        </div>
      </form>
    `;

    formRow.appendChild(formCell);

    // Insert the form after the review row
    reviewRow.parentNode.insertBefore(formRow, reviewRow.nextSibling);

    // Focus on the textarea
    const textarea = formRow.querySelector("textarea");
    textarea.focus();

    // Add event listeners
    const form = formRow.querySelector("form");
    form.addEventListener("submit", handleQuickReplySubmit);

    const cancelBtn = formRow.querySelector(".cancel-reply");
    cancelBtn.addEventListener("click", function () {
      formRow.remove();
    });
  }
});

// Handle quick reply submit
function handleQuickReplySubmit(e) {
  e.preventDefault();

  const form = e.target;
  const reviewId = form.getAttribute("data-review-id");
  const responseText = form.querySelector("textarea").value;

  if (!responseText.trim()) {
    alert("Please enter a response");
    return;
  }

  // Send the response to the server
  fetch("/seller/api/review-response", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      review_id: reviewId,
      response: responseText,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        console.log("Response saved successfully:", data);

        // Update the status badge
        const reviewRow = document.querySelector(
          `tr[data-review-id="${reviewId}"]`
        );
        if (reviewRow) {
          const statusBadge = reviewRow.querySelector(".status-badge");
          if (statusBadge) {
            statusBadge.className = "status-badge responded";
            statusBadge.textContent = "Responded";
          }
        }

        // Remove the form
        const formRow = document.getElementById(`quick-reply-form-${reviewId}`);
        if (formRow) {
          formRow.remove();
        }

        // Show success notification
        showNotification("Response saved successfully", "success");
      } else {
        console.error("Error saving response:", data);
        showNotification("Failed to save response. Please try again.", "error");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showNotification("Failed to save response. Please try again.", "error");
    });
}
*/
