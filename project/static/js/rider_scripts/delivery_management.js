// Delivery Management Page JS

document.addEventListener("DOMContentLoaded", function () {
  // Proof of Delivery Modal Logic
  const proofOfDeliveryModal = document.getElementById("proofOfDeliveryModal");
  const closeButton = proofOfDeliveryModal.querySelector(".close-button");
  const proofOfDeliveryForm = document.getElementById("proofOfDeliveryForm");
  const modalDeliveryIdInput = document.getElementById("modalDeliveryId");

  document.querySelectorAll(".proof-btn").forEach((button) => {
    button.addEventListener("click", function () {
      const deliveryId = this.closest("tr").dataset.deliveryId;
      modalDeliveryIdInput.value = deliveryId;
      proofOfDeliveryModal.style.display = "block";
    });
  });

  closeButton.addEventListener("click", function () {
    proofOfDeliveryModal.style.display = "none";
  });

  window.addEventListener("click", function (event) {
    if (event.target == proofOfDeliveryModal) {
      proofOfDeliveryModal.style.display = "none";
    }
  });

  proofOfDeliveryForm.addEventListener("submit", function (event) {
    event.preventDefault();
    const deliveryId = modalDeliveryIdInput.value;
    const photo = document.getElementById("photoUpload").files[0];
    const signature = document.getElementById("customerSignature").value;
    const notes = document.getElementById("deliveryNotes").value;

    // In a real application, you would send this data to your backend
    console.log(`Submitting proof for delivery ${deliveryId}:`);
    console.log("Photo:", photo ? photo.name : "No photo");
    console.log("Signature:", signature);
    console.log("Notes:", notes);

    alert("Proof of delivery submitted! (Demo)");
    proofOfDeliveryModal.style.display = "none";
    // Optionally update the delivery status to 'Delivered' here
    updateDeliveryStatusUI(deliveryId, "Delivered");
  });

  // Status Update Dropdown Logic
  document.querySelectorAll(".status-dropdown-content a").forEach((link) => {
    link.addEventListener("click", async function (event) {
      event.preventDefault();
      const newStatus = this.dataset.status;
      const deliveryId = this.closest("tr").dataset.deliveryId;

      try {
        const response = await fetch(`/api/delivery/${deliveryId}/status`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ status: newStatus }),
        });
        const data = await response.json();
        if (data.success) {
          updateDeliveryStatusUI(deliveryId, newStatus);
          alert(`Delivery ${deliveryId} status updated to ${newStatus}`);
        } else {
          alert(`Failed to update status: ${data.message}`);
        }
      } catch (error) {
        console.error("Error updating delivery status:", error);
        alert("An error occurred while updating status.");
      }
    });
  });

  function updateDeliveryStatusUI(deliveryId, newStatus) {
    const row = document.querySelector(`tr[data-delivery-id="${deliveryId}"]`);
    if (row) {
      const statusBadge = row.querySelector(".status-badge");
      if (statusBadge) {
        statusBadge.textContent = newStatus;
        statusBadge.className = `status-badge status-${newStatus
          .toLowerCase()
          .replace(" ", "-")}`;
      }
    }
  }

  // Search input (similar to job_list.js, but for deliveries)
  const deliverySearchInput = document.getElementById("deliverySearchInput");
  if (deliverySearchInput) {
    deliverySearchInput.addEventListener("input", function () {
      // Implement search logic for deliveries here if needed
      console.log("Searching deliveries:", deliverySearchInput.value);
    });
  }
});
