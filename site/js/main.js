/* ==========================================================================
   ESR Manager Self Service Hub — progressive enhancement only.
   Every page works without this file; JS just adds convenience.
   ========================================================================== */
(function () {
  "use strict";

  document.documentElement.classList.remove("no-js");
  document.documentElement.classList.add("js");

  /* ---------- Mobile navigation ---------- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* ---------- Back to top ---------- */
  var backTop = document.querySelector(".back-top");
  if (backTop) {
    window.addEventListener("scroll", function () {
      backTop.classList.toggle("is-visible", window.scrollY > 600);
    }, { passive: true });
  }

  /* ---------- Guide: highlight current section in table of contents ---------- */
  var tocLinks = document.querySelectorAll(".toc a[href^='#']");
  if (tocLinks.length && "IntersectionObserver" in window) {
    var byId = {};
    tocLinks.forEach(function (a) { byId[a.getAttribute("href").slice(1)] = a; });
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          tocLinks.forEach(function (a) { a.classList.remove("is-active"); a.removeAttribute("aria-current"); });
          var link = byId[entry.target.id];
          if (link) { link.classList.add("is-active"); link.setAttribute("aria-current", "true"); }
        }
      });
    }, { rootMargin: "-40% 0px -55% 0px" });
    Object.keys(byId).forEach(function (id) {
      var el = document.getElementById(id);
      if (el) observer.observe(el);
    });
  }

  /* ---------- Screenshot lightbox ---------- */
  var lightbox = document.getElementById("lightbox");
  if (lightbox && typeof lightbox.showModal === "function") {
    var lbImg = lightbox.querySelector("img");
    var lbCaption = lightbox.querySelector(".lightbox-caption");
    document.querySelectorAll("[data-zoom]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var img = btn.querySelector("img");
        lbImg.src = img.src;
        lbImg.alt = img.alt;
        lbCaption.textContent = img.alt;
        lightbox.showModal();
      });
    });
    lightbox.addEventListener("click", function (e) {
      if (e.target === lightbox || e.target.closest("[data-close]")) lightbox.close();
    });
  }

  /* ---------- Learning library: search & filter ---------- */
  var library = document.getElementById("library");
  if (!library) return;

  var modules = Array.prototype.slice.call(library.querySelectorAll(".module"));
  var categories = Array.prototype.slice.call(library.querySelectorAll(".category"));
  var search = document.getElementById("module-search");
  var filterButtons = document.querySelectorAll(".filter-chips button");
  var resultsCount = document.getElementById("results-count");
  var resultsStatus = document.getElementById("results-status");
  var empty = document.querySelector(".empty-state");
  var activeFilter = "all";

  function applyFilters() {
    var q = (search && search.value || "").trim().toLowerCase();
    var visible = 0;
    modules.forEach(function (m) {
      var text = m.dataset.search;
      var matchQuery = !q || text.indexOf(q) !== -1;
      var matchFilter =
        activeFilter === "all" ||
        (activeFilter === "essential" && m.dataset.essential === "true");
      var show = matchQuery && matchFilter;
      m.hidden = !show;
      if (show) visible++;
    });
    categories.forEach(function (c) {
      var any = c.querySelector(".module:not([hidden])");
      c.hidden = !any;
    });
    if (empty) empty.classList.toggle("is-visible", visible === 0);
    var msg = visible + " of " + modules.length + " guide" + (modules.length === 1 ? "" : "s") + " shown";
    if (resultsCount) resultsCount.textContent = msg;
    if (resultsStatus) resultsStatus.textContent = msg;
  }

  if (search) search.addEventListener("input", applyFilters);
  filterButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      activeFilter = btn.dataset.filter;
      filterButtons.forEach(function (b) { b.setAttribute("aria-pressed", b === btn ? "true" : "false"); });
      applyFilters();
    });
  });

  // Support deep links such as learning.html?q=sickness
  var params = new URLSearchParams(window.location.search);
  if (search && params.get("q")) search.value = params.get("q");

  applyFilters();
})();
