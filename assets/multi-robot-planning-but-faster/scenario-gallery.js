document.querySelectorAll('[data-scenario-gallery]').forEach(gallery => {
  const video = gallery.querySelector('video');
  const captionTitle = gallery.querySelector('figcaption .scenario-gallery__title');
  const captionMeta = gallery.querySelector('figcaption .scenario-gallery__meta');
  const choices = gallery.querySelectorAll('[data-gallery-clip]');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const play = () => video.play().catch(() => {});

  choices.forEach(choice => choice.addEventListener('click', event => {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    video.pause();
    video.poster = choice.dataset.poster;
    video.src = choice.href;
    video.setAttribute('aria-label', `${choice.dataset.title}, ${choice.dataset.robots} robots, ${choice.dataset.targets} targets`);
    captionTitle.textContent = choice.dataset.title;
    captionMeta.textContent = `${choice.dataset.robots} robots · ${choice.dataset.targets} targets`;
    choices.forEach(item => item.removeAttribute('aria-current'));
    choice.setAttribute('aria-current', 'true');
    play();
  }));

  // Keep off-screen galleries idle; explicit playback also works without JS.
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) video.pause();
        else if (!reducedMotion.matches) play();
      });
    }, { threshold: .25 });
    observer.observe(video);
  }
});
