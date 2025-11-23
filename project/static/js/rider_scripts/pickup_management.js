// Pickup Management Page JS

document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".mark-picked-up-btn").forEach((button) => {
    button.addEventListener("click", async function () {
      const row = this.closest("tr");
      const pickupId = row.dataset.pickupId;

      if (confirm(`Mark pickup ${pickupId} as Picked Up?`)) {
        // In a real application, you would send this to your backend
        console.log(`Marking pickup ${pickupId} as Picked Up`);
        // Simulate API call
        await new Promise((resolve) => setTimeout(resolve, 500));

        // Update UI
        const statusBadge = row.querySelector(".status-badge");
        if (statusBadge) {
          statusBadge.textContent = "Picked Up";
          statusBadge.className = "status-badge status-picked-up";
        }
        // Replace button with 'View Proof' or similar
        this.outerHTML = `
          <button class="action-btn view-proof-btn" title="View Proof">
            <span class="material-symbols-outlined">visibility</span>
          </button>
        `;
        alert(`Pickup ${pickupId} marked as Picked Up!`);
      }
    });
  });

  // Add search functionality for pickups if needed
});
