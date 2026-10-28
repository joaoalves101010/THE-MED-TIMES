'use strict';
(() => {
  const $ = selector => document.querySelector(selector);
  const panel = $('#search-panel'), searchToggle = $('.search-toggle');
  const menuToggle = $('.menu-toggle'), nav = $('#section-navigation');
  const mobile = window.matchMedia('(max-width: 760px)');
  const closeMenu = (focus = false) => {
    if (!menuToggle || !nav) return;
    menuToggle.setAttribute('aria-expanded', 'false');
    nav.hidden = mobile.matches;
    if (focus) menuToggle.focus();
  };
  const closeSearch = (focus = false) => {
    if (!panel || !searchToggle) return;
    panel.hidden = true;
    searchToggle.setAttribute('aria-expanded', 'false');
    if (focus) searchToggle.focus();
  };
  if (menuToggle && nav) {
    menuToggle.hidden = !mobile.matches;
    closeMenu();
    menuToggle.addEventListener('click', () => {
      const open = menuToggle.getAttribute('aria-expanded') !== 'true';
      closeSearch();
      menuToggle.setAttribute('aria-expanded', String(open));
      nav.hidden = !open;
      if (open) nav.querySelector('a')?.focus();
    });
    mobile.addEventListener('change', () => {
      const hadFocus = nav.contains(document.activeElement);
      menuToggle.hidden = !mobile.matches;
      closeMenu(hadFocus && mobile.matches);
    });
  }
  searchToggle?.addEventListener('click', () => {
    const open = panel.hidden;
    closeMenu();
    panel.hidden = !open;
    searchToggle.setAttribute('aria-expanded', String(open));
    if (open) $('#search').focus();
  });
  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape') return;
    if (panel && !panel.hidden) { closeSearch(true); event.preventDefault(); }
    else if (menuToggle?.getAttribute('aria-expanded') === 'true') { closeMenu(true); event.preventDefault(); }
  });

  const norm = text => String(text || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const typeKey = value => {
    const type = norm(value);
    if (['noticia', 'news'].includes(type)) return 'noticia';
    if (type.includes('analis')) return 'analise';
    return 'guia';
  };
  const rankArticles = (articles, query = '', section = '', type = '', category = '') => {
    const phrase = norm(query.trim()), tokens = phrase.split(/\s+/).filter(Boolean);
    return articles.map((article, index) => {
      if (section && article.section !== section || type && typeKey(article.contentType) !== type || category && norm(article.category) !== norm(category)) return null;
      const title = norm(article.title), deck = norm(article.deck);
      const body = norm([article.category, article.sectionName, ...(article.paragraphs || [])].join(' '));
      if (!tokens.every(token => [title, deck, body].some(field => field.includes(token)))) return null;
      const score = (phrase && title.includes(phrase) ? 100 : 0) + tokens.reduce((sum, token) => sum + (title.includes(token) ? 12 : 0) + (deck.includes(token) ? 4 : 0) + (body.includes(token) ? 1 : 0), 0);
      return { article, score, index };
    }).filter(Boolean).sort((a, b) => b.score - a.score || a.index - b.index).map(item => item.article);
  };
  const params = new URLSearchParams(location.search), data = $('#edition-data');
  if (data) {
    const meta = $('#edition-search-meta');
    const metadata = meta ? JSON.parse(meta.textContent) : {};
    const articles = JSON.parse(data.textContent).map(article => ({ ...article, ...(metadata[article.id] || {}) }));
    const root = data.dataset.root || '';
    const query = params.get('q')?.trim() || '', section = params.get('secao') || '', type = params.get('tipo') || '', category = params.get('editoria') || '';
    if (params.has('q') || section || type || category) {
      $('#front-page').hidden = true;
      $('#filtered-page').hidden = false;
      const results = rankArticles(articles, query, section, type, category);
      $('#results-heading').textContent = query ? 'Busca: “' + query + '”' : 'Busca nesta edição';
      $('#result-count').textContent = results.length + (results.length === 1 ? ' matéria encontrada' : ' matérias encontradas') + ' na edição ' + document.body.dataset.edition + '.';
      $('#empty').hidden = results.length > 0;
      document.title = (query ? 'Busca: ' + query : 'Busca nesta edição') + ' — THE MED TIMES';
      panel.hidden = false;
      searchToggle.setAttribute('aria-expanded', 'true');
      $('#search').value = query;
      $('#search-section').value = section;
      $('#search-type').value = type;
      for (const article of results) {
        const el = document.createElement('article');
        el.className = 'story search-result';
        el.dataset.articleId = article.id;
        const kicker = document.createElement('p');
        kicker.className = 'kicker';
        kicker.textContent = (article.sectionName || article.category) + ' · ' + (article.typeLabel || article.contentType || 'Síntese editorial');
        const title = document.createElement('h2'), anchor = document.createElement('a');
        anchor.href = root + article.url;
        anchor.textContent = article.title;
        title.append(anchor);
        const deck = document.createElement('p'); deck.textContent = article.deck;
        const details = document.createElement('p'); details.className = 'result-metadata';
        details.textContent = (article.dateLabel || 'Data da fonte não informada') + ' · ' + (article.readingMinutes || 1) + ' min de leitura';
        const read = document.createElement('a');
        read.className = 'continue'; read.href = anchor.href; read.textContent = 'Ler matéria e fontes →';
        el.append(kicker, title, deck, details, read);
        $('#results').append(el);
      }
    }
  }

  // Only explicit return clicks restore a position. Ordinary scrolling/back stays native.
  const edition = document.body.dataset.edition;
  const base = panel ? new URL(panel.action, location.href) : new URL('./', location.href);
  const originKey = 'tmt:reading-origin:' + edition, returnKey = 'tmt:reading-return:' + edition;
  const readState = key => { try { return JSON.parse(sessionStorage.getItem(key) || 'null'); } catch { return null; } };
  const writeState = (key, value) => { try { sessionStorage.setItem(key, JSON.stringify(value)); } catch { /* Navigation fallback remains usable. */ } };
  const safeOrigin = record => {
    if (!record || record.edition !== edition || !Number.isFinite(record.y) || record.y < 0 || !Number.isFinite(record.at) || Date.now() - record.at > 172800000 || record.at > Date.now()) return null;
    try {
      const url = new URL(record.url, location.href);
      const prefix = base.pathname.endsWith('/') ? base.pathname : base.pathname + '/';
      const rest = url.pathname.startsWith(prefix) ? url.pathname.slice(prefix.length) : null;
      if (url.origin !== location.origin || rest === null || !(rest === '' || /^editorias\/(pesquisa|clinica|saude-publica|formacao|inovacao|instituicoes)\/$/.test(rest))) return null;
      return { ...record, url: url.pathname + url.search + url.hash };
    } catch { return null; }
  };
  const returnLink = $('[data-return-origin]'), saved = safeOrigin(readState(originKey));
  if (returnLink && saved) {
    returnLink.href = saved.url;
    returnLink.textContent = 'Voltar ao ponto de leitura →';
    returnLink.addEventListener('click', event => {
      if (event.button === 0 && !event.ctrlKey && !event.metaKey && !event.shiftKey && !event.altKey) writeState(returnKey, saved);
    });
  }
  document.addEventListener('click', event => {
    if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || $('[data-current-article]')) return;
    const link = event.target.closest?.('a[href]');
    if (!link || link.target === '_blank') return;
    const url = new URL(link.href, location.href);
    if (url.origin !== location.origin || !url.pathname.includes('/edicao-' + edition + '/artigos/')) return;
    const record = safeOrigin({ edition, url: location.pathname + location.search + location.hash, y: window.scrollY, at: Date.now(), articleId: link.closest('[data-article-id]')?.dataset.articleId || '' });
    if (record) writeState(originKey, record);
  }, true);
  window.addEventListener('pageshow', () => {
    const state = safeOrigin(readState(returnKey));
    if (!state || state.url !== location.pathname + location.search + location.hash) return;
    try { sessionStorage.removeItem(returnKey); } catch { /* No persistent change needed. */ }
    Promise.resolve(document.fonts?.ready).then(() => requestAnimationFrame(() => {
      if (state.articleId && /^[a-z0-9-]+$/.test(state.articleId)) document.querySelector('[data-article-id="' + state.articleId + '"] h2 a')?.focus({ preventScroll: true });
      window.scrollTo({ top: state.y, left: 0, behavior: 'instant' });
    }));
  });
  $('[data-print]')?.addEventListener('click', () => window.print());
  $('[data-copy]')?.addEventListener('click', async () => {
    const status = $('#tool-status');
    try { await navigator.clipboard.writeText(location.href); status.textContent = 'Link copiado.'; }
    catch { status.textContent = 'Copie o endereço na barra do navegador.'; }
  });
  for (const link of document.querySelectorAll('.navrow a')) {
    const url = new URL(link.href, location.href);
    if (url.pathname === location.pathname && !url.search && !location.search) link.setAttribute('aria-current', 'page');
  }
  // Pure, deterministic hooks for tests of the actual shipped implementation.
  window.TMTReading = Object.freeze({ norm, typeKey, rankArticles, safeOrigin });
})();
