/* Shoes-specific carousel functionality */

console.log("Shoes carousel module loaded");

class ShoesCarouselController {
  constructor() {
    this.wrapper = document.getElementById("carouselWrapper");
    this.prevBtn = document.getElementById("prevBtn");
    this.nextBtn = document.getElementById("nextBtn");
    this.cards = document.querySelectorAll(".card");
    this.init();
  }

  init() {
    // lightweight click debounce to avoid double invocations and make transitions snappier
    this._clickLock = false;
    this.cards.forEach((card) => {
      card.addEventListener("click", () => {
        if (this._clickLock) return;
        this._clickLock = true;
        setTimeout(() => (this._clickLock = false), 300);
        const category = card.dataset.category;
        // delegate to global helper which performs class-based show/hide
        if (window.showSubcarouselGlobal) {
          window.showSubcarouselGlobal(category);
        } else {
          this.showSubcarousel(category);
        }
      });
    });
    const back = document.getElementById("backToMain");
    if (back) {
      back.addEventListener("click", () => this.backToMain());
    }
  }

  showSubcarousel(category) {
    // fallback behavior if helper not present
    if (window.showSubcarouselGlobal)
      return window.showSubcarouselGlobal(category);
    const wrapper = this.wrapper;
    const prev = this.prevBtn;
    const next = this.nextBtn;
    const back = document.getElementById("backToMain");
    const subcontainer = document.getElementById("subcarousels");
    if (!subcontainer) return;
    wrapper && wrapper.classList.add("is-hidden");
    prev && prev.classList.add("is-hidden");
    next && next.classList.add("is-hidden");
    subcontainer.classList.add("is-visible");
    const sub = subcontainer.querySelector(
      `.subcarousel[data-category="${category}"]`
    );
    if (sub) sub.classList.add("is-visible");
    back && back.classList.add("is-visible");
  }

  backToMain() {
    const wrapper = this.wrapper;
    const prev = this.prevBtn;
    const next = this.nextBtn;
    const back = document.getElementById("backToMain");
    const subcontainer = document.getElementById("subcarousels");

    if (subcontainer) {
      subcontainer.classList.remove("is-visible");
      subcontainer
        .querySelectorAll(".subcarousel")
        .forEach((s) => s.classList.remove("is-visible"));
    }
    wrapper && wrapper.classList.remove("is-hidden");
    prev && prev.classList.remove("is-hidden");
    next && next.classList.remove("is-hidden");
    back && back.classList.remove("is-visible");
    if (window.removeDynamicBreadcrumb) window.removeDynamicBreadcrumb();
  }
}

document.addEventListener("DOMContentLoaded", () => {
  // expose controller globally so per-partial scripts can trigger subcarousels
  window.shoesCarouselController = new ShoesCarouselController();
});
