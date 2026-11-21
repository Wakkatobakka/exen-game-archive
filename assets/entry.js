(() => {
  'use strict';
  const footer = document.querySelector('.footer-vision');
  if (footer?.textContent.trim() === 'A true archive of the game and its history, not just a file.') {
    footer.textContent = 'Game histories, creator credits and original sources.';
  }
  const viewer = document.getElementById('image-viewer');
  if (viewer && typeof viewer.showModal === 'function') {
    const image = document.getElementById('viewer-image');
    const canvas = document.getElementById('viewer-canvas');
    const zoom = document.getElementById('viewer-zoom');
    let trigger;
    for (const link of document.querySelectorAll('[data-image]')) {
      link.addEventListener('click', event => {
        if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        trigger = link;
        image.src = link.dataset.image;
        image.alt = link.dataset.caption;
        document.getElementById('viewer-title').textContent = link.dataset.caption;
        canvas.classList.remove('zoomed');
        zoom.textContent = 'Zoom in';
        zoom.setAttribute('aria-pressed', 'false');
        viewer.showModal();
        canvas.scrollTo(0, 0);
      });
    }
    zoom.addEventListener('click', () => {
      const on = canvas.classList.toggle('zoomed');
      zoom.textContent = on ? 'Fit image' : 'Zoom in';
      zoom.setAttribute('aria-pressed', String(on));
    });
    document.getElementById('viewer-close').addEventListener('click', () => viewer.close());
    viewer.addEventListener('close', () => trigger?.focus());
  }
  if ('IntersectionObserver' in window) {
    const links = [...document.querySelectorAll('.entry-contents a')];
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        for (const link of links) {
          if (link.hash === '#' + entry.target.id) link.setAttribute('aria-current', 'location');
          else link.removeAttribute('aria-current');
        }
      }
    }, { rootMargin: '-5% 0px -60% 0px', threshold: 0 });
    for (const section of document.querySelectorAll('.game-entry>.entry-section')) observer.observe(section);
  }
})();
