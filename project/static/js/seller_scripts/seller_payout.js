// Seller Payout JavaScript
document.addEventListener("DOMContentLoaded", function () {
  // Sample data - in a real app, this would come from the server
  const balanceData = {
    availableBalance: 12850.75,
    totalEarned: 18750.25,
    pendingClearance: 2450.5,
    previouslyWithdrawn: 3449.0,
  };

  const withdrawalHistory = [
    {
      date: "2025-10-15",
      reference: "WD-78945612",
      amount: 1500.0,
      method: "GCash",
      status: "completed",
    },
    {
      date: "2025-09-30",
      reference: "WD-12378945",
      amount: 950.0,
      method: "Bank Transfer (BPI)",
      status: "completed",
    },
    {
      date: "2025-09-15",
      reference: "WD-65432178",
      amount: 999.0,
      method: "PayMaya",
      status: "completed",
    },
  ];

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat("en-PH", {
      style: "currency",
      currency: "PHP",
      minimumFractionDigits: 2,
    })
      .format(amount)
      .replace("PHP", "₱");
  };

  // Initialize balance card
  const initBalanceCard = () => {
    document.getElementById("availableBalance").textContent =
      balanceData.availableBalance.toFixed(2);
    document.getElementById("totalEarned").textContent = formatCurrency(
      balanceData.totalEarned
    );
    document.getElementById("pendingClearance").textContent = formatCurrency(
      balanceData.pendingClearance
    );
    document.getElementById("previouslyWithdrawn").textContent = formatCurrency(
      balanceData.previouslyWithdrawn
    );
  };

  // Initialize withdrawal history table
  const initWithdrawalTable = () => {
    const tableBody = document.getElementById("withdrawalsTable");

    if (withdrawalHistory.length === 0) {
      tableBody.innerHTML =
        '<tr><td colspan="5" class="empty-table">No withdrawal records found</td></tr>';
      return;
    }

    tableBody.innerHTML = "";

    withdrawalHistory.forEach((withdrawal) => {
      const row = document.createElement("tr");
      const formattedDate = new Date(withdrawal.date).toLocaleDateString(
        "en-US",
        {
          year: "numeric",
          month: "short",
          day: "numeric",
        }
      );

      row.innerHTML = `
        <td>${formattedDate}</td>
        <td>${withdrawal.reference}</td>
        <td>${formatCurrency(withdrawal.amount)}</td>
        <td>${withdrawal.method}</td>
        <td><span class="status-badge ${withdrawal.status}">${
        withdrawal.status.charAt(0).toUpperCase() + withdrawal.status.slice(1)
      }</span></td>
      `;

      tableBody.appendChild(row);
    });
  };

  // Handle payment method selection
  const initPaymentMethodSelection = () => {
    const paymentMethodSelect = document.getElementById("paymentMethod");
    const bankFields = document.getElementById("bankFields");
    const ewalletFields = document.getElementById("ewalletFields");

    paymentMethodSelect.addEventListener("change", function () {
      // Hide all payment specific fields first
      bankFields.classList.add("hidden");
      ewalletFields.classList.add("hidden");

      // Show relevant fields based on selection
      if (this.value === "bank") {
        bankFields.classList.remove("hidden");
      } else if (this.value === "gcash" || this.value === "paymaya") {
        ewalletFields.classList.remove("hidden");
      }
    });
  };

  // Form submission handling
  const initFormSubmission = () => {
    const form = document.getElementById("withdrawalForm");
    const availableBalanceElem = document.getElementById("availableBalance");

    form.addEventListener("submit", function (e) {
      e.preventDefault();

      const withdrawalAmount = parseFloat(
        document.getElementById("withdrawalAmount").value
      );
      const availableBalance = parseFloat(availableBalanceElem.textContent);
      const paymentMethod = document.getElementById("paymentMethod").value;

      // Validation
      if (withdrawalAmount < 500) {
        alert("Minimum withdrawal amount is ₱500.00");
        return;
      }

      if (withdrawalAmount > availableBalance) {
        alert("Withdrawal amount cannot exceed your available balance");
        return;
      }

      if (!paymentMethod) {
        alert("Please select a payment method");
        return;
      }

      // Payment method specific validation
      if (paymentMethod === "bank") {
        const bankName = document.getElementById("bankName").value;
        const accountNumber = document.getElementById("accountNumber").value;
        const accountName = document.getElementById("accountName").value;

        if (!bankName || !accountNumber || !accountName) {
          alert("Please complete all bank details");
          return;
        }
      } else if (paymentMethod === "gcash" || paymentMethod === "paymaya") {
        const mobileNumber = document.getElementById("mobileNumber").value;
        const ewalletName = document.getElementById("ewalletName").value;

        if (!mobileNumber || !ewalletName) {
          alert("Please complete all e-wallet details");
          return;
        }
      }

      // Show success message
      alert(
        `Withdrawal request for ${formatCurrency(
          withdrawalAmount
        )} submitted successfully! Your funds will be processed within 1-3 business days.`
      );

      // In a real app, you would send this data to the server
      // and handle the response appropriately

      // Reset form (for demo purposes)
      form.reset();
      bankFields.classList.add("hidden");
      ewalletFields.classList.add("hidden");
    });
  };

  // Initialize everything
  initBalanceCard();
  initWithdrawalTable();
  initPaymentMethodSelection();
  initFormSubmission();
});
