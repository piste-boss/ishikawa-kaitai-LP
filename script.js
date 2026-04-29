(function () {
  'use strict';

  // === Hero parallax ===
  const heroImg = document.getElementById('hero-img');
  const heroBigword = document.getElementById('hero-bigword');
  let ticking = false;
  const onScroll = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      const y = window.scrollY;
      if (heroImg) {
        heroImg.style.transform = 'translateY(' + (y * 0.3) + 'px) scale(1.05)';
      }
      if (heroBigword) {
        heroBigword.style.transform = 'translate(0, ' + (-y * 0.15) + 'px)';
      }
      ticking = false;
    });
  };
  window.addEventListener('scroll', onScroll, { passive: true });

  // === Scroll reveal observer ===
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) {
        e.target.classList.add('in');
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -10% 0px' });

  document.querySelectorAll('.reveal').forEach((el) => io.observe(el));

  // === Apply form: experience selector ===
  const expOpts = document.getElementById('expOpts');
  const expField = document.getElementById('expField');
  if (expOpts && expField) {
    expOpts.addEventListener('click', (ev) => {
      const btn = ev.target.closest('.apply__exp-opt');
      if (!btn) return;
      expOpts.querySelectorAll('.apply__exp-opt').forEach((b) => b.classList.remove('is-on'));
      btn.classList.add('is-on');
      expField.value = btn.dataset.val;
    });
  }

  // === Apply form: submit handling ===
  const form = document.getElementById('applyForm');
  const done = document.getElementById('applyDone');
  if (form && done) {
    form.addEventListener('submit', (ev) => {
      // If running on Netlify, the form will be POSTed normally and the page reloads.
      // For local/static preview without Netlify, fake a successful submit.
      const isNetlify = window.location.hostname.endsWith('.netlify.app') || window.location.hostname.endsWith('.netlify.com');
      if (!isNetlify) {
        ev.preventDefault();
        form.style.display = 'none';
        done.style.display = 'block';
      }
    });
  }
})();
