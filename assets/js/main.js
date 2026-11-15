// Small progressive enhancements; the page is complete without JavaScript.
(function () {
  "use strict";

  // Hairline under the header once the page is scrolled.
  var header = document.querySelector(".site-header");
  function onScroll() {
    if (header) header.classList.toggle("scrolled", window.scrollY > 8);
  }
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  // Highlight the navigation link of the section in view.
  var links = Array.prototype.slice.call(document.querySelectorAll('.nav-links a[href^="#"]'));
  var sections = links
    .map(function (link) { return document.getElementById(link.getAttribute("href").slice(1)); })
    .filter(Boolean);
  if ("IntersectionObserver" in window && sections.length) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        links.forEach(function (link) {
          link.classList.toggle("active", link.getAttribute("href") === "#" + entry.target.id);
        });
      });
    }, { rootMargin: "-30% 0px -60% 0px" });
    sections.forEach(function (section) { observer.observe(section); });
  }

  // A click on a card image shows the whole figure at full size. Without this script the link
  // opens the image file itself.
  var thumbs = Array.prototype.slice.call(document.querySelectorAll("a.pub-thumb[data-zoom]"));
  if (thumbs.length && typeof HTMLDialogElement === "function") {
    var dialog = document.createElement("dialog");
    dialog.className = "lightbox";
    dialog.setAttribute("aria-label", "Figure");
    dialog.innerHTML =
      '<div class="lightbox-stage"><img class="lightbox-img" alt=""></div>' +
      '<p class="lightbox-caption"></p>' +
      '<button class="lightbox-close" type="button" aria-label="Close">&times;</button>';
    document.body.appendChild(dialog);
    var stage = dialog.querySelector(".lightbox-stage");
    var figure = dialog.querySelector(".lightbox-img");
    var caption = dialog.querySelector(".lightbox-caption");
    var opener = null;

    // On a narrow screen the fitted figure is small: a click on it switches to a larger,
    // scrollable view and back.
    var updateZoom = function () {
      var zoomed = dialog.classList.contains("zoomed");
      var small = figure.clientWidth > 0 && figure.clientWidth < 1000 &&
        figure.naturalWidth > figure.clientWidth * 1.3;
      dialog.classList.toggle("can-zoom", zoomed || small);
      var hint = caption.querySelector("span");
      var verb = window.matchMedia && window.matchMedia("(hover: none)").matches ? "Tap" : "Click";
      if (hint) hint.textContent = zoomed ? verb + " the figure to fit it to the screen"
        : (small ? verb + " the figure to enlarge it" : "");
    };

    thumbs.forEach(function (thumb) {
      thumb.addEventListener("click", function (event) {
        if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        var image = thumb.querySelector("img");
        var title = thumb.parentNode.querySelector(".pub-title");
        opener = thumb;
        dialog.classList.remove("zoomed", "can-zoom");
        figure.alt = image ? image.alt : "";
        figure.src = thumb.href;
        caption.textContent = title ? title.textContent : "";
        caption.appendChild(document.createElement("span"));
        dialog.showModal();
        updateZoom();
      });
    });
    figure.addEventListener("load", updateZoom);
    window.addEventListener("resize", function () { if (dialog.open) updateZoom(); });
    figure.addEventListener("click", function () {
      if (!dialog.classList.contains("can-zoom")) { dialog.close(); return; }
      dialog.classList.toggle("zoomed");
      stage.scrollTop = 0;
      stage.scrollLeft = 0;
      updateZoom();
    });
    dialog.querySelector(".lightbox-close").addEventListener("click", function () { dialog.close(); });
    dialog.addEventListener("click", function (event) {
      if (event.target === dialog || event.target === stage || event.target === caption) dialog.close();
    });
    dialog.addEventListener("close", function () {
      figure.removeAttribute("src");
      if (opener) opener.focus({ preventScroll: true });
      opener = null;
    });
  }

  var year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());
})();
