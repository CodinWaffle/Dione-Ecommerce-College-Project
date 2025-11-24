// Additional JavaScript specific to seller management
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

        // Action button functionality
        const viewButtons = document.querySelectorAll(".action-btn.view");
        viewButtons.forEach((button) => {
          button.addEventListener("click", function () {
            const row = this.closest("tr");
            const sellerName = row.querySelector(".seller-name").textContent;
            alert(`Viewing details for ${sellerName}`);
            // In a real implementation, this would open a modal with seller details
          });
        });

        const approveButtons = document.querySelectorAll(".action-btn.approve");
        approveButtons.forEach((button) => {
          button.addEventListener("click", function () {
            const row = this.closest("tr");
            const sellerName = row.querySelector(".seller-name").textContent;
            if (confirm(`Are you sure you want to approve ${sellerName}?`)) {
              // In a real implementation, this would call an API to approve the seller
              alert(`${sellerName} has been approved!`);
            }
          });
        });

        // Warning and suspension functionality
        const warnButtons = document.querySelectorAll(".action-btn.warn");
        warnButtons.forEach((button) => {
          button.addEventListener("click", function () {
            const row = this.closest("tr");
            const sellerName = row.querySelector(".seller-name").textContent;
            if (
              confirm(
                `Are you sure you want to issue a warning to ${sellerName}?`
              )
            ) {
              // In a real implementation, this would open a modal to compose a warning
              alert(`Warning issued to ${sellerName}`);
            }
          });
        });

        const suspendButtons = document.querySelectorAll(".action-btn.suspend");
        suspendButtons.forEach((button) => {
          button.addEventListener("click", function () {
            const row = this.closest("tr");
            const sellerName = row.querySelector(".seller-name").textContent;
            if (
              confirm(
                `Are you sure you want to suspend ${sellerName}? This will temporarily disable their account.`
              )
            ) {
              // In a real implementation, this would call an API to suspend the seller
              alert(`${sellerName} has been suspended`);
            }
          });
        });
      });