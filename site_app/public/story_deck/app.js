(() => {
  "use strict";

  const presentationOrder = [
    "slide-1", "slide-2", "slide-3", "slide-3-training", "slide-4", "slide-5", "slide-6", "slide-7", "slide-8",
    "slide-16", "slide-case-studies", "slide-24", "slide-opioid-open", "slide-opioid-problem", "slide-opioid-scale",
    "slide-opioid-material", "slide-opioid-direct-path", "slide-opioid-vector-space", "slide-opioid-retrieval-results", "slide-rag-starter-data", "slide-rag-starter-build", "slide-rag-starter-prompts", "slide-opioid-close",
    ...Array.from({ length: 7 }, (_, index) => `slide-${index + 9}`),
  ];
  const slideContainer = document.querySelector("main");
  presentationOrder.forEach((slideId) => {
    const slide = document.getElementById(slideId);
    if (slide) slideContainer.append(slide);
  });

  const slides = [...document.querySelectorAll(".slide")];
  const currentSlide = document.querySelector("#currentSlide");
  const totalSlides = document.querySelector("#totalSlides");
  const currentTitle = document.querySelector("#currentTitle");
  const progressBar = document.querySelector("#progressBar");
  const slideDots = document.querySelector("#slideDots");
  const previousButton = document.querySelector("#previousSlide");
  const nextButton = document.querySelector("#nextSlide");
  const notesButton = document.querySelector("#toggleNotes");
  const overviewButton = document.querySelector("#openOverview");
  const overviewDialog = document.querySelector("#overviewDialog");
  const closeOverview = document.querySelector("#closeOverview");
  const overviewList = document.querySelector("#overviewList");
  const toast = document.querySelector("#toast");
  let activeIndex = 0;
  let toastTimer;

  const twoDigits = (value) => String(value).padStart(2, "0");

  function announce(message) {
    window.clearTimeout(toastTimer);
    toast.textContent = message;
    toast.classList.add("is-visible");
    toastTimer = window.setTimeout(() => toast.classList.remove("is-visible"), 1700);
  }

  function setActiveSlide(index) {
    const boundedIndex = Math.max(0, Math.min(index, slides.length - 1));
    activeIndex = boundedIndex;

    slides.forEach((slide, slideIndex) => {
      slide.classList.toggle("is-active", slideIndex === boundedIndex);
    });

    [...slideDots.children].forEach((dot, dotIndex) => {
      dot.classList.toggle("is-active", dotIndex === boundedIndex);
      if (dotIndex === boundedIndex) {
        dot.setAttribute("aria-current", "page");
      } else {
        dot.removeAttribute("aria-current");
      }
    });

    const slide = slides[boundedIndex];
    currentSlide.textContent = twoDigits(boundedIndex + 1);
    currentTitle.textContent = slide.dataset.title;
    progressBar.style.width = `${((boundedIndex + 1) / slides.length) * 100}%`;
    previousButton.disabled = boundedIndex === 0;
    nextButton.disabled = boundedIndex === slides.length - 1;
    document.title = `${twoDigits(boundedIndex + 1)} · ${slide.dataset.title} — Applied AI: From Language Models to RAG`;
  }

  function goToSlide(index) {
    const boundedIndex = Math.max(0, Math.min(index, slides.length - 1));
    slides[boundedIndex].scrollIntoView({ behavior: "smooth", block: "start" });
    setActiveSlide(boundedIndex);
  }

  function toggleNotes(force) {
    const visible = typeof force === "boolean"
      ? force
      : !document.body.classList.contains("notes-visible");
    document.body.classList.toggle("notes-visible", visible);
    notesButton.setAttribute("aria-pressed", String(visible));
    notesButton.textContent = visible ? "Hide notes" : "Notes";
    announce(visible ? "Presenter notes on" : "Presenter notes off");
  }

  slides.forEach((slide, index) => {
    const dot = document.createElement("a");
    dot.href = `#${slide.id}`;
    dot.setAttribute("aria-label", `Slide ${index + 1}: ${slide.dataset.title}`);
    dot.addEventListener("click", () => setActiveSlide(index));
    slideDots.append(dot);

    const item = document.createElement("li");
    const link = document.createElement("a");
    const title = document.createElement("strong");
    const time = document.createElement("time");
    link.href = `#${slide.id}`;
    title.textContent = slide.dataset.title;
    time.textContent = slide.dataset.time;
    link.append(title, time);
    link.addEventListener("click", () => {
      overviewDialog.close();
      setActiveSlide(index);
    });
    item.append(link);
    overviewList.append(item);
  });

  totalSlides.textContent = twoDigits(slides.length);
  const requestedSlideIndex = slides.findIndex((slide) => `#${slide.id}` === window.location.hash);
  const initialSlideIndex = requestedSlideIndex >= 0 ? requestedSlideIndex : 0;
  setActiveSlide(initialSlideIndex);
  if (requestedSlideIndex >= 0) {
    const positionRequestedSlide = () => window.setTimeout(() => {
      slides[initialSlideIndex].scrollIntoView({ block: "start" });
      setActiveSlide(initialSlideIndex);
    }, 0);
    if (document.readyState === "complete") {
      positionRequestedSlide();
    } else {
      window.addEventListener("load", positionRequestedSlide, { once: true });
    }
  }

  previousButton.addEventListener("click", () => goToSlide(activeIndex - 1));
  nextButton.addEventListener("click", () => goToSlide(activeIndex + 1));
  notesButton.addEventListener("click", () => toggleNotes());

  overviewButton.addEventListener("click", () => overviewDialog.showModal());
  closeOverview.addEventListener("click", () => overviewDialog.close());
  overviewDialog.addEventListener("click", (event) => {
    if (event.target === overviewDialog) overviewDialog.close();
  });

  const observer = new IntersectionObserver((entries) => {
    const visibleSlides = entries
      .filter((entry) => entry.isIntersecting)
      .sort((first, second) => second.intersectionRatio - first.intersectionRatio);
    if (!visibleSlides.length) return;
    const index = slides.indexOf(visibleSlides[0].target);
    if (index >= 0) setActiveSlide(index);
  }, { threshold: [0.4, 0.58, 0.75] });

  slides.forEach((slide) => observer.observe(slide));

  document.addEventListener("keydown", (event) => {
    const interactive = event.target.closest("button, a, input, textarea, select, [contenteditable='true']");
    if (overviewDialog.open) {
      if (event.key === "Escape") overviewDialog.close();
      return;
    }

    if ((event.key === "n" || event.key === "N") && !interactive) {
      event.preventDefault();
      toggleNotes();
      return;
    }

    if (event.key === "Escape" && document.body.classList.contains("notes-visible")) {
      toggleNotes(false);
      return;
    }

    if (interactive) return;

    if (["ArrowRight", "ArrowDown", "PageDown", " "].includes(event.key)) {
      event.preventDefault();
      goToSlide(activeIndex + 1);
    } else if (["ArrowLeft", "ArrowUp", "PageUp"].includes(event.key)) {
      event.preventDefault();
      goToSlide(activeIndex - 1);
    } else if (event.key === "Home") {
      event.preventDefault();
      goToSlide(0);
    } else if (event.key === "End") {
      event.preventDefault();
      goToSlide(slides.length - 1);
    }
  });

  document.querySelectorAll("[data-score]").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll("[data-score]").forEach((candidate) => {
        candidate.setAttribute("aria-pressed", String(candidate === button));
      });
      document.querySelector("#scoreFormula").textContent = `${button.dataset.vector} · [2, 1, 3] = ${button.dataset.scoreValue}`;
      document.querySelector("#scoreExplanation").textContent = button.dataset.explanation;
      announce(`${button.dataset.word}: score ${button.dataset.scoreValue}`);
    });
  });

  const auditButtons = [...document.querySelectorAll("[data-audit]")];
  const reviewedClaims = new Set();
  const auditProgress = document.querySelector("#auditProgress");
  const auditExplanation = document.querySelector("#auditExplanation");

  auditButtons.forEach((button) => {
    button.addEventListener("click", () => {
      reviewedClaims.add(button);
      button.classList.add("is-revealed");
      button.setAttribute("aria-expanded", "true");
      button.querySelector(".audit-verdict").textContent = button.dataset.verdict;
      auditProgress.textContent = `${reviewedClaims.size} of ${auditButtons.length} claims reviewed`;
      auditExplanation.textContent = button.dataset.explanation;
      announce(button.dataset.verdict);
    });
  });

  document.querySelectorAll("[data-copy-prompt]").forEach((button) => {
    button.addEventListener("click", async () => {
      const target = button.dataset.copyTarget || "#researchPrompt";
      const prompt = document.querySelector(target).textContent.trim();
      try {
        await navigator.clipboard.writeText(prompt);
      } catch {
        const textarea = document.createElement("textarea");
        textarea.value = prompt;
        textarea.setAttribute("readonly", "");
        textarea.style.position = "fixed";
        textarea.style.opacity = "0";
        document.body.append(textarea);
        textarea.select();
        document.execCommand("copy");
        textarea.remove();
      }
      button.textContent = "Copied";
      announce("Prompt copied");
      window.setTimeout(() => {
        button.textContent = "Copy";
      }, 1600);
    });
  });

  const ragPromptTabs = [...document.querySelectorAll("[data-rag-prompt-tab]")];
  const ragPromptPanels = [...document.querySelectorAll("[data-rag-prompt-panel]")];
  const ragPromptPrevious = document.querySelector("#ragPromptPrevious");
  const ragPromptNext = document.querySelector("#ragPromptNext");
  const ragPromptCopy = document.querySelector("#ragPromptCopy");
  const ragPromptPosition = document.querySelector("#ragPromptPosition");
  let activeRagPrompt = 0;

  function showRagPrompt(index) {
    if (!ragPromptTabs.length || !ragPromptPanels.length) return;
    activeRagPrompt = Math.max(0, Math.min(index, ragPromptPanels.length - 1));
    ragPromptTabs.forEach((tab, tabIndex) => {
      const isActive = tabIndex === activeRagPrompt;
      tab.classList.toggle("is-active", isActive);
      tab.setAttribute("aria-selected", String(isActive));
      tab.setAttribute("tabindex", isActive ? "0" : "-1");
    });
    ragPromptPanels.forEach((panel, panelIndex) => {
      panel.hidden = panelIndex !== activeRagPrompt;
    });
    ragPromptPrevious.disabled = activeRagPrompt === 0;
    ragPromptNext.disabled = activeRagPrompt === ragPromptPanels.length - 1;
    ragPromptPosition.textContent = `Prompt ${activeRagPrompt + 1} of ${ragPromptPanels.length}`;
  }

  ragPromptTabs.forEach((tab, index) => {
    tab.addEventListener("click", () => showRagPrompt(index));
  });
  ragPromptPrevious?.addEventListener("click", () => showRagPrompt(activeRagPrompt - 1));
  ragPromptNext?.addEventListener("click", () => showRagPrompt(activeRagPrompt + 1));
  ragPromptCopy?.addEventListener("click", async () => {
    const prompt = ragPromptPanels[activeRagPrompt]?.textContent.trim();
    if (!prompt) return;
    try {
      await navigator.clipboard.writeText(prompt);
    } catch {
      const textarea = document.createElement("textarea");
      textarea.value = prompt;
      textarea.setAttribute("readonly", "");
      textarea.style.position = "fixed";
      textarea.style.opacity = "0";
      document.body.append(textarea);
      textarea.select();
      document.execCommand("copy");
      textarea.remove();
    }
    ragPromptCopy.textContent = "Copied";
    announce(`Prompt ${activeRagPrompt + 1} copied`);
    window.setTimeout(() => {
      ragPromptCopy.textContent = "Copy prompt";
    }, 1600);
  });

  showRagPrompt(0);
})();
