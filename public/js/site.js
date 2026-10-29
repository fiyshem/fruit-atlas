(() => {
  'use strict';
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

  function setupSidebar() {
    const body = document.body;
    const toggleButton = $('#sidebarMenuToggle');
    const scrim = $('#sidebarScrim');
    const mobileQuery = window.matchMedia('(max-width: 980px)');
    const storageKey = 'fruit-atlas-sidebar-hidden';
    const updateToggle = (expanded) => {
      if (!toggleButton) return;
      toggleButton.setAttribute('aria-expanded', String(expanded));
      toggleButton.setAttribute('aria-label', expanded ? 'Collapse navigation sidebar' : 'Expand navigation sidebar');
      toggleButton.title = expanded ? 'Collapse navigation sidebar' : 'Expand navigation sidebar';
    };
    const closeMobile = () => {
      body.classList.remove('sidebar-open-mobile', 'no-scroll');
      updateToggle(false);
    };
    const setDesktopHidden = (hidden, persist = true) => {
      body.classList.toggle('sidebar-hidden', hidden);
      updateToggle(!hidden);
      if (persist) {
        try { localStorage.setItem(storageKey, hidden ? '1' : '0'); } catch (_) { /* Storage may be disabled. */ }
      }
    };
    const initialise = () => {
      if (mobileQuery.matches) {
        body.classList.remove('sidebar-hidden');
        closeMobile();
      } else {
        let hidden = false;
        try { hidden = localStorage.getItem(storageKey) === '1'; } catch (_) { /* Storage may be disabled. */ }
        setDesktopHidden(hidden, false);
      }
    };
    initialise();
    if (toggleButton) toggleButton.addEventListener('click', () => {
      if (mobileQuery.matches) {
        const open = !body.classList.contains('sidebar-open-mobile');
        body.classList.toggle('sidebar-open-mobile', open);
        body.classList.toggle('no-scroll', open);
        updateToggle(open);
      } else {
        setDesktopHidden(!body.classList.contains('sidebar-hidden'));
      }
    });
    if (scrim) scrim.addEventListener('click', closeMobile);
    $$('.side-link').forEach(link => link.addEventListener('click', () => { if (mobileQuery.matches) closeMobile(); }));
    document.addEventListener('keydown', event => { if (event.key === 'Escape' && body.classList.contains('sidebar-open-mobile')) closeMobile(); });
    window.addEventListener('resize', initialise);
  }

  function setupDropdowns() {
    const menus = $$('.topbar-dropdown');
    const closeOthers = current => menus.forEach(menu => { if (menu !== current) menu.removeAttribute('open'); });
    menus.forEach(menu => {
      const summary = $('summary', menu);
      if (!summary) return;
      summary.addEventListener('click', () => window.requestAnimationFrame(() => { if (menu.open) closeOthers(menu); }));
    });
    document.addEventListener('click', event => {
      if (!event.target.closest('.topbar-dropdown')) menus.forEach(menu => menu.removeAttribute('open'));
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape') {
        const openMenu = menus.find(menu => menu.open);
        menus.forEach(menu => menu.removeAttribute('open'));
        if (openMenu) $('summary', openMenu)?.focus();
      }
    });
  }

  const imageCache = new Map();
  function readCachedImage(title) {
    if (imageCache.has(title)) return imageCache.get(title);
    try {
      const raw = localStorage.getItem(`fruit-atlas-img:${title.toLowerCase()}`);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed && parsed.source) { imageCache.set(title, parsed.source); return parsed.source; }
      }
    } catch (_) { /* Cache is an optional performance enhancement. */ }
    return null;
  }
  function cacheImage(title, source) {
    imageCache.set(title, source);
    try { localStorage.setItem(`fruit-atlas-img:${title.toLowerCase()}`, JSON.stringify({ source, savedAt: Date.now() })); } catch (_) { /* Ignore quota or privacy-mode errors. */ }
  }
  async function fetchWikiImage(title) {
    const cached = readCachedImage(title);
    if (cached) return cached;
    const endpoint = `https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(title.replace(/ /g, '_'))}`;
    try {
      const response = await fetch(endpoint, { headers: { Accept: 'application/json' }, mode: 'cors', credentials: 'omit' });
      if (!response.ok) return null;
      const page = await response.json();
      const source = page?.thumbnail?.source || page?.originalimage?.source || null;
      if (source && /^https:\/\//i.test(source)) { cacheImage(title, source); return source; }
    } catch (_) { /* Online imagery is optional; the bundled page still works without it. */ }
    return null;
  }
  function setupImages() {
    const images = $$('img[data-wiki-page], img[data-image-fallback]');
    const genericFruitImage = 'https://images.unsplash.com/photo-1490474418585-ba9bad8fd0ea?auto=format&fit=crop&w=1200&q=80';
    const genericNatureImage = 'https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=1200&q=80';
    images.forEach(img => {
      const fallback = img.dataset.imageFallback || img.getAttribute('src') || '';
      img.addEventListener('error', () => {
        // Try the page's intended fallback first, then a known general fruit photo.
        // Broken remote photos should not leave the browser's broken-image glyph on cards.
        const stage = Number(img.dataset.fallbackStage || 0);
        if (stage === 0 && fallback && img.src !== fallback) {
          img.dataset.fallbackStage = '1';
          img.src = fallback;
          return;
        }
        const naturalSubject = /forest|woodland|canopy|botanical|blossom|leaf|leaves|plant|biology|ecology|habitat|landscape|garden|seed|flower|orchard/i.test(img.alt || '');
        const genericImage = naturalSubject ? genericNatureImage : genericFruitImage;
        if (stage <= 1 && img.src !== genericImage) {
          img.dataset.fallbackStage = '2';
          img.src = genericImage;
          return;
        }
        img.classList.add('image-unavailable');
        img.removeAttribute('src');
      });
      img.addEventListener('load', () => {
        img.classList.remove('image-unavailable');
        img.classList.add('is-loaded');
      }, { once: true });
      // Image requests can fail before deferred setup runs, so inspect completed images too.
      if (img.complete && img.naturalWidth === 0) {
        if (fallback && img.src !== fallback) {
          img.dataset.fallbackStage = '1';
          img.src = fallback;
        } else {
          img.dataset.fallbackStage = '2';
          const naturalSubject = /forest|woodland|canopy|botanical|blossom|leaf|leaves|plant|biology|ecology|habitat|landscape|garden|seed|flower|orchard/i.test(img.alt || '');
          img.src = naturalSubject ? genericNatureImage : genericFruitImage;
        }
      }
    });
    // Resolve only a modest number of images at once and let the browser lazy-load the rest.
    const queue = images.filter(img => img.dataset.wikiPage && img.dataset.wikiPage.length < 70);
    const runBatch = async batch => {
      const titles = [...new Set(batch.map(img => img.dataset.wikiPage).filter(Boolean))];
      const pairs = await Promise.all(titles.map(async title => [title, await fetchWikiImage(title)]));
      const resolved = new Map(pairs.filter(pair => pair[1]));
      batch.forEach(img => {
        const title = img.dataset.wikiPage;
        const source = resolved.get(title);
        if (source && img.isConnected && img.dataset.fallbackStage !== '2') {
          img.src = source;
          img.dataset.imageResolved = '1';
        }
      });
    };
    const seen = new WeakSet();
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver(entries => {
        entries.filter(entry => entry.isIntersecting).forEach(entry => {
          observer.unobserve(entry.target);
          if (!seen.has(entry.target)) { seen.add(entry.target); runBatch([entry.target]); }
        });
      }, { rootMargin: '250px 0px' });
      queue.forEach(img => observer.observe(img));
    } else {
      runBatch(queue.slice(0, 8));
    }
  }

  function setupSearchSuggestions() {
    const inputs = $$('.topbar-search input, .hero-search input, #catalogSearch, #searchPageInput');
    inputs.forEach((input, inputIndex) => {
      const form = input.closest('form');
      if (!form) return;
      form.classList.add('has-suggestions');
      const list = document.createElement('div');
      list.className = 'search-suggestions';
      list.hidden = true;
      list.id = `fruit-suggestions-${input.id || inputIndex}`;
      list.setAttribute('role', 'listbox');
      input.setAttribute('aria-autocomplete', 'list');
      input.setAttribute('aria-controls', list.id);
      input.setAttribute('aria-expanded', 'false');
      form.appendChild(list);
      let requestId = 0;
      let hideTimer;
      let activeIndex = -1;
      const options = () => $$('.search-suggestions a[role="option"]', list);
      const setActive = nextIndex => {
        const rows = options();
        activeIndex = rows.length ? Math.max(0, Math.min(nextIndex, rows.length - 1)) : -1;
        rows.forEach((row, index) => {
          const active = index === activeIndex;
          row.setAttribute('aria-selected', String(active));
          row.classList.toggle('is-active', active);
        });
        if (activeIndex >= 0) input.setAttribute('aria-activedescendant', rows[activeIndex].id);
        else input.removeAttribute('aria-activedescendant');
      };
      const hide = () => {
        list.hidden = true;
        list.replaceChildren();
        activeIndex = -1;
        input.setAttribute('aria-expanded', 'false');
        input.removeAttribute('aria-activedescendant');
      };
      input.addEventListener('input', async () => {
        const query = input.value.trim();
        const currentRequest = ++requestId;
        activeIndex = -1;
        input.removeAttribute('aria-activedescendant');
        if (query.length < 2) { hide(); return; }
        list.replaceChildren();
        list.hidden = true;
        input.setAttribute('aria-expanded', 'false');
        try {
          const response = await fetch(`/api/fruits?q=${encodeURIComponent(query)}&limit=7`, { headers: { Accept: 'application/json' } });
          if (!response.ok) return hide();
          const data = await response.json();
          if (currentRequest !== requestId) return;
          list.replaceChildren();
          (data.results || []).forEach((item, index) => {
            const link = document.createElement('a');
            link.href = item.url;
            link.id = `${list.id}-option-${index}`;
            link.setAttribute('role', 'option');
            link.setAttribute('aria-selected', 'false');
            const name = document.createElement('strong');
            name.textContent = item.name;
            const detail = document.createElement('small');
            detail.textContent = `${item.recordType} · ${item.scientificName}`;
            link.append(name, detail);
            list.appendChild(link);
          });
          if (!list.childElementCount) {
            const empty = document.createElement('div');
            empty.className = 'search-suggestions-empty';
            empty.textContent = 'No close match. Press Enter to search all records.';
            list.appendChild(empty);
          }
          list.hidden = false;
          input.setAttribute('aria-expanded', 'true');
        } catch (_) { hide(); }
      });
      input.addEventListener('focus', () => {
        clearTimeout(hideTimer);
        if (list.childElementCount && input.value.trim().length >= 2) {
          list.hidden = false;
          input.setAttribute('aria-expanded', 'true');
        }
      });
      input.addEventListener('blur', () => { hideTimer = window.setTimeout(hide, 180); });
      input.addEventListener('keydown', event => {
        const rows = options();
        if (event.key === 'ArrowDown' && !list.hidden && rows.length) {
          event.preventDefault();
          setActive(activeIndex + 1);
        } else if (event.key === 'ArrowUp' && !list.hidden && rows.length) {
          event.preventDefault();
          setActive(activeIndex < 0 ? rows.length - 1 : activeIndex - 1);
        } else if (event.key === 'Enter' && !list.hidden && activeIndex >= 0 && rows[activeIndex]) {
          event.preventDefault();
          window.location.href = rows[activeIndex].href;
        } else if (event.key === 'Escape') {
          hide();
        }
      });
      list.addEventListener('mousedown', event => event.preventDefault());
      list.addEventListener('mousemove', event => {
        const row = event.target.closest('a[role="option"]');
        if (row) setActive(options().indexOf(row));
      });
      document.addEventListener('click', event => {
        if (!form.contains(event.target)) hide();
      });
    });
  }

  function setupSeasonExplorer() {
    const select = $('#seasonRegion');
    const panels = $$('[data-season-panel]');
    if (!select || !panels.length) return;
    const show = value => panels.forEach(panel => {
      const active = panel.dataset.seasonPanel === value;
      panel.classList.toggle('is-active', active);
      panel.setAttribute('aria-hidden', String(!active));
    });
    select.addEventListener('change', () => show(select.value));
    show(select.value);
  }

  function setupChecklists() {
    $$('.checklist-panel input[type="checkbox"]').forEach(input => {
      input.addEventListener('change', () => input.closest('label')?.classList.toggle('checked', input.checked));
    });
  }

  function setupFooterDetails() {
    // Native <details> intentionally manages the expandable, multi-column footer.
    // This does not overlay or cover the page: the document reflows when opened.
    $$('.footer-drawer').forEach(details => {
      const syncState = () => {
        const summary = $('summary', details);
        const action = $('.footer-drawer-action', details);
        if (summary) summary.setAttribute('aria-expanded', String(details.open));
        if (action && action.firstChild) action.firstChild.textContent = details.open ? 'Collapse directory ' : 'Expand directory ';
      };
      details.addEventListener('toggle', syncState);
      syncState();
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    setupSidebar();
    setupDropdowns();
    setupImages();
    setupSearchSuggestions();
    setupSeasonExplorer();
    setupChecklists();
    setupFooterDetails();
  });
})();
