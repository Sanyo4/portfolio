/* sanay.space, night edition: interaction layer */
(() => {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  const desktop = () => window.matchMedia('(min-width: 1000px)').matches;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));

  /* ---------- split words ---------- */
  $$('[data-split]').forEach((el) => {
    const walk = (node) => {
      Array.from(node.childNodes).forEach((n) => {
        if (n.nodeType === 3) {
          const frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach((piece) => {
            if (!piece) return;
            if (/^\s+$/.test(piece)) { frag.appendChild(document.createTextNode(' ')); return; }
            const w = document.createElement('span'); w.className = 'w';
            const inner = document.createElement('span'); inner.textContent = piece;
            w.appendChild(inner); frag.appendChild(w);
          });
          node.replaceChild(frag, n);
        } else if (n.nodeType === 1) walk(n);
      });
    };
    walk(el);
    $$('.w', el).forEach((w, i) => { w.style.setProperty('--wd', `${Math.min(i * 0.035, 1.2)}s`); });
  });

  /* ---------- smooth scroll ---------- */
  let lenis = null;
  if (!reduced && window.Lenis) {
    lenis = new Lenis({ lerp: 0.09, wheelMultiplier: 0.95, smoothWheel: true, syncTouch: false });
    const raf = (t) => { lenis.raf(t); requestAnimationFrame(raf); };
    requestAnimationFrame(raf);
  }
  const scrollTo = (target) => {
    const el = typeof target === 'string' ? $(target) : target;
    if (!el) return;
    if (lenis) lenis.scrollTo(el, { offset: -20, duration: 1.4 });
    else el.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth' });
  };

  /* ---------- gsap ---------- */
  const hasGsap = !!(window.gsap && window.ScrollTrigger);
  if (hasGsap) {
    gsap.registerPlugin(ScrollTrigger);
    if (lenis) { lenis.on('scroll', ScrollTrigger.update); }
  }

  /* ---------- loader ---------- */
  const loader = $('#loader');
  const count = $('#loader-count');
  const nav = $('#nav');
  const hero = $('#hero');
  const startedAt = performance.now();
  let done = false;

  const finishLoader = () => {
    if (done) return; done = true;
    loader.classList.add('is-done');
    document.body.classList.add('is-loaded');
    setTimeout(() => {
      nav.classList.add('is-in');
      hero.querySelectorAll('.reveal-up').forEach((el) => el.classList.add('is-in'));
      const title = $('.hero__title');
      if (title) title.classList.add('is-in');
    }, 200);
    setTimeout(() => { loader.remove(); }, 1500);
  };

  if (reduced) { finishLoader(); }
  else {
    let n = 0;
    const tick = () => {
      const elapsed = performance.now() - startedAt;
      const goal = Math.min(100, Math.floor(elapsed / 11));
      n = Math.max(n, goal);
      count.textContent = String(n).padStart(2, '0');
      if (n >= 100) { setTimeout(finishLoader, 140); return; }
      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
    // whatever happens, never hold the page hostage
    setTimeout(finishLoader, 2600);
  }

  /* ---------- reveals ---------- */
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
  $$('.reveal-up, [data-split]').forEach((el) => { if (!hero.contains(el)) io.observe(el); });

  /* ---------- manifesto word lighting ---------- */
  const man = $('.manifesto__text');
  if (man) {
    const words = $$('.w', man);
    const light = () => {
      const r = man.getBoundingClientRect();
      const vh = window.innerHeight;
      const p = Math.min(1, Math.max(0, (vh * 0.82 - r.top) / (r.height + vh * 0.25)));
      const lit = Math.floor(p * words.length);
      words.forEach((w, i) => w.classList.toggle('is-lit', i < lit));
    };
    window.addEventListener('scroll', light, { passive: true });
    if (lenis) lenis.on('scroll', light);
    light();
  }

  /* ---------- clock ---------- */
  const clockEls = [$('#clock'), $('#clock-foot')].filter(Boolean);
  const fmt = new Intl.DateTimeFormat('en-GB', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/London' });
  const tickClock = () => {
    const t = fmt.format(new Date());
    clockEls.forEach((el, i) => { el.textContent = i === 0 ? `London ${t}` : t; });
  };
  tickClock(); setInterval(tickClock, 15000);

  /* ---------- theme ---------- */
  const root = document.documentElement;
  const themeMeta = document.querySelector('meta[name="theme-color"]');
  const setTheme = (light, persist = true) => {
    if (light) root.setAttribute('data-theme', 'light'); else root.removeAttribute('data-theme');
    if (themeMeta) themeMeta.setAttribute('content', light ? '#e9ebe6' : '#0d1110');
    $$('#theme-btn').forEach((b) => b.setAttribute('aria-pressed', String(light)));
    if (window.__terrainTheme) window.__terrainTheme();
    if (persist) { try { localStorage.setItem('theme', light ? 'light' : 'dark'); } catch (e) {} }
  };
  setTheme(root.getAttribute('data-theme') === 'light', false);
  $$('#theme-btn, [data-theme-toggle]').forEach((b) => b.addEventListener('click', () => setTheme(root.getAttribute('data-theme') !== 'light')));

  /* ---------- menu ---------- */
  const menu = $('#menu');
  const menuBtn = $('#menu-btn');
  const setMenu = (open) => {
    menu.classList.toggle('is-open', open);
    menu.setAttribute('aria-hidden', String(!open));
    menuBtn.setAttribute('aria-expanded', String(open));
    if (lenis) { open ? lenis.stop() : lenis.start(); }
    document.documentElement.style.overflow = open ? 'hidden' : '';
  };
  menuBtn.addEventListener('click', () => setMenu(!menu.classList.contains('is-open')));
  $$('a[href^="#"]', menu).forEach((a) => a.addEventListener('click', (e) => {
    e.preventDefault(); setMenu(false); setTimeout(() => scrollTo(a.getAttribute('href')), 250);
  }));
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') setMenu(false); });
  $$('a[href^="#"]:not(.menu a)').forEach((a) => a.addEventListener('click', (e) => {
    const id = a.getAttribute('href'); if (id.length < 2) return;
    e.preventDefault(); scrollTo(id);
  }));

  /* ---------- typewriter ---------- */
  const tw = $('#typewriter');
  if (tw && !reduced) {
    const phrases = [
      'building an AI agent team for accountants',
      'just wrapped an AI discovery for a national pharmacy group',
      'writing case studies instead of a CV',
    ];
    let pi = 0, ci = phrases[0].length, deleting = true;
    const step = () => {
      const p = phrases[pi];
      if (deleting) { ci--; tw.textContent = p.slice(0, ci); if (ci === 0) { deleting = false; pi = (pi + 1) % phrases.length; setTimeout(step, 300); return; } setTimeout(step, 22); }
      else { ci++; tw.textContent = phrases[pi].slice(0, ci); if (ci === phrases[pi].length) { deleting = true; setTimeout(step, 3600); return; } setTimeout(step, 46 + Math.random() * 40); }
    };
    setTimeout(step, 5200);
  }

  /* ---------- ticker ---------- */
  const ticker = $('#ticker');
  if (ticker) {
    const clone = ticker.cloneNode(true); clone.id = ''; clone.setAttribute('aria-hidden', 'true');
    ticker.parentNode.appendChild(clone);
    const track = ticker.parentNode;
    track.style.display = 'flex';
    let x = 0, last = performance.now();
    const speed = reduced ? 0 : 38;
    const loop = (now) => {
      const dt = (now - last) / 1000; last = now;
      x -= speed * dt;
      const w = ticker.getBoundingClientRect().width + 38;
      if (-x >= w) x += w;
      ticker.style.transform = `translate3d(${x}px,0,0)`;
      clone.style.transform = `translate3d(${x}px,0,0)`;
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  }

  /* ---------- horizontal rail (desktop pin) ---------- */
  const rail = $('#rail');
  const track = $('#rail-track');
  let railST = null;
  const buildRail = () => {
    if (railST) { railST.kill(); railST = null; gsap.set(track, { clearProps: 'all' }); }
    if (!hasGsap || reduced || !desktop()) return;
    const dist = () => track.scrollWidth - window.innerWidth;
    railST = gsap.to(track, {
      x: () => -dist(),
      ease: 'none',
      scrollTrigger: {
        trigger: rail, start: 'top top', end: () => `+=${dist()}`,
        pin: true, scrub: 0.6, invalidateOnRefresh: true, anticipatePin: 1,
      },
    }).scrollTrigger;
  };
  const dragRail = () => {
    let down = false, startX = 0, startLeft = 0, moved = false, pid = null;
    track.addEventListener('pointerdown', (e) => {
      if (railST || e.pointerType !== 'mouse' || e.button !== 0) return;
      down = true; moved = false; startX = e.clientX; startLeft = track.scrollLeft; pid = e.pointerId;
      track.setPointerCapture(pid);
    });
    track.addEventListener('pointermove', (e) => {
      if (!down) return;
      const dx = e.clientX - startX;
      if (Math.abs(dx) > 4 && !moved) { moved = true; track.classList.add('is-dragging'); }
      if (moved) track.scrollLeft = startLeft - dx;
    });
    const end = () => {
      if (!down) return; down = false;
      if (pid != null) { try { track.releasePointerCapture(pid); } catch (e) {} }
      setTimeout(() => track.classList.remove('is-dragging'), 60);
    };
    track.addEventListener('pointerup', end);
    track.addEventListener('pointercancel', end);
    track.addEventListener('click', (e) => { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
    // a vertical wheel over the rail pushes it sideways when it is not pinned
    track.addEventListener('wheel', (e) => {
      if (railST || Math.abs(e.deltaY) < Math.abs(e.deltaX)) return;
      const max = track.scrollWidth - track.clientWidth;
      const atEdge = (e.deltaY > 0 && track.scrollLeft >= max - 1) || (e.deltaY < 0 && track.scrollLeft <= 0);
      if (atEdge) return;
      e.preventDefault(); track.scrollLeft += e.deltaY;
    }, { passive: false });
  };
  if (rail && track) {
    buildRail();
    dragRail();
    let rw;
    window.addEventListener('resize', () => { clearTimeout(rw); rw = setTimeout(() => { buildRail(); ScrollTrigger.refresh(); }, 200); });
  }

  /* ---------- parallax images ---------- */
  if (hasGsap && !reduced) {
    $$('.parallax').forEach((el) => {
      const speed = parseFloat(el.dataset.speed || '0.1');
      const holder = el.closest('figure') || el.parentElement;
      gsap.fromTo(el, { yPercent: -speed * 100 * 0.6 }, {
        yPercent: speed * 100 * 0.6, ease: 'none',
        scrollTrigger: { trigger: holder, start: 'top bottom', end: 'bottom top', scrub: true },
      });
      if (el.tagName === 'IMG') el.style.transform = 'scale(1.16)';
    });
  }

  /* ---------- lore shuffle ---------- */
  const drops = [
    '43 flights in 45 weeks, mostly on a student budget and a lounge pass.',
    'My favourite way into a city: talk to strangers until one of them shows me around. The Fujifilm starts the conversation.',
    'A detour once ended at a monastery in the Taiwanese highlands, hosted by an eccentric German monk.',
    'Boys\' school did Macbeth. Someone had to be Lady Macbeth, and it was me: dress, full makeup, full house. An acting agency scouted me off the back of it.',
    'Performed in the school\'s first student-led play, Another Country.',
    'Halloween in Hongdae. Ask me about it.',
    'A road trip across the south of Japan in a kei car. Ask me about it.',
    'A private watch event with the Arnault family. Long story.',
    'Coxed a rowing four to winning a national B final.',
    'I built a travel AI on three reference points: Bourdain, The Hangover, An Idiot Abroad. It\'s basically autobiographical.',
  ];
  const drop = $('#lore-drop');
  const dropCount = $('#lore-count');
  const shuffleBtn = $('#lore-shuffle');
  if (drop && shuffleBtn) {
    let deck = []; let idx = 0; let typing = null;
    const reshuffle = () => { deck = drops.map((_, i) => i).sort(() => Math.random() - 0.5); if (deck[0] === 0 && drops.length > 1) deck.push(deck.shift()); };
    reshuffle();
    const show = (i) => {
      const text = drops[i];
      dropCount.textContent = `${String(i + 1).padStart(2, '0')} / ${String(drops.length).padStart(2, '0')}`;
      if (reduced) { drop.textContent = text; return; }
      clearTimeout(typing);
      drop.textContent = '';
      let c = 0;
      const t = () => { c++; drop.textContent = text.slice(0, c); if (c < text.length) typing = setTimeout(t, 14 + Math.random() * 18); };
      t();
    };
    shuffleBtn.addEventListener('click', () => { if (idx >= deck.length) { reshuffle(); idx = 0; } show(deck[idx++]); });
  }

  /* ---------- video ---------- */
  const video = $('#ocean');
  if (video) {
    const conn = navigator.connection || {};
    const light = conn.saveData || /2g/.test(conn.effectiveType || '') || window.innerWidth < 700;
    const src = light ? 'assets/ocean-360.mp4' : 'assets/ocean-720.mp4';
    const vio = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          if (!video.src) { video.src = src; video.load(); }
          video.play().then(() => video.classList.add('is-playing')).catch(() => {});
        } else { video.pause(); }
      });
    }, { rootMargin: '30% 0px' });
    vio.observe(video.closest('section'));
  }

  /* ---------- cursor + magnetic ---------- */
  const cursor = $('#cursor');
  if (cursor && fine && !reduced) {
    let cx = -100, cy = -100, tx = -100, ty = -100;
    window.addEventListener('pointermove', (e) => { tx = e.clientX; ty = e.clientY; cursor.classList.remove('is-hidden'); }, { passive: true });
    document.addEventListener('pointerleave', () => cursor.classList.add('is-hidden'));
    const loop = () => { cx += (tx - cx) * 0.22; cy += (ty - cy) * 0.22; cursor.style.transform = `translate(${cx}px,${cy}px)`; requestAnimationFrame(loop); };
    loop();
    document.addEventListener('pointerover', (e) => {
      const t = e.target.closest('[data-cursor]');
      cursor.classList.toggle('is-link', !!t && t.dataset.cursor === 'link');
      cursor.classList.toggle('is-drag', !!t && t.dataset.cursor === 'drag' && !railST);
    });
    $$('.magnetic').forEach((el) => {
      el.addEventListener('pointermove', (e) => {
        const r = el.getBoundingClientRect();
        const dx = (e.clientX - (r.left + r.width / 2)) * 0.18;
        const dy = (e.clientY - (r.top + r.height / 2)) * 0.3;
        el.style.transform = `translate(${dx}px,${dy}px)`;
      });
      el.addEventListener('pointerleave', () => { el.style.transition = 'transform 0.6s cubic-bezier(0.22,1,0.36,1)'; el.style.transform = ''; setTimeout(() => { el.style.transition = ''; }, 600); });
    });
  }

  /* ---------- rail drag on touch is native; on desktop the pin handles it ---------- */
  window.addEventListener('load', () => { if (hasGsap) ScrollTrigger.refresh(); });
})();
