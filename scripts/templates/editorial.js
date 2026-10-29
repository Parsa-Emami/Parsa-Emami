(() => {
  const root = document.documentElement;
  const motionControl = document.querySelector('[data-motion-toggle]');
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const wideScreen = matchMedia('(min-width: 1001px)');
  const titles = [...document.querySelectorAll('[data-kinetic]')];
  const progress = document.querySelector('.reading-progress');
  let motionPreference = null;
  let frame = 0;
  try {
    const saved = localStorage.getItem('profile-motion');
    if (saved === 'paused' || saved === 'playing') motionPreference = saved;
  } catch {}
  const motionPaused = () => reducedMotion.matches || motionPreference === 'paused';
  const paint = () => {
    frame = 0;
    if (motionPaused()) return;
    const range = Math.max(1, root.scrollHeight - window.innerHeight);
    if (progress) progress.style.transform = `scaleX(${Math.min(1, Math.max(0, window.scrollY / range))})`;
    for (const title of titles) {
      const bounds = title.getBoundingClientRect();
      const offset = wideScreen.matches ? Math.max(-12, Math.min(12, (bounds.top - window.innerHeight / 2) * 0.025)) : 0;
      title.style.transform = `translateX(${offset}px)`;
    }
  };
  const schedule = () => {
    if (!frame && !motionPaused()) frame = requestAnimationFrame(paint);
  };
  const applyMotion = () => {
    const paused = motionPaused();
    root.dataset.motion = paused ? 'paused' : 'playing';
    if (motionControl) {
      motionControl.hidden = false;
      motionControl.disabled = reducedMotion.matches;
      motionControl.textContent = reducedMotion.matches ? 'Reduced motion' : paused ? 'Play motion' : 'Pause motion';
      motionControl.setAttribute('aria-pressed', String(paused));
    }
    if (paused) {
      if (frame) cancelAnimationFrame(frame);
      frame = 0;
      for (const title of titles) title.style.transform = '';
    } else schedule();
  };
  motionControl?.addEventListener('click', () => {
    motionPreference = motionPaused() ? 'playing' : 'paused';
    try { localStorage.setItem('profile-motion', motionPreference); } catch {}
    applyMotion();
  });
  reducedMotion.addEventListener('change', applyMotion);
  wideScreen.addEventListener('change', schedule);
  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule, { passive: true });
  window.addEventListener('storage', event => {
    if (event.key !== 'profile-motion' && event.key !== null) return;
    motionPreference = ['paused', 'playing'].includes(event.newValue) ? event.newValue : null;
    applyMotion();
  });
  applyMotion();

  const copyButton = document.querySelector('[data-copy-email]');
  const copyStatus = document.querySelector('[data-copy-status]');
  if (copyButton && copyStatus) {
    copyButton.hidden = false;
    copyButton.addEventListener('click', async () => {
      copyButton.disabled = true;
      try {
        await navigator.clipboard.writeText(copyButton.dataset.copyEmail);
        copyStatus.textContent = 'Email copied.';
      } catch {
        copyStatus.textContent = 'Copy unavailable. Select the email address, or use the email link.';
      } finally {
        copyButton.disabled = false;
      }
    });
  }

  const clock = document.querySelector('[data-local-time]');
  if (clock) {
    const formatter = new Intl.DateTimeFormat('en-GB', { timeZone: 'Asia/Tehran', hour: '2-digit', minute: '2-digit' });
    const updateClock = () => {
      const now = new Date();
      clock.dateTime = now.toISOString();
      clock.textContent = `${formatter.format(now)} / IRST`;
    };
    updateClock();
    setInterval(updateClock, 60000);
  }
})();
