(function () {
  var root = document.documentElement;
  var stored = null;
  try { stored = localStorage.getItem("theme"); } catch (e) {}
  if (stored === "dark") root.setAttribute("data-theme", "dark");
  function paintButtons() {
    var dark = root.getAttribute("data-theme") === "dark";
    document.querySelectorAll(".theme-toggle").forEach(function (b) {
      b.textContent = dark ? "Light" : "Dark";
      b.setAttribute("aria-pressed", dark ? "true" : "false");
    });
  }
  document.querySelectorAll(".theme-toggle").forEach(function (b) {
    b.addEventListener("click", function () {
      var dark = root.getAttribute("data-theme") === "dark";
      if (dark) root.removeAttribute("data-theme");
      else root.setAttribute("data-theme", "dark");
      try { localStorage.setItem("theme", dark ? "light" : "dark"); } catch (e) {}
      paintButtons();
    });
  });
  paintButtons();

  // page-load reveal
  function pageIn() { document.body.classList.add("is-in"); }
  if (document.readyState === "complete") requestAnimationFrame(pageIn);
  else window.addEventListener("load", function () { requestAnimationFrame(pageIn); });
  setTimeout(pageIn, 1200);

  // reading progress
  var bar = document.getElementById("progress");
  var article = document.querySelector(".cs-article");
  if (bar && article) {
    var ticking = false;
    function update() {
      ticking = false;
      var rect = article.getBoundingClientRect();
      var total = rect.height - window.innerHeight;
      var p = total > 0 ? Math.min(1, Math.max(0, -rect.top / total)) : 1;
      bar.style.transform = "scaleX(" + p.toFixed(4) + ")";
    }
    window.addEventListener("scroll", function () {
      if (!ticking) { requestAnimationFrame(update); ticking = true; }
    }, { passive: true });
    window.addEventListener("resize", update, { passive: true });
    update();
  }
})();
