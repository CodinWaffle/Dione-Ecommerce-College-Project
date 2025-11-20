// Progress bar controller used by seller product forms
(function () {
  function initProgressBar(containerId) {
    let currentStep = 1;
    const totalSteps = document.querySelectorAll(
      "#" + containerId + " .step"
    ).length;
    const container = document.getElementById(containerId);
    if (!container) return;

    // If the template set a default step via data attribute, use it
    const dataStep = parseInt(container.getAttribute("data-current-step"), 10);
    if (!isNaN(dataStep) && dataStep >= 1 && dataStep <= totalSteps) {
      currentStep = dataStep;
    }

    const progressFill = container.querySelector(".progress-line-fill");
    const steps = container.querySelectorAll(".step");
    const stepEls = Array.from(steps);

    function updateProgress() {
      const progressPercent = ((currentStep - 1) / (totalSteps - 1)) * 100;
      if (progressFill) progressFill.style.width = progressPercent + "%";

      stepEls.forEach((step, index) => {
        const stepNum = index + 1;
        step.classList.remove("active", "completed");
        if (stepNum < currentStep) step.classList.add("completed");
        else if (stepNum === currentStep) step.classList.add("active");
      });
    }

    // make steps clickable
    stepEls.forEach((step) => {
      step.addEventListener("click", () => {
        const n = parseInt(step.getAttribute("data-step")) || 1;
        currentStep = n;
        updateProgress();
      });
    });

    // expose simple API on container
    container.progressSet = (n) => {
      currentStep = Math.min(Math.max(1, n), totalSteps);
      updateProgress();
    };
    container.progressNext = () => {
      if (currentStep < totalSteps) {
        currentStep++;
        updateProgress();
      }
    };
    container.progressPrev = () => {
      if (currentStep > 1) {
        currentStep--;
        updateProgress();
      }
    };

    // initial paint
    updateProgress();
  }

  // auto-init default id if present
  document.addEventListener("DOMContentLoaded", function () {
    if (document.getElementById("productProgress"))
      initProgressBar("productProgress");
  });

  window.initProductProgressBar = initProgressBar;
})();
