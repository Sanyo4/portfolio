// sanay.space/flights: the reel of stubs drives the in-flight map.
// The reel is the only control. Scroll, drag, click or arrow keys pick a
// flight; the camera eases to frame it, the route draws and the paper plane
// flies it. Without JS the reel is a plain list by trip.
(function () {
  var dataEl = document.getElementById("flights");
  var reel = document.getElementById("reel");
  var svg = document.getElementById("map");
  if (!dataEl || !reel || !svg) return;

  var D = JSON.parse(dataEl.textContent);
  var F = D.flights, N = F.length;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var glass = svg.parentNode;
  var readout = document.getElementById("readout");
  var legs = Array.prototype.slice.call(reel.querySelectorAll(".leg"));
  var routes = F.map(function (f, i) { return document.getElementById("r" + i); });
  var $ = function (id) { return document.getElementById(id); };
  var glow = $("glow"), endA = $("endA"), endB = $("endB"), codeA = $("codeA"), codeB = $("codeB"), plane = $("jet");
  var ro = { count: $("roCount"), season: $("roSeason"), codes: $("roCodes"), meta: $("roMeta"), date: $("roDate") };
  var caption = $("caption");
  var MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];

  // ---------- reel semantics: a listbox of flights, grouped by trip ----------
  reel.setAttribute("role", "listbox");
  Array.prototype.forEach.call(reel.querySelectorAll(".trip"), function (t) {
    t.setAttribute("role", "group");
    t.setAttribute("aria-label", t.getAttribute("data-trip") + ", " + t.getAttribute("data-when"));
    t.querySelector(".trip__name").setAttribute("aria-hidden", "true");
    t.querySelector(".trip__legs").setAttribute("role", "none");
  });
  legs.forEach(function (l, i) {
    l.setAttribute("role", "option");
    l.setAttribute("aria-selected", "false");
    l.tabIndex = i === 0 ? 0 : -1;
    l.trip = l.closest(".trip");
  });

  // ---------- camera ----------
  var world = D.world;
  var vb = world.slice(), camFrom = null, camTo = null, camT0 = 0, camRaf = 0;

  function ease(t) { return 1 - Math.pow(1 - t, 3); }

  function view() {
    var w = glass.clientWidth, h = glass.clientHeight, r = readout.offsetHeight;
    return { w: w, h: h, open: Math.max(40, h - r) };
  }

  // Frame a box in the open part of the screen above the readout.
  function frameBox(b, minW) {
    var v = view();
    if (!v.w || !v.h) return vb.slice(); // hidden or not laid out yet: keep the current view
    var aspect = v.w / v.open;
    var cx = (b[0] + b[2]) / 2, cy = (b[1] + b[3]) / 2;
    var w = (b[2] - b[0]) * 1.48, h = (b[3] - b[1]) * 1.48;
    w = Math.max(w, h * aspect, minW);
    var maxW = Math.max(world[2] - world[0], (world[3] - world[1]) * aspect) * 1.1;
    if (w > maxW) w = maxW;
    h = w / aspect;
    var full = h * v.h / v.open;
    return [cx - w / 2, cy - h / 2, w, full];
  }

  function worldFrame() {
    return frameBox(world, 0);
  }

  function setView(v) {
    if (!v.every(isFinite)) return;
    vb = v;
    svg.setAttribute("viewBox", v.map(function (n) { return n.toFixed(1); }).join(" "));
    u = v[2] / (glass.clientWidth || 1);
    svg.style.setProperty("--u", u.toFixed(4));
    placeMarks();
  }

  function camera(target, instant) {
    cancelAnimationFrame(camRaf);
    if (instant || reduce) { setView(target); return; }
    camFrom = vb.slice();
    camTo = target;
    camT0 = performance.now();
    camRaf = requestAnimationFrame(function step(now) {
      var t = Math.min(1, (now - camT0) / 700), k = ease(t);
      setView(camFrom.map(function (a, j) { return a + (camTo[j] - a) * k; }));
      if (t < 1) camRaf = requestAnimationFrame(step);
    });
  }

  // ---------- route, plane, end markers ----------
  var u = 1, idx = -1, shown = -1, drawP = 1, drawRaf = 0, len = 0, intro = true;

  function placeMarks() {
    if (shown < 0) return;
    var f = F[shown], o = 6 * u;
    codeA.setAttribute("x", f.a[0] + o); codeA.setAttribute("y", f.a[1] - o);
    codeB.setAttribute("x", f.b[0] + o); codeB.setAttribute("y", f.b[1] - o);
    placePlane();
  }

  function placePlane() {
    var r = routes[shown];
    if (!r || !len) return;
    var at = Math.max(0.5, len * drawP);
    var p = r.getPointAtLength(at), q = r.getPointAtLength(Math.max(0, at - 1.5));
    var deg = Math.atan2(p.y - q.y, p.x - q.x) * 180 / Math.PI + 43;
    plane.setAttribute("transform", "translate(" + p.x.toFixed(1) + " " + p.y.toFixed(1) + ") rotate(" + deg.toFixed(1) + ") scale(" + (u * 22 / 32).toFixed(4) + ")");
  }

  function setDraw(p) {
    drawP = p;
    var off = (len * (1 - p)).toFixed(1);
    routes[shown].style.strokeDashoffset = off;
    glow.style.strokeDashoffset = off;
    placePlane();
  }

  function draw() {
    cancelAnimationFrame(drawRaf);
    if (reduce) { setDraw(1); return; }
    var t0 = performance.now() + 120;
    drawRaf = requestAnimationFrame(function step(now) {
      var t = Math.max(0, Math.min(1, (now - t0) / 900));
      setDraw(ease(t));
      if (t < 1) drawRaf = requestAnimationFrame(step);
    });
  }

  // ---------- readout ----------
  function hm(m) { return m ? Math.floor(m / 60) + " h " + ("0" + (m % 60)).slice(-2) : ""; }
  function dmy(iso) { return iso.slice(8, 10) + " " + MONTHS[+iso.slice(5, 7) - 1] + " " + iso.slice(0, 4); }

  function fill(f, i) {
    ro.count.textContent = "Flight " + (i + 1) + " / " + N;
    ro.season.textContent = f.season ? D.season + " in 45 · " + f.season : "";
    ro.codes.textContent = f.from + " → " + f.to;
    ro.meta.textContent = [
      f.fromCity + " to " + f.toCity,
      f.km.toLocaleString("en-GB") + " km",
      hm(f.min),
      (f.airline + " " + f.flight).trim(),
      f.cabin === "Economy" ? "" : f.cabin
    ].filter(Boolean).join(" · ");
    ro.date.textContent = dmy(f.date);
    var t = legs[i].trip;
    caption.textContent = t.getAttribute("data-trip") + " · " + t.getAttribute("data-when");
  }

  // ---------- the passport follows the reel ----------
  var visas = Array.prototype.slice.call(document.querySelectorAll(".visa")).map(function (el) {
    el.addEventListener("animationend", function () { el.classList.remove("is-new"); });
    return { el: el, country: el.getAttribute("data-country"), first: +el.getAttribute("data-first"), n: el.querySelector(".visa__n") };
  });

  function stampTo(i, prev) {
    var count = {};
    for (var j = 0; j <= i; j++) count[F[j].country] = (count[F[j].country] || 0) + 1;
    visas.forEach(function (v) {
      var seen = v.first <= i;
      v.el.classList.toggle("is-blank", !seen);
      if (seen) v.el.removeAttribute("aria-hidden");
      else v.el.setAttribute("aria-hidden", "true");
      v.el.classList.toggle("is-here", F[i].country === v.country);
      // stamp only when stepping forward from a flight, not when leaving the full opening view
      if (seen && prev >= 0 && prev < v.first && !reduce) {
        v.el.classList.remove("is-new");
        void v.el.offsetWidth; // restart the stamp animation
        v.el.classList.add("is-new");
      } else if (!seen) {
        v.el.classList.remove("is-new");
      }
      if (seen) v.n.textContent = count[v.country];
      v.el.lastElementChild.lastChild.textContent = count[v.country] === 1 ? " landing" : " landings";
    });
  }

  // ---------- selecting a flight ----------
  // Two speeds. pick() is cheap and runs for every stub that passes the
  // centre: the stub, the readout and a haptic tick. commit() moves the map,
  // draws the route and updates the passport, once the reel rests on a stub.
  var commitTimer = 0, target = -1;

  function pick(i) {
    if (i === idx) return;
    var prev = idx;
    idx = i;
    if (prev < 0) legs[0].tabIndex = -1;
    if (prev >= 0) {
      legs[prev].classList.remove("is-active");
      legs[prev].setAttribute("aria-selected", "false");
      legs[prev].tabIndex = -1;
    }
    legs[i].classList.add("is-active");
    legs[i].setAttribute("aria-selected", "true");
    legs[i].tabIndex = 0;
    if (armed) haptic();
    fill(F[i], i);
    // a slow drag that lingers on a stub shows its map too
    if (target < 0) {
      clearTimeout(commitTimer);
      commitTimer = setTimeout(commit, 160);
    }
  }

  function commit() {
    clearTimeout(commitTimer);
    var i = idx;
    if (i < 0 || i === shown) return;
    var prev = shown;
    shown = i;
    var f = F[i];

    if (intro) { svg.classList.remove("is-intro"); intro = false; }
    for (var j = 0; j < N; j++) {
      routes[j].classList.toggle("is-past", j < i);
      routes[j].classList.toggle("is-cur", j === i);
    }
    if (prev >= 0) {
      routes[prev].style.strokeDasharray = "";
      routes[prev].style.strokeDashoffset = "";
    }
    var r = routes[i];
    len = r.getTotalLength();
    r.style.strokeDasharray = len;
    glow.setAttribute("d", r.getAttribute("d"));
    glow.style.strokeDasharray = len;
    svg.classList.toggle("is-gold", f.gold);
    endA.setAttribute("cx", f.a[0]); endA.setAttribute("cy", f.a[1]);
    endB.setAttribute("cx", f.b[0]); endB.setAttribute("cy", f.b[1]);
    codeA.textContent = f.from;
    codeB.textContent = f.to;
    stampTo(i, prev);

    camera(frameBox(f.box, 180));
    cancelAnimationFrame(drawRaf);
    setDraw(reduce ? 1 : 0);
    draw();
  }

  // ---------- the reel as input: a flywheel ----------
  // Touch and mouse drags move the reel one to one. Letting go keeps it
  // rolling at the speed of the flick, slowing like a free-spinning wheel, and
  // it comes to rest centred on a stub. Vertical page scrolling stays native
  // (touch-action: pan-y), and trackpads and keys still work.
  var centres = [], armed = false, scrollRaf = 0, settleTimer = 0;
  var drag = null, flyRaf = 0, toRaf = 0, dragged = false;
  var FRICTION = 0.955; // speed kept per 60th of a second
  var BOOST = 1.6; // a flick carries further than the finger moved
  var MAXV = 9; // px per ms
  var GLIDE = 16.7 / (1 - FRICTION); // ms of travel per px/ms of launch speed

  // Before any of this, only a person's touch, wheel or key leaves the opening view.
  ["pointerdown", "touchstart", "wheel", "keydown"].forEach(function (t) {
    reel.addEventListener(t, function () { armed = true; reel.classList.remove("is-nudge"); }, { passive: true });
  });

  // A detent under the thumb as each stub passes the centre. Android has the
  // Vibration API. iOS Safari does not, but from iOS 18 toggling a switch
  // checkbox through its label gives a system haptic, so a hidden one stands in.
  var lastTick = 0, switchLabel = null;
  if (!("vibrate" in navigator)) {
    var sw = document.createElement("input");
    sw.type = "checkbox";
    sw.setAttribute("switch", "");
    sw.tabIndex = -1;
    switchLabel = document.createElement("label");
    switchLabel.setAttribute("aria-hidden", "true");
    switchLabel.style.cssText = "position:fixed;left:-200px;top:0;width:1px;height:1px;overflow:hidden;opacity:0;pointer-events:none";
    switchLabel.appendChild(sw);
    document.body.appendChild(switchLabel);
  }
  function haptic() {
    var now = performance.now();
    if (now - lastTick < 45) return;
    lastTick = now;
    if (switchLabel) {
      var had = document.activeElement;
      switchLabel.click();
      if (had && had !== document.activeElement) had.focus({ preventScroll: true }); // keep keyboard focus on the stub
    } else if (!navigator.userActivation || navigator.userActivation.hasBeenActive) {
      navigator.vibrate(8); // Chrome blocks it until the first tap, and would log each try
    }
  }

  // The belt runs with the reel (a transform, so it stays on the compositor),
  // then goes back to bobbing once the reel is still.
  var belt = document.getElementById("belt"), beltTimer = 0;
  function runBelt() {
    if (!belt) return;
    belt.classList.add("is-live");
    belt.style.setProperty("--bx", (-(reel.scrollLeft % 60)).toFixed(1) + "px");
    clearTimeout(beltTimer);
    beltTimer = setTimeout(function () { belt.classList.remove("is-live"); }, 1600);
  }

  // One shove the first time the reel comes into view, so it reads as something that moves.
  if (!reduce && "IntersectionObserver" in window) {
    var nudger = new IntersectionObserver(function (es) {
      if (!es[0].isIntersecting) return;
      nudger.disconnect();
      if (armed) return;
      reel.classList.add("is-nudge");
      reel.addEventListener("animationend", function () { reel.classList.remove("is-nudge"); }, { once: true });
    }, { threshold: 0.6 });
    nudger.observe(reel);
  }

  function measure() {
    centres = legs.map(function (l) { return l.offsetLeft + l.offsetWidth / 2; });
  }

  function nearestTo(left) {
    var c = left + reel.clientWidth / 2, best = 0, bd = Infinity;
    for (var i = 0; i < centres.length; i++) {
      var d = Math.abs(centres[i] - c);
      if (d < bd) { bd = d; best = i; }
    }
    return best;
  }
  function nearest() { return nearestTo(reel.scrollLeft); }
  function maxLeft() { return reel.scrollWidth - reel.clientWidth; }
  function leftFor(i) { return Math.max(0, Math.min(maxLeft(), centres[i] - reel.clientWidth / 2)); }

  function stop() {
    cancelAnimationFrame(flyRaf);
    cancelAnimationFrame(toRaf);
    flyRaf = toRaf = 0;
    clearTimeout(settleTimer);
  }

  // Ease the reel to a scroll position; the stubs it passes still tick.
  function slideTo(left, ms, done) {
    stop();
    var from = reel.scrollLeft, t0 = performance.now();
    if (reduce || Math.abs(left - from) < 1) {
      reel.scrollLeft = left;
      if (done) done();
      return;
    }
    toRaf = requestAnimationFrame(function step(now) {
      var t = Math.min(1, (now - t0) / ms);
      reel.scrollLeft = from + (left - from) * ease(t);
      if (t < 1) toRaf = requestAnimationFrame(step);
      else { toRaf = 0; if (done) done(); }
    });
  }

  function rest(i) {
    target = -1;
    pick(i);
    commit();
  }

  function settle() {
    var i = nearest();
    target = i;
    slideTo(leftFor(i), 240, function () { rest(i); });
  }

  function onStub() { return Math.abs(reel.scrollLeft - leftFor(nearest())) < 1; }

  // Roll on from a flick, aimed so the wheel coasts to a stop on a stub.
  function fling(v) {
    stop();
    if (reduce || Math.abs(v) < 0.1) { settle(); return; }
    var from = reel.scrollLeft;
    target = nearestTo(Math.max(0, Math.min(maxLeft(), from + v * GLIDE)));
    var land = leftFor(target);
    v = (land - from) / GLIDE;
    var last = performance.now();
    flyRaf = requestAnimationFrame(function step(now) {
      var dt = Math.min(34, now - last);
      last = now;
      var before = reel.scrollLeft;
      reel.scrollLeft = before + v * dt;
      v *= Math.pow(FRICTION, dt / 16.7);
      var stuck = Math.abs(reel.scrollLeft - before) < 0.3 && Math.abs(v * dt) > 0.5;
      if (Math.abs(v) > 0.05 && !stuck) flyRaf = requestAnimationFrame(step);
      else { flyRaf = 0; settle(); }
    });
  }

  reel.addEventListener("pointerdown", function (e) {
    if (drag || (e.pointerType === "mouse" && e.button !== 0)) return;
    stop();
    target = -1;
    drag = { id: e.pointerId, x: e.clientX, y: e.clientY, left: reel.scrollLeft, moved: false, pts: [[e.timeStamp, e.clientX]] };
  });

  reel.addEventListener("pointermove", function (e) {
    if (!drag || e.pointerId !== drag.id) return;
    var dx = e.clientX - drag.x;
    if (!drag.moved) {
      if (Math.abs(dx) < 6) return;
      if (Math.abs(e.clientY - drag.y) > Math.abs(dx)) { drag = null; return; } // the page is scrolling
      drag.moved = true;
      try { reel.setPointerCapture(drag.id); } catch (err) { /* pointer already gone */ }
      reel.classList.add("is-dragging");
    }
    reel.scrollLeft = drag.left - dx;
    drag.pts.push([e.timeStamp, e.clientX]);
    if (drag.pts.length > 8) drag.pts.shift();
  });

  function release(e) {
    if (!drag || e.pointerId !== drag.id) return;
    var d = drag;
    drag = null;
    reel.classList.remove("is-dragging");
    if (!d.moved) { // a tap: a stub's own click selects it, anywhere else re-centres
      if (!onStub()) settle();
      return;
    }
    dragged = true;
    setTimeout(function () { dragged = false; }, 0);
    // speed over the last 100ms of the drag; none if the finger stopped first
    var pts = d.pts, last = pts[pts.length - 1], first = last;
    for (var k = pts.length - 1; k >= 0 && last[0] - pts[k][0] <= 100; k--) first = pts[k];
    var dt = Math.max(16, last[0] - first[0]); // two events a hair apart must not read as a huge flick
    var v = dt > 0 && e.timeStamp - last[0] < 80 ? -(last[1] - first[1]) / dt : 0;
    fling(Math.max(-MAXV, Math.min(MAXV, v * BOOST)));
  }
  reel.addEventListener("pointerup", release);
  reel.addEventListener("pointercancel", function (e) {
    if (!drag || e.pointerId !== drag.id) return;
    drag = null;
    reel.classList.remove("is-dragging");
    settle();
  });

  reel.addEventListener("scroll", function () {
    if (scrollRaf) return;
    scrollRaf = requestAnimationFrame(function () {
      scrollRaf = 0;
      runBelt();
      if (!armed) return;
      pick(nearest());
      // native scrolling (a trackpad, say) comes to rest on a stub as well
      clearTimeout(settleTimer);
      if (!drag && !flyRaf && !toRaf) settleTimer = setTimeout(settle, 140);
    });
  }, { passive: true });

  function go(i, focus) {
    i = Math.max(0, Math.min(N - 1, i));
    var from = idx < 0 ? 0 : idx;
    target = i;
    pick(i);
    commit();
    slideTo(leftFor(i), Math.min(700, 260 + 18 * Math.abs(i - from)), function () { rest(i); });
    if (focus) legs[i].focus({ preventScroll: true });
  }

  legs.forEach(function (l, i) {
    l.addEventListener("click", function () { if (!dragged) go(i, true); });
  });

  function tripStart(from, dir) {
    var t = legs[from].trip, i = from;
    if (dir > 0) {
      while (i < N - 1 && legs[i].trip === t) i++;
      return i;
    }
    if (i > 0 && legs[i - 1].trip !== t) t = legs[--i].trip;
    while (i > 0 && legs[i - 1].trip === t) i--;
    return i;
  }

  reel.addEventListener("keydown", function (e) {
    var i = idx < 0 ? 0 : idx, to = null;
    if (e.key === "ArrowRight" || e.key === "ArrowDown") to = i + 1;
    else if (e.key === "ArrowLeft" || e.key === "ArrowUp") to = i - 1;
    else if (e.key === "Home") to = 0;
    else if (e.key === "End") to = N - 1;
    else if (e.key === "PageDown") to = tripStart(i, 1);
    else if (e.key === "PageUp") to = tripStart(i, -1);
    if (to === null) return;
    e.preventDefault();
    go(idx < 0 && e.key !== "End" ? 0 : to, true);
  });

  // A sideways trackpad swipe moves the reel directly and settles when it stops.
  // A vertical mouse wheel steps through the stubs, one per 60px of wheel,
  // and hands the page back its scroll at either end.
  var wheel = 0;
  reel.addEventListener("wheel", function (e) {
    if (Math.abs(e.deltaX) > Math.abs(e.deltaY)) {
      e.preventDefault();
      stop();
      target = -1;
      reel.scrollLeft += e.deltaX;
      return;
    }
    if (window.matchMedia("(pointer: fine)").matches) {
      var at = idx < 0 ? -1 : idx;
      if ((e.deltaY < 0 && at <= 0) || (e.deltaY > 0 && at >= N - 1)) return;
      e.preventDefault();
      wheel += e.deltaY;
      if (Math.abs(wheel) < 60) return;
      go(at < 0 ? 0 : at + (wheel > 0 ? 1 : -1), false);
      wheel = 0;
    }
  }, { passive: false });

  var resizeTimer = 0;
  window.addEventListener("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      measure();
      if (intro) setView(worldFrame());
      else if (shown >= 0) camera(frameBox(F[shown].box, 180), true);
      if (toRaf) settle();
      else if (idx >= 0 && !drag && !flyRaf) reel.scrollLeft = leftFor(idx);
    }, 120);
  });

  // ---------- start: the whole map, every route faint, flight 1 on the reel ----------
  measure();
  svg.classList.add("is-intro");
  setView(worldFrame());
  idx = 0;
  var f0 = F[0];
  legs[0].classList.add("is-active");
  legs[0].setAttribute("aria-selected", "true");
  fill(f0, 0);
  ro.count.textContent = N + " flights";
  ro.codes.textContent = "Every route since " + f0.date.slice(0, 4);
  ro.meta.textContent = D.totals.km.toLocaleString("en-GB") + " km · " + D.totals.airports + " airports · " + D.totals.countries.length + " countries";
  ro.date.textContent = "";
  ro.season.textContent = "";
  var LONG = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  var my = function (iso) { return LONG[+iso.slice(5, 7) - 1] + " " + iso.slice(0, 4); };
  caption.textContent = my(f0.date) + " to " + my(F[N - 1].date);
  idx = -1;
  legs[0].classList.remove("is-active");
  legs[0].setAttribute("aria-selected", "false");
  reel.scrollLeft = 0;
})();
