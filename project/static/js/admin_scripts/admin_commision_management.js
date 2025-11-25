// Additional JavaScript specific to commission management
      document.addEventListener("DOMContentLoaded", function () {
        // Tab switching functionality
        const tabButtons = document.querySelectorAll(".tab-btn");
        const tabContents = document.querySelectorAll(".tab-content");

        tabButtons.forEach((button) => {
          button.addEventListener("click", () => {
            // Remove active class from all buttons and contents
            tabButtons.forEach((btn) => btn.classList.remove("active"));
            tabContents.forEach((content) =>
              content.classList.remove("active")
            );

            // Add active class to clicked button and corresponding content
            button.classList.add("active");
            const tabId = button.getAttribute("data-tab");
            document.getElementById(tabId).classList.add("active");
          });
        });

        // Commission rate slider functionality
        const rateSlider = document.querySelector(".rate-slider");
        const rateDisplay = document.querySelector(".rate-display");

        if (rateSlider && rateDisplay) {
          rateSlider.addEventListener("input", function () {
            rateDisplay.textContent = this.value + "%";
          });
        }

        // Commission toggle switch
        const customRatesToggle = document.getElementById("customRatesToggle");

        if (customRatesToggle) {
          customRatesToggle.addEventListener("change", function () {
            // In a real app, this would show/hide category-specific rate settings
            const message = this.checked
              ? "Category-specific rates enabled. You can now set different rates for each category."
              : "Category-specific rates disabled. The global rate will apply to all categories.";

            alert(message);
          });
        }

        // Payout action buttons
        const processAllButton = document.querySelector(
          ".payout-card .payout-action"
        );
        if (processAllButton) {
          processAllButton.addEventListener("click", function () {
            const confirmProcess = confirm(
              "Are you sure you want to process all pending payouts? This will initiate transfers to 32 sellers."
            );

            if (confirmProcess) {
              alert("Processing payouts. This may take a few minutes.");
              // In a real app, this would call an API to process payouts
            }
          });
        } // Filter options functionality
        const filterOptions = document.querySelectorAll(".filter-option");
        filterOptions.forEach((option) => {
          option.addEventListener("click", () => {
            filterOptions.forEach((opt) => opt.classList.remove("active"));
            option.classList.add("active");
          });
        });

        // Time filter functionality
        const timeFilters = document.querySelectorAll(".time-filter button");
        timeFilters.forEach((button) => {
          button.addEventListener("click", () => {
            // Find parent time filter
            const parent = button.closest(".time-filter");
            if (parent) {
              // Remove active class from all siblings
              parent
                .querySelectorAll("button")
                .forEach((btn) => btn.classList.remove("active"));
            }
            // Add active to clicked button
            button.classList.add("active");
          });
        });

        // Select all checkbox functionality
        const selectAllCheckbox = document.querySelector(
          ".select-all-checkbox"
        );
        const rowCheckboxes = document.querySelectorAll(".row-checkbox");

        if (selectAllCheckbox) {
          selectAllCheckbox.addEventListener("change", () => {
            rowCheckboxes.forEach((checkbox) => {
              checkbox.checked = selectAllCheckbox.checked;
            });
          });
        }

        // Commission Rate Edit functionality
        const rateEditButtons = document.querySelectorAll(
          ".rate-actions .edit"
        );
        rateEditButtons.forEach((button) => {
          button.addEventListener("click", function () {
            const rateCard = this.closest(".commission-rate-card");
            const categoryName = rateCard.querySelector("h4").textContent;
            const currentRate =
              rateCard.querySelector(".rate-value").textContent;

            // In a real implementation, this would open a modal for editing
            const newRate = prompt(
              `Edit commission rate for ${categoryName} (currently ${currentRate}):`,
              currentRate
            );
            if (newRate !== null && newRate.trim() !== "") {
              // Update the displayed rate (in a real app, you'd save to database)
              rateCard.querySelector(".rate-value").textContent = newRate;
              // Update the "Last Updated" text
              const today = new Date();
              const dateStr = today.toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
                year: "numeric",
              });
              rateCard.querySelector(
                ".rate-details span:first-child"
              ).textContent = `Last Updated: ${dateStr}`;
            }
          });
        });

        // Payout Request Approval Functionality
        const approveButtons = document.querySelectorAll(".action-btn.approve");
        const rejectButtons = document.querySelectorAll(".action-btn.reject");
        const processButtons = document.querySelectorAll(".action-btn.process");

        // Approve functionality
        approveButtons.forEach((button) => {
          button.addEventListener("click", function () {
            const row = this.closest("tr");
            const type = row.querySelector(".type-badge").textContent.trim();
            const name = row.querySelectorAll("td")[1].textContent.trim();
            const amount = row.querySelectorAll("td")[4].textContent.trim();

            if (confirm(`Approve ${type} payout for ${name} (${amount})?`)) {
              // Update status badge
              const statusBadge = row.querySelector(".status-badge");
              statusBadge.className = "status-badge approved-badge";
              statusBadge.textContent = "Approved";

              // Replace action buttons
              const actionsCell = row.querySelector(
                "td:last-child .action-buttons"
              );
              actionsCell.innerHTML = `
                <button class="action-btn process" title="Process Payout">
                  <i class="bx bx-play-circle"></i>
                </button>
                <button class="action-btn view" title="View Details">
                  <i class="bx bx-show"></i>
                </button>
              `;

              // Re-attach process button listener
              attachProcessListener(
                actionsCell.querySelector(".action-btn.process")
              );
            }
          });
        });

        // Reject functionality
        rejectButtons.forEach((button) => {
          button.addEventListener("click", function () {
            const row = this.closest("tr");
            const type = row.querySelector(".type-badge").textContent.trim();
            const name = row.querySelectorAll("td")[1].textContent.trim();
            const amount = row.querySelectorAll("td")[4].textContent.trim();

            const reason = prompt(
              `Reject ${type} payout for ${name}? Please provide a reason:`,
              ""
            );
            if (reason !== null) {
              // Update status badge
              const statusBadge = row.querySelector(".status-badge");
              statusBadge.className = "status-badge rejected-badge";
              statusBadge.textContent = "Rejected";

              // Remove action buttons
              const actionsCell = row.querySelector(
                "td:last-child .action-buttons"
              );
              actionsCell.innerHTML = `
                <button class="action-btn view" title="View Details">
                  <i class="bx bx-show"></i>
                </button>
              `;
            }
          });
        });

        // Process payout functionality
        function attachProcessListener(button) {
          if (button) {
            button.addEventListener("click", function () {
              const row = this.closest("tr");
              const type = row.querySelector(".type-badge").textContent.trim();
              const name = row.querySelectorAll("td")[1].textContent.trim();
              const amount = row.querySelectorAll("td")[4].textContent.trim();

              if (confirm(`Process ${type} payout for ${name} (${amount})?`)) {
                // Update status badge
                const statusBadge = row.querySelector(".status-badge");
                statusBadge.className = "status-badge processing-badge";
                statusBadge.textContent = "Processing";

                // Disable action buttons
                const actionButtons = row.querySelectorAll(".action-btn");
                actionButtons.forEach((btn) => {
                  btn.classList.add("disabled");
                  btn.disabled = true;
                });

                // Show spinner
                const actionsCell = row.querySelector(
                  "td:last-child .action-buttons"
                );
                actionsCell.innerHTML = `
                  <button class="action-btn" title="Processing" disabled>
                    <i class="bx bx-loader-alt bx-spin"></i>
                  </button>
                `;

                // Simulate processing delay
                setTimeout(() => {
                  statusBadge.className = "status-badge completed-badge";
                  statusBadge.textContent = "Completed";
                  actionsCell.innerHTML = `
                    <button class="action-btn view" title="View Details">
                      <i class="bx bx-show"></i>
                    </button>
                  `;
                }, 2000);
              }
            });
          }
        }

        processButtons.forEach((button) => {
          attachProcessListener(button);
        });

        // Filter functionality
        const typeFilter = document.querySelector(
          ".filter-select:nth-of-type(1)"
        );
        const statusFilter = document.querySelector(
          ".filter-select:nth-of-type(2)"
        );
        const tableRows = document.querySelectorAll(
          ".payout-request-table tbody tr"
        );

        function filterTable() {
          const selectedType = typeFilter ? typeFilter.value : "all";
          const selectedStatus = statusFilter ? statusFilter.value : "all";

          tableRows.forEach((row) => {
            let typeMatch = true;
            let statusMatch = true;

            if (selectedType !== "all") {
              const rowType = row
                .querySelector(".type-badge")
                .textContent.toLowerCase();
              typeMatch = rowType.includes(selectedType);
            }

            if (selectedStatus !== "all") {
              const rowStatus = row
                .querySelector(".status-badge")
                .textContent.toLowerCase();
              statusMatch = rowStatus.includes(selectedStatus);
            }

            row.style.display = typeMatch && statusMatch ? "" : "none";
          });
        }

        if (typeFilter) typeFilter.addEventListener("change", filterTable);
        if (statusFilter) statusFilter.addEventListener("change", filterTable);
      });