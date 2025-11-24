// Rider Dashboard Page JS

document.addEventListener("DOMContentLoaded", function () {
  const onlineStatusToggle = document.getElementById("onlineStatusToggle");
  const currentStatusText = document.getElementById("currentStatusText");

  if (onlineStatusToggle && currentStatusText) {
    onlineStatusToggle.addEventListener("change", function () {
      const newStatus = this.checked ? "Online" : "Offline";
      updateRiderStatus(newStatus);
    });
  }
});

async function updateRiderStatus(status) {
  try {
    const response = await fetch("/api/rider-status", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: status }),
    });
    const data = await response.json();
    if (data.success) {
      currentStatusText.textContent = data.status;
      currentStatusText.className = `status-text status-${data.status.toLowerCase()}`;
    }
  } catch (error) {
    console.error("Error updating rider status:", error);
  }
}
