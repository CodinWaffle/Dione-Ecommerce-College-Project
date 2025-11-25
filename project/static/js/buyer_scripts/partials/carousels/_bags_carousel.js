// JS for _bags_carousel.html

class BagsCarousel {
  constructor() {
    this.wrapper = document.getElementById("carouselWrapper");
    this.prevBtn = document.getElementById("prevBtn");
    this.nextBtn = document.getElementById("nextBtn");
    this.cards = document.querySelectorAll(".card");
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
        // For now, show alert - you can replace with actual navigation
        if (window.showSubcarouselGlobal) {
          window.showSubcarouselGlobal(category);
        } else if (
          window.shoesCarouselController &&
          typeof window.shoesCarouselController.showSubcarousel === "function"
        ) {
          window.shoesCarouselController.showSubcarousel(category);
        } else {
          console.log(`Subcarousel requested for ${category}`);
        }
        // Future implementation: window.location.href = `/shop/clothing/tops/${category}`;
      });
    });
  }

  updateResponsiveSettings() {
    const containerWidth = this.wrapper.parentElement.offsetWidth;

    if (containerWidth <= 400) {
      this.cardsToShow = 1;
      this.cardWidth = 280;
    } else if (containerWidth <= 720) {
      this.cardsToShow = 2;
      this.cardWidth = 320;
    } else if (containerWidth <= 1080) {
      this.cardsToShow = 3;
      this.cardWidth = 320;
    } else if (containerWidth <= 1400) {
      this.cardsToShow = 4;
      this.cardWidth = 320;
    } else {
      this.cardsToShow = 5;
      this.cardWidth = 320;
    }

    this.maxIndex = Math.max(0, this.cards.length - this.cardsToShow);
    this.currentIndex = Math.min(this.currentIndex, this.maxIndex);
    this.updateCarousel();
  }

  prev() {
    if (!this.cards || this.cards.length === 0) return;
    if (this.currentIndex > 0) {
      this.currentIndex--;
    } else {
      this.currentIndex = this.maxIndex;
    }
    this.updateCarousel();
  }

  next() {
    if (!this.cards || this.cards.length === 0) return;
    if (this.currentIndex < this.maxIndex) {
      this.currentIndex++;
    } else {
      this.currentIndex = 0;
    }
    this.updateCarousel();
  }

  updateCarousel() {
    const translateX = -(this.currentIndex * (this.cardWidth + this.cardGap));
    this.wrapper.style.transform = `translateX(${translateX}px)`;
    this.updateButtons();
  }

  updateButtons() {
    const shouldDisable = this.maxIndex === 0;
    if (this.prevBtn) this.prevBtn.disabled = !!shouldDisable;
    if (this.nextBtn) this.nextBtn.disabled = !!shouldDisable;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  new BagsCarousel();
});
