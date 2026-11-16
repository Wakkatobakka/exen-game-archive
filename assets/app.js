(() => {
  'use strict';
  const grid = document.getElementById('game-list');
  if (!grid) return;
  const cards = Array.from(grid.querySelectorAll('.record'));
  const search = document.getElementById('game-search');
  const year = document.getElementById('year-filter');
  const genre = document.getElementById('genre-filter');
  const research = document.getElementById('research-filter');
  const sort = document.getElementById('sort-by');
  const result = document.getElementById('result-count');
  const empty = document.getElementById('no-results');
  const reset = document.getElementById('reset-filters');
  const params = new URLSearchParams(location.search);
  const norm = s => String(s).toLocaleLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g, '');
  search.value = (params.get('q') || '').slice(0, 100);
  for (const [control, key] of [[year, 'year'], [genre, 'genre'], [research, 'research'], [sort, 'sort']]) {
    if (Array.from(control.options).some(option => option.value === params.get(key))) {
      control.value = params.get(key);
    }
  }
  function refresh() {
    const needle = norm(search.value.trim());
    let shown = 0;
    cards.forEach(card => {
      const genres = card.dataset.genres.split('|').filter(Boolean);
      const matchesGenre = !genre.value || (genre.value === 'unknown' ? !genres.length : genres.includes(genre.value));
      const matchesCoverage = !research.value ||
        (research.value === 'history' && card.dataset.hasHistory === 'true') ||
        (research.value === 'credits' && card.dataset.hasCredits === 'true') ||
        (research.value === 'listing' && card.dataset.hasHistory !== 'true' && card.dataset.hasCredits !== 'true');
      const matches = (!needle || norm(card.dataset.search).includes(needle)) &&
        (!year.value || card.dataset.year === year.value) && matchesGenre &&
        matchesCoverage;
      card.hidden = !matches;
      if (matches) shown++;
    });
    const comparator = sort.value === 'oldest'
      ? (a, b) => +a.dataset.year - +b.dataset.year || a.dataset.name.localeCompare(b.dataset.name)
      : sort.value === 'newest'
      ? (a, b) => +b.dataset.year - +a.dataset.year || a.dataset.name.localeCompare(b.dataset.name)
      : (a, b) => a.dataset.name.localeCompare(b.dataset.name);
    cards.sort(comparator).forEach(card => grid.appendChild(card));
    result.textContent = `${shown} of ${cards.length} game entries`;
    empty.hidden = shown !== 0;
    reset.hidden = !search.value && !year.value && !genre.value && !research.value && sort.value === 'title';
    const url = new URL(location.href);
    for (const [key, value] of [['q', search.value.trim()], ['year', year.value], ['genre', genre.value], ['research', research.value], ['sort', sort.value === 'title' ? '' : sort.value]]) {
      if (value) url.searchParams.set(key, value);
      else url.searchParams.delete(key);
    }
    try { history.replaceState(null, '', url); } catch (_) { /* Local file previews can restrict history. */ }
  }
  document.getElementById('catalog-filters').hidden = false;
  search.addEventListener('input', refresh);
  for (const control of [year, genre, research, sort]) control.addEventListener('change', refresh);
  reset.addEventListener('click', () => {
    search.value = year.value = genre.value = research.value = '';
    sort.value = 'title';
    refresh();
    search.focus();
  });
  refresh();
})();
