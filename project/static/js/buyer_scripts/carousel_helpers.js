// Generic helper to show subcarousels from any partial script
// Uses class toggles and a short lock to make transitions snappier and prevent duplicate clicks.
window._carouselTransitionLock = false;
window.showSubcarouselGlobal = function (category) {
  try {
    if (window._carouselTransitionLock) return;
    window._carouselTransitionLock = true;
    setTimeout(() => (window._carouselTransitionLock = false), 260);

    const wrapper = document.getElementById("carouselWrapper");
    const prev = document.getElementById("prevBtn");
    const next = document.getElementById("nextBtn");
    const back = document.getElementById("backToMain");
    const subcontainer = document.getElementById("subcarousels");
    if (!subcontainer) return;

    // hide main wrapper visually (use class so transitions can be GPU accelerated)
    if (wrapper) wrapper.classList.add("is-hidden");
    if (prev) prev.classList.add("is-hidden");
    if (next) next.classList.add("is-hidden");

    const sub = subcontainer.querySelector(
      `.subcarousel[data-category="${category}"]`
    );
    // ensure container is visible and mark sub as visible
    subcontainer.classList.add("is-visible");
    if (sub) {
      // trigger via rAF for smoother paint
      window.requestAnimationFrame(() => sub.classList.add("is-visible"));
    }

    if (back) back.classList.add("is-visible");
  } catch (err) {
    console.error("showSubcarouselGlobal error", err);
  }
};

// Restore breadcrumb to main category view (remove dynamic third item if exists)
window.removeDynamicBreadcrumb = function () {
  try {
    const breadcrumb = document.querySelector(".carousel-breadcrumb");
    if (!breadcrumb) return;
    // Remove separator and dynamic third breadcrumb item
    const items = breadcrumb.querySelectorAll(
      ".breadcrumb-separator, .breadcrumb-link"
    );
    if (items.length >= 4) {
      // Remove last two items (separator + subcategory link)
      items[items.length - 2].remove();
      items[items.length - 1].remove();
    }
  } catch (err) {
    console.error("removeDynamicBreadcrumb error", err);
  }
};

// Enhanced: when showing subcarousel, update the breadcrumb's third item (if exists)
// or append separator + subcategory to show: Home > Shoes > Heels
const originalShow = window.showSubcarouselGlobal;
window.showSubcarouselGlobal = function (category) {
  try {
    // call original behavior
    originalShow(category);

    const breadcrumb = document.querySelector(".carousel-breadcrumb");
    if (!breadcrumb) return;

    // Remove any prior dynamic breadcrumb items before appending new ones
    window.removeDynamicBreadcrumb();

    // determine display name: try to read from main carousel card title
    let displayName = null;
    const mainCardTitle = document.querySelector(
      `#carouselWrapper .card[data-category="${category}"] .card-title`
    );
    if (mainCardTitle) displayName = mainCardTitle.textContent.trim();

    if (!displayName) {
      // fallback: prettify the slug
      displayName = category
        .replace(/[-_]/g, " ")
        .replace(/\b\w/g, (c) => c.toUpperCase());
    }

    // create separator element (SVG) matching existing templates
    const sep = document.createElement("span");
    sep.className = "breadcrumb-separator";
    sep.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle">
        <path d="M6 12L10 8L6 4" stroke="#bbb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
      </svg>`;

    // create clickable anchor for the subcategory
    const link = document.createElement("a");
    link.className = "breadcrumb-link current";
    // try to build href from the existing main-category breadcrumb link
    const anchors = breadcrumb.querySelectorAll("a.breadcrumb-link");
    if (anchors && anchors.length >= 2) {
      // anchors[1] should be the main category (e.g. '/shop/shoes')
      let hrefBase = anchors[1].getAttribute("href") || "";
      hrefBase = hrefBase.replace(/\/$/, "");
      link.setAttribute("href", hrefBase + "/" + encodeURIComponent(category));
    } else {
      // fallback: link to '#'
      link.setAttribute("href", "#");
    }
    link.textContent = displayName;

    // Append separator and subcategory link to breadcrumb
    breadcrumb.appendChild(sep);
    breadcrumb.appendChild(link);

    // hide subcarousel's own breadcrumb if present
    const subcontainer = document.getElementById("subcarousels");
    if (subcontainer) {
      const sub = subcontainer.querySelector(
        `.subcarousel[data-category="${category}"]`
      );
      if (sub) {
        const subBreadcrumb = sub.querySelector(".carousel-breadcrumb");
        if (subBreadcrumb) subBreadcrumb.style.display = "none";
      }
    }
  } catch (err) {
    console.error("enhanced showSubcarouselGlobal error", err);
  }
};
