/* Carousel JavaScript */

document.addEventListener("DOMContentLoaded", function () {
  initCarousel();
});

function initCarousel() {
  const carousels = document.querySelectorAll(".carousel-container");

  carousels.forEach((carousel) => {
    const track = carousel.querySelector(".carousel-track");
    const prevBtn = carousel.querySelector(".carousel-btn.prev");
    const nextBtn = carousel.querySelector(".carousel-btn.next");
    const items = carousel.querySelectorAll(".carousel-item");

    if (!track || !items.length) return;

    let currentIndex = 0;
    const itemsToShow = getItemsToShow();
    const maxIndex = Math.max(0, items.length - itemsToShow);

    function getItemsToShow() {
      const width = window.innerWidth;
      if (width < 480) return 1;
      if (width < 768) return 2;
      if (width < 1024) return 3;
      return 4;
    }

    function updateCarousel() {
      const itemWidth = items[0].offsetWidth;
      const gap = 20;
      const offset = -(currentIndex * (itemWidth + gap));
      track.style.transform = `translateX(${offset}px)`;

      // Update button states
      if (prevBtn) prevBtn.disabled = currentIndex === 0;
      if (nextBtn) nextBtn.disabled = currentIndex >= maxIndex;
    }

    if (prevBtn) {
      prevBtn.addEventListener("click", () => {
        if (currentIndex > 0) {
          currentIndex--;
          updateCarousel();
        }
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener("click", () => {
        if (currentIndex < maxIndex) {
          currentIndex++;
          updateCarousel();
        }
      });
    }

    // Handle window resize
    let resizeTimeout;
    window.addEventListener("resize", () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        const newItemsToShow = getItemsToShow();
        const newMaxIndex = Math.max(0, items.length - newItemsToShow);
        if (currentIndex > newMaxIndex) {
          currentIndex = newMaxIndex;
        }
        updateCarousel();
      }, 250);
    });

    updateCarousel();
  });
}
