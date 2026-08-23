const slides = [...document.querySelectorAll(".slide")];
const currentSlideLabel = document.querySelector("#currentSlide");
const totalSlidesLabel = document.querySelector("#totalSlides");
const currentTitleLabel = document.querySelector("#currentTitle");
const progressBar = document.querySelector("#progressBar");
const slideDots = document.querySelector("#slideDots");
const previousButton = document.querySelector("#previousSlide");
const nextButton = document.querySelector("#nextSlide");
const openOverviewButton = document.querySelector("#openOverview");
const closeOverviewButton = document.querySelector("#closeOverview");
const overviewDialog = document.querySelector("#overviewDialog");
const overviewList = document.querySelector("#overviewList");
const toast = document.querySelector("#toast");

let activeIndex = 0;
let toastTimer;

function showToast(message) {
  if (!toast) return;
  window.clearTimeout(toastTimer);
  toast.textContent = message;
  toast.classList.add("is-visible");
  toastTimer = window.setTimeout(() => {
    toast.classList.remove("is-visible");
  }, 2200);
}

function setActiveSlide(index) {
  activeIndex = Math.max(0, Math.min(index, slides.length - 1));
  const slide = slides[activeIndex];
  const number = activeIndex + 1;

  currentSlideLabel.textContent = String(number).padStart(2, "0");
  currentTitleLabel.textContent = slide.dataset.title || `Slide ${number}`;
  progressBar.style.width = `${(number / slides.length) * 100}%`;

  [...slideDots.children].forEach((dot, dotIndex) => {
    const isActive = dotIndex === activeIndex;
    dot.classList.toggle("is-active", isActive);
    dot.setAttribute("aria-current", isActive ? "step" : "false");
  });

  previousButton.disabled = activeIndex === 0;
  nextButton.disabled = activeIndex === slides.length - 1;
  nextButton.setAttribute(
    "aria-label",
    activeIndex === slides.length - 1 ? "End of deck" : "Next slide"
  );
}

function goToSlide(index) {
  const safeIndex = Math.max(0, Math.min(index, slides.length - 1));
  slides[safeIndex].scrollIntoView({ behavior: "smooth", block: "start" });
  setActiveSlide(safeIndex);
}

function buildNavigation() {
  totalSlidesLabel.textContent = String(slides.length).padStart(2, "0");

  slides.forEach((slide, index) => {
    const number = index + 1;
    const title = slide.dataset.title || `Slide ${number}`;

    const dot = document.createElement("button");
    dot.type = "button";
    dot.className = "slide-dot";
    dot.setAttribute("aria-label", `Go to slide ${number}: ${title}`);
    dot.addEventListener("click", () => goToSlide(index));
    slideDots.append(dot);

    const item = document.createElement("li");
    const link = document.createElement("a");
    link.href = `#${slide.id}`;
    link.innerHTML = `
      <span class="overview-number">${String(number).padStart(2, "0")}</span>
      <span class="overview-copy">
        <strong>${title}</strong>
        <small>${slide.dataset.time || ""}</small>
      </span>
    `;
    link.addEventListener("click", () => overviewDialog.close());
    item.append(link);
    overviewList.append(item);
  });
}

function handleScoreChoice(button) {
  document.querySelectorAll("[data-score-choice]").forEach((choice) => {
    choice.setAttribute("aria-pressed", String(choice === button));
  });

  const score = button.querySelector("span").textContent;
  document.querySelector("#scoreFormula").textContent = `${button.dataset.vector} · [2, 1, 3] = ${score}`;
  document.querySelector("#scoreMeaning").textContent = button.dataset.explanation;
  showToast(`${button.dataset.word}: ${button.dataset.calculation}`);
}

buildNavigation();
setActiveSlide(0);

previousButton.addEventListener("click", () => goToSlide(activeIndex - 1));
nextButton.addEventListener("click", () => goToSlide(activeIndex + 1));

openOverviewButton.addEventListener("click", () => overviewDialog.showModal());
closeOverviewButton.addEventListener("click", () => overviewDialog.close());
overviewDialog.addEventListener("click", (event) => {
  if (event.target === overviewDialog) overviewDialog.close();
});

document.querySelectorAll("[data-score-choice]").forEach((button) => {
  button.addEventListener("click", () => handleScoreChoice(button));
});

document.addEventListener("keydown", (event) => {
  const tag = document.activeElement?.tagName;
  const isInteractive = ["INPUT", "TEXTAREA", "SELECT", "BUTTON", "A"].includes(tag);
  if (isInteractive || overviewDialog.open) return;

  if (["ArrowRight", "ArrowDown", "PageDown", " "].includes(event.key)) {
    event.preventDefault();
    goToSlide(activeIndex + 1);
  }

  if (["ArrowLeft", "ArrowUp", "PageUp"].includes(event.key)) {
    event.preventDefault();
    goToSlide(activeIndex - 1);
  }

  if (event.key === "Home") {
    event.preventDefault();
    goToSlide(0);
  }

  if (event.key === "End") {
    event.preventDefault();
    goToSlide(slides.length - 1);
  }
});

const observer = new IntersectionObserver(
  (entries) => {
    const visible = entries
      .filter((entry) => entry.isIntersecting)
      .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

    if (visible) {
      setActiveSlide(slides.indexOf(visible.target));
    }
  },
  { threshold: [0.45, 0.65, 0.85] }
);

slides.forEach((slide) => observer.observe(slide));
