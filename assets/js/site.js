// sanay.space: parallax on the hero paper layers, the route line that
// fills as you read, and prints that settle in as they scroll into view.
// Everything here is optional. The page reads the same without it.
(function () {
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var wide = window.matchMedia("(min-width: 768px)");
  var finePointer = window.matchMedia("(pointer: fine)").matches;

  // Scroll-in
  var risers = document.querySelectorAll(".rise");
  if (!reduce && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add("is-in");
          io.unobserve(e.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    risers.forEach(function (el) { io.observe(el); });
  } else {
    risers.forEach(function (el) { el.classList.add("is-in"); });
  }

  if (reduce) return;

  var layers = Array.prototype.slice.call(document.querySelectorAll("[data-depth]"));
  var hero = document.querySelector(".hero");
  var route = document.querySelector(".route");
  var progress = document.querySelector(".cs-progress");
  var px = 0, py = 0, tx = 0, ty = 0, sy = 0, ticking = false, heroVisible = true;

  if (hero && "IntersectionObserver" in window) {
    new IntersectionObserver(function (e) { heroVisible = e[0].isIntersecting; }).observe(hero);
  }

  function frame() {
    ticking = false;
    sy = window.scrollY;

    if (heroVisible && layers.length && wide.matches) {
      tx += (px - tx) * 0.12;
      ty += (py - ty) * 0.12;
      for (var i = 0; i < layers.length; i++) {
        var d = parseFloat(layers[i].getAttribute("data-depth")) || 0;
        var x = tx * d * 28;
        var y = ty * d * 18 + sy * d * 0.35;
        layers[i].style.transform = "translate3d(" + x.toFixed(2) + "px," + y.toFixed(2) + "px,0)";
      }
      if (Math.abs(px - tx) > 0.002 || Math.abs(py - ty) > 0.002) request();
    }

    if (route) {
      var r = route.getBoundingClientRect();
      var mid = window.innerHeight * 0.55;
      var p = (mid - r.top) / r.height;
      p = p < 0 ? 0 : p > 1 ? 1 : p;
      route.style.setProperty("--p", p.toFixed(4));
    }

    if (progress) {
      var max = document.documentElement.scrollHeight - window.innerHeight;
      progress.style.setProperty("--p", max > 0 ? Math.min(1, sy / max).toFixed(4) : 0);
    }
  }

  function request() {
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(frame);
    }
  }

  window.addEventListener("scroll", request, { passive: true });
  window.addEventListener("resize", function () {
    if (!wide.matches) layers.forEach(function (l) { l.style.transform = ""; });
    request();
  });

  if (finePointer && hero) {
    hero.addEventListener("pointermove", function (e) {
      px = e.clientX / window.innerWidth - 0.5;
      py = e.clientY / window.innerHeight - 0.5;
      request();
    });
    hero.addEventListener("pointerleave", function () { px = 0; py = 0; request(); });
  }

  request();
})();
