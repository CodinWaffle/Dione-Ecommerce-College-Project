// JS for _clothing_carousel.html

class ClothingCarousel {
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
        this.showSubcarousel(category);
      });
    });
  }

  showSubcarouselByElement(elem) {
    const category = elem.dataset.category;
    this.showSubcarousel(category);
  }

  showSubcarousel(category) {
    // hide main wrapper and nav buttons
    const wrapper = this.wrapper;
    const prev = this.prevBtn;
    const next = this.nextBtn;
    const back = document.getElementById("backToMain");
    const subcontainer = document.getElementById("subcarousels");

    if (!subcontainer) return;

    // hide main carousel and controls
    wrapper.style.display = "none";
    prev.style.display = "none";
    next.style.display = "none";

    // show requested subcarousel
    const sub = subcontainer.querySelector(
      `.subcarousel[data-category="${category}"]`
    );
    if (sub) {
      sub.style.display = "block";
      subcontainer.style.display = "block";
    } else {
      console.warn("No subcarousel for", category);
    }

    // show back button
    if (back) back.style.display = "inline-block";
    if (back && !back._bound) {
      back.addEventListener("click", () => this.backToMain());
      back._bound = true;
    }
  }

  backToMain() {
    const wrapper = this.wrapper;
    const prev = this.prevBtn;
    const next = this.nextBtn;
    const back = document.getElementById("backToMain");
    const subcontainer = document.getElementById("subcarousels");

    // hide all subcarousels
    if (subcontainer) {
      subcontainer.style.display = "none";
      const subs = subcontainer.querySelectorAll(".subcarousel");
      subs.forEach((s) => (s.style.display = "none"));
    }

    // show main carousel and controls
    wrapper.style.display = "";
    prev.style.display = "";
    next.style.display = "";

    if (back) back.style.display = "none";
    if (window.removeDynamicBreadcrumb) window.removeDynamicBreadcrumb();
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
    if (this.currentIndex > 0) {
      this.currentIndex--;
      this.updateCarousel();
    }
  }

  next() {
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
    this.prevBtn.disabled = this.currentIndex === 0;
    this.nextBtn.disabled = this.currentIndex >= this.maxIndex;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  new ClothingCarousel();
});
