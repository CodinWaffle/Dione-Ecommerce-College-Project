/* Accessories-specific carousel functionality */

console.log("Accessories carousel module loaded");
class AccessoriesCarouselController {
  constructor() {
    this.wrapper = document.getElementById("carouselWrapper");
    this.prevBtn = document.getElementById("prevBtn");
    this.nextBtn = document.getElementById("nextBtn");
    this.cards = document.querySelectorAll(".card");
    this.init();
  }

  init() {
    this.cards.forEach((card) => {
      card.addEventListener("click", () => {
        const category = card.dataset.category;
        this.showSubcarousel(category);
      });
    });
    const back = document.getElementById("backToMain");
    if (back) back.addEventListener("click", () => this.backToMain());
  }

  showSubcarousel(category) {
    const wrapper = this.wrapper;
    const prev = this.prevBtn;
    const next = this.nextBtn;
    const back = document.getElementById("backToMain");
    const subcontainer = document.getElementById("subcarousels");
    if (!subcontainer) return;

    if (wrapper) wrapper.style.display = "none";
    if (prev) prev.style.display = "none";
    if (next) next.style.display = "none";

    const sub = subcontainer.querySelector(
      `.subcarousel[data-category="${category}"]`
    );
    if (sub) sub.style.display = "block";
    subcontainer.style.display = "block";
    if (back) back.style.display = "inline-block";
  }

  backToMain() {
    const wrapper = this.wrapper;
    const prev = this.prevBtn;
    const next = this.nextBtn;
    const back = document.getElementById("backToMain");
    const subcontainer = document.getElementById("subcarousels");

    if (subcontainer) {
      subcontainer.style.display = "none";
      subcontainer
        .querySelectorAll(".subcarousel")
        .forEach((s) => (s.style.display = "none"));
    }
    if (wrapper) wrapper.style.display = "";
    if (prev) prev.style.display = "";
    if (next) next.style.display = "";
    if (back) back.style.display = "none";
    if (window.removeDynamicBreadcrumb) window.removeDynamicBreadcrumb();
  }
}

document.addEventListener(
  "DOMContentLoaded",
  () => new AccessoriesCarouselController()
);
