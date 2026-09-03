/* Case study pages: theme, reveals, reading progress. */
(() => {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));

  // split words for the title reveal
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

  // theme
  const root = document.documentElement;
  const meta = $('meta[name="theme-color"]');
  const setTheme = (light, persist = true) => {
    if (light) root.setAttribute('data-theme', 'light'); else root.removeAttribute('data-theme');
    if (meta) meta.setAttribute('content', light ? '#e9ebe6' : '#0d1110');
    $$('#theme-btn').forEach((b) => b.setAttribute('aria-pressed', String(light)));
    if (persist) { try { localStorage.setItem('theme', light ? 'light' : 'dark'); } catch (e) {} }
  };
  setTheme(root.getAttribute('data-theme') === 'light', false);
  $$('#theme-btn').forEach((b) => b.addEventListener('click', () => setTheme(root.getAttribute('data-theme') !== 'light')));

  // reveals
  const pageIn = () => {
    $$('.cs-head [data-split], .hub__head [data-split]').forEach((el) => el.classList.add('is-in'));
    $$('.cs-head .reveal-up, .hub__head .reveal-up, .hub__list').forEach((el) => el.classList.add('is-in'));
  };
  if (reduced) pageIn(); else setTimeout(pageIn, 120);
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
  $$('.reveal-up').forEach((el) => { if (!el.closest('.cs-head, .hub__head')) io.observe(el); });

  // reading progress
  const bar = $('#progress');
  const article = $('.cs-article');
  if (bar && article) {
    let ticking = false;
    const update = () => {
      ticking = false;
      const rect = article.getBoundingClientRect();
      const total = rect.height - window.innerHeight;
      const p = total > 0 ? Math.min(1, Math.max(0, -rect.top / total)) : 1;
      bar.style.transform = `scaleX(${p.toFixed(4)})`;
    };
    window.addEventListener('scroll', () => { if (!ticking) { requestAnimationFrame(update); ticking = true; } }, { passive: true });
    window.addEventListener('resize', update, { passive: true });
    update();
  }
})();
