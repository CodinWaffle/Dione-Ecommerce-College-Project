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
    let itemsToShow = getItemsToShow();
    let maxIndex = Math.max(0, items.length - itemsToShow);

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

      // In looping mode buttons remain active unless there is nothing to scroll
      const shouldDisable = maxIndex === 0;
      if (prevBtn) prevBtn.disabled = !!shouldDisable;
      if (nextBtn) nextBtn.disabled = !!shouldDisable;
    }

    if (prevBtn) {
      prevBtn.addEventListener("click", () => {
        if (items.length === 0) return;
        if (currentIndex > 0) {
          currentIndex--;
        } else {
          currentIndex = maxIndex;
        }
        updateCarousel();
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener("click", () => {
        if (items.length === 0) return;
        if (currentIndex < maxIndex) {
          currentIndex++;
        } else {
          currentIndex = 0;
        }
        updateCarousel();
      });
    }

    // Handle window resize
    let resizeTimeout;
    window.addEventListener("resize", () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        itemsToShow = getItemsToShow();
        maxIndex = Math.max(0, items.length - itemsToShow);
        if (currentIndex > maxIndex) {
          currentIndex = maxIndex;
        }
        updateCarousel();
      }, 250);
    });

    updateCarousel();
  });
}
