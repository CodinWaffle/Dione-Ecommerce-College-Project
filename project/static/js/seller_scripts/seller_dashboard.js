// Initialize Lucide icons
document.addEventListener("DOMContentLoaded", function () {
  lucide.createIcons();
});

// DOM Elements
const sidebar = document.getElementById("sidebar");
const sidebarToggle = document.getElementById("sidebarToggle");
const navItems = document.querySelectorAll(".nav-item[data-page]");
const pageSections = document.querySelectorAll(".page-section");

// Sidebar Toggle
sidebarToggle.addEventListener("click", () => {
  sidebar.classList.remove("active");
});

// Navigation
navItems.forEach((item) => {
  item.addEventListener("click", (e) => {
    // Determine the page and whether it maps to an in-page section
    const page = item.getAttribute("data-page");
    const targetSection = document.getElementById(`${page}-section`);

    if (targetSection) {
      // It's an in-page section: prevent default anchor navigation and toggle views
      e.preventDefault();

      // Remove active class from all nav items
      navItems.forEach((nav) => nav.classList.remove("active"));

      // Add active class to clicked item
      item.classList.add("active");

      // Hide all sections and show the selected one
      pageSections.forEach((section) => section.classList.remove("active"));
      targetSection.classList.add("active");

      // Close sidebar on mobile after navigation
      if (window.innerWidth <= 768) {
        sidebar.classList.remove("active");
      }

      // Reinitialize icons for dynamically shown content
      try {
        lucide.createIcons();
      } catch (err) {
        /* ignore */
      }
    } else {
      // No in-page section - allow the anchor to follow its href to a server route.
      // Ensure active class updates for visual feedback; don't prevent navigation.
      navItems.forEach((nav) => nav.classList.remove("active"));
      item.classList.add("active");
      // No further JS interception so the browser will navigate to the href.
    }
  });
});

// Simple Chart Simulation (you can replace this with Chart.js or any other library)
function drawSimpleChart() {
  const canvas = document.getElementById("revenueChart");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  const width = canvas.parentElement.clientWidth;
  const height = 300;

  canvas.width = width;
  canvas.height = height;

  // Sample data
  const data = [3200, 4100, 3800, 5200, 4800, 6100, 5800];
  const labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const max = Math.max(...data);
  const padding = 40;
  const chartHeight = height - padding * 2;
  const chartWidth = width - padding * 2;
  const barWidth = chartWidth / data.length;

  // Clear canvas
  ctx.clearRect(0, 0, width, height);

  // Create gradient
  const gradient = ctx.createLinearGradient(0, 0, 0, height);
  gradient.addColorStop(0, "#8b5cf6");
  gradient.addColorStop(1, "#6d28d9");

  // Draw bars
  data.forEach((value, index) => {
    const barHeight = (value / max) * chartHeight;
    const x = padding + index * barWidth + barWidth * 0.2;
    const y = height - padding - barHeight;
    const w = barWidth * 0.6;

    // Draw bar with rounded top
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.roundRect(x, y, w, barHeight, [8, 8, 0, 0]);
    ctx.fill();

    // Add subtle shadow
    ctx.shadowColor = "rgba(0, 0, 0, 0.1)";
    ctx.shadowBlur = 10;
    ctx.shadowOffsetY = 4;

    // Draw label
    ctx.fillStyle = "#737373";
    ctx.font = "12px Poppins";
    ctx.textAlign = "center";
    ctx.fillText(labels[index], x + w / 2, height - padding + 20);

    // Draw value
    ctx.fillStyle = "#171717";
    ctx.font = "600 11px Poppins";
    ctx.fillText("$" + value, x + w / 2, y - 8);

    ctx.fillStyle = "#8b5cf6";
  });
}

// Initialize chart on load
window.addEventListener("load", () => {
  drawSimpleChart();
  lucide.createIcons();
});

// Redraw chart on window resize
let resizeTimeout;
window.addEventListener("resize", () => {
  clearTimeout(resizeTimeout);
  resizeTimeout = setTimeout(() => {
    drawSimpleChart();
  }, 250);
});

// Simulate real-time updates (optional)
function simulateRealtimeUpdates() {
  // Update notification badges randomly
  setInterval(() => {
    const badges = document.querySelectorAll(".badge");
    badges.forEach((badge) => {
      const currentValue = Number.parseInt(badge.textContent);
      const newValue = Math.max(
        0,
        currentValue + Math.floor(Math.random() * 3) - 1
      );
      badge.textContent = newValue;
      if (newValue === 0) {
        badge.style.display = "none";
      } else {
        badge.style.display = "block";
      }
    });
  }, 10000);
}

// Start real-time updates
simulateRealtimeUpdates();

// Handle logout
document.querySelector('a[href="#logout"]')?.addEventListener("click", (e) => {
  e.preventDefault();
  if (confirm("Are you sure you want to logout?")) {
    alert("Logout functionality would be implemented here");
  }
});

// Handle support
document.querySelector('a[href="#support"]')?.addEventListener("click", (e) => {
  e.preventDefault();
  alert("Support page would be implemented here");
});
