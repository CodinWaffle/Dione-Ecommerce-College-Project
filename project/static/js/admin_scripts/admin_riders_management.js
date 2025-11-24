// Additional JavaScript specific to rider management
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

        // Image zoom functionality
        const zoomButtons = document.querySelectorAll(".image-zoom");
        zoomButtons.forEach((button) => {
          button.addEventListener("click", function () {
            const image = this.previousElementSibling.getAttribute("src");
            // Create modal for image preview
            const modal = document.createElement("div");
            modal.classList.add("zoom-modal");
            modal.innerHTML = `
              <div class="zoom-content">
                <span class="zoom-close">&times;</span>
                <img src="${image}" alt="Zoomed Image">
              </div>
            `;
            document.body.appendChild(modal);

            // Close modal functionality
            modal
              .querySelector(".zoom-close")
              .addEventListener("click", function () {
                document.body.removeChild(modal);
              });

            // Close on outside click
            modal.addEventListener("click", function (e) {
              if (e.target === modal) {
                document.body.removeChild(modal);
              }
            });
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

        // Rider approval actions
        const approveButtons = document.querySelectorAll(
          ".action-btn.approve:not(.disabled)"
        );
        approveButtons.forEach((button) => {
          button.addEventListener("click", function () {
            const row = this.closest("tr");
            const riderName = row.querySelector(".rider-name").textContent;

            if (
              confirm(
                `Are you sure you want to approve ${riderName} as a rider?`
              )
            ) {
              alert(`${riderName} has been approved and account activated.`);
              // In a real app, you would call an API to approve the rider
              row.remove(); // Remove from the pending list
            }
          });
        });

        const rejectButtons = document.querySelectorAll(".action-btn.reject");
        rejectButtons.forEach((button) => {
          button.addEventListener("click", function () {
            const row = this.closest("tr");
            const riderName = row.querySelector(".rider-name").textContent;

            if (
              confirm(
                `Are you sure you want to reject ${riderName}'s application?`
              )
            ) {
              alert(`${riderName}'s application has been rejected.`);
              // In a real app, you would call an API to reject the rider
              row.remove(); // Remove from the pending list
            }
          });
        });

        // Issue resolution actions
        const resolveButtons = document.querySelectorAll(
          ".issue-resolution .btn-primary"
        );
        resolveButtons.forEach((button) => {
          button.addEventListener("click", function () {
            const resolutionDropdown = this.previousElementSibling;
            const selectedValue = resolutionDropdown.value;
            const issueCard = this.closest(".issue-card");
            const riderName =
              issueCard.querySelector(".rider-name").textContent;

            if (!selectedValue) {
              alert("Please select a resolution method.");
              return;
            }

            let resolutionAction = "";
            switch (selectedValue) {
              case "warning":
                resolutionAction = "issued a warning to";
                break;
              case "training":
                resolutionAction = "scheduled additional training for";
                break;
              case "suspend":
                resolutionAction = "suspended";
                break;
              case "terminate":
                resolutionAction = "terminated partnership with";
                break;
            }

            if (
              confirm(
                `Are you sure you want to ${resolutionAction} ${riderName}?`
              )
            ) {
              alert(`Action completed: ${resolutionAction} ${riderName}`);
              // In a real app, you would call an API to apply the selected action

              // Update the issue status
              const statusBadge = issueCard.querySelector(".status-badge");
              statusBadge.className = "status-badge success";
              statusBadge.textContent = "Resolved";
            }
          });
        });

        // Process payment buttons
        const processPaymentButtons = document.querySelectorAll(
          ".action-btn.process"
        );
        processPaymentButtons.forEach((button) => {
          button.addEventListener("click", function () {
            const row = this.closest("tr");
            const riderName = row.querySelector(".rider-name").textContent;
            const paymentAmount =
              row.querySelector("td:nth-child(5)").textContent;

            if (
              confirm(`Process payment of ${paymentAmount} to ${riderName}?`)
            ) {
              alert(`Payment to ${riderName} has been processed successfully.`);
              // In a real app, you would call an API to process the payment

              // Update the status badge
              const statusBadge = row.querySelector(".status-badge");
              statusBadge.className = "status-badge success";
              statusBadge.textContent = "Paid";

              // Replace the process button with download button
              this.innerHTML = '<i class="bx bx-download"></i>';
              this.title = "Download Statement";
              this.className = "action-btn download";
            }
          });
        });
      });