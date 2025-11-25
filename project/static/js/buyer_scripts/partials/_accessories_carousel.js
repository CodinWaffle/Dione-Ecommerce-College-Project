// JS for _accessories_carousel.html

class AccessoriesCarousel {
  constructor() {
    // Use more specific selectors to avoid conflicts
    const container = document.querySelector(
      ".carousel-container:not(.subcarousel)"
    );
    if (!container) return;

    this.wrapper = container.querySelector("#carouselWrapper");
    this.prevBtn = container.querySelector("#prevBtn");
    this.nextBtn = container.querySelector("#nextBtn");
    this.cards = container.querySelectorAll(".card");
    this.currentIndex = 0;
    this.cardsToShow = 5;
    this.cardWidth = 320;
    this.cardGap = 20;
    this.maxIndex = Math.max(0, this.cards.length - this.cardsToShow);

    this.init();
    this.updateResponsiveSettings();
    window.addEventListener("resize", () => this.updateResponsiveSettings());
  }

  init() {
    if (!this.wrapper || !this.prevBtn || !this.nextBtn) return;

    this.prevBtn.addEventListener("click", (e) => {
      e.preventDefault();
      this.prev();
    });
    this.nextBtn.addEventListener("click", (e) => {
      e.preventDefault();
      this.next();
    });
    this.updateButtons();

    this.cards.forEach((card) => {
      card.addEventListener("click", () => {
        const category = card.dataset.category;
        console.log(`Clicked on ${category}`);
        // Navigate to specific accessory category pages
        if (category === "bags") {
          window.location.href = "/shop/accessories/bags";
        } else if (category === "jewelry") {
          window.location.href = "/shop/accessories/jewelry";
        } else if (category === "hair-accessories") {
          window.location.href = "/shop/accessories/hair-accessories";
        } else if (category === "belts") {
          window.location.href = "/shop/accessories/belts";
        } else if (category === "scarves-wraps") {
          window.location.href = "/shop/accessories/scarves-&-wraps";
        } else if (category === "hats-caps") {
          window.location.href = "/shop/accessories/hats-&-caps";
        } else if (category === "eyewear") {
          window.location.href = "/shop/accessories/eyewear";
        } else if (category === "watches") {
          window.location.href = "/shop/accessories/watches";
        } else if (category === "gloves") {
          window.location.href = "/shop/accessories/gloves";
        } else if (category === "others") {
          window.location.href = "/shop/accessories/others";
        } else {
          console.log(`Navigation for ${category} not implemented yet`);
        }
      });
    });
  }

  updateResponsiveSettings() {
    if (!this.wrapper || !this.cards.length) return;
    
    // Get the actual viewport width (excluding padding)
    const viewportWidth = this.wrapper.parentElement.offsetWidth - 120; // Account for padding

    if (viewportWidth <= 400) {
      this.cardsToShow = 1;
      this.cardWidth = 280;
    } else if (viewportWidth <= 720) {
      this.cardsToShow = 2;
      this.cardWidth = 320;
    } else if (viewportWidth <= 1080) {
      this.cardsToShow = 3;
      this.cardWidth = 320;
    } else if (viewportWidth <= 1400) {
      this.cardsToShow = 4;
      this.cardWidth = 320;
    } else {
      this.cardsToShow = 5;
      this.cardWidth = 320;
    }

    // Calculate how many cards can fit in the viewport
    const totalCardWidth = this.cardWidth + this.cardGap;
    const actualCardsToShow = Math.floor(viewportWidth / totalCardWidth);
    this.cardsToShow = Math.max(1, Math.min(this.cardsToShow, actualCardsToShow));

    // Calculate max index - ensure last card is fully visible
    this.maxIndex = Math.max(0, this.cards.length - this.cardsToShow);
    
    // Ensure current index doesn't exceed max
    this.currentIndex = Math.min(this.currentIndex, this.maxIndex);
    this.updateCarousel();
  }

  prev() {
    if (!this.cards || this.cards.length === 0) return;
    if (this.currentIndex > 0) {
      this.currentIndex--;
      this.updateCarousel();
    }
  }

  next() {
    if (!this.cards || this.cards.length === 0) return;
    if (this.currentIndex < this.maxIndex) {
      this.currentIndex++;
      this.updateCarousel();
    }
  }

  updateCarousel() {
    const translateX = -(this.currentIndex * (this.cardWidth + this.cardGap));
    this.wrapper.style.transform = `translateX(${translateX}px)`;
    this.updateButtons();
  }

  updateButtons() {
    if (!this.prevBtn || !this.nextBtn) return;
    
    // Disable prev button when at the beginning
    this.prevBtn.disabled = this.currentIndex === 0;
    
    // Disable next button when at the end
    this.nextBtn.disabled = this.currentIndex >= this.maxIndex;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  new AccessoriesCarousel();
});
