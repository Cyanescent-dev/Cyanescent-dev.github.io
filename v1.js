/* ═══════════════════════════════════════════════════════════════
   Cyanescent Player 1.0 — Website Scripts
   Progressive enhancement only: every section works without JS.
   ═══════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  /* ─── Mobile navigation ─── */

  var toggle = document.querySelector('.nav-toggle');
  var links = document.getElementById('nav-links');

  if (toggle && links) {
    var setOpen = function (open) {
      links.classList.toggle('is-open', open);
      toggle.setAttribute('aria-expanded', String(open));
    };

    toggle.addEventListener('click', function () {
      setOpen(!links.classList.contains('is-open'));
    });

    links.addEventListener('click', function (e) {
      if (e.target.closest('a')) setOpen(false);
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && links.classList.contains('is-open')) {
        setOpen(false);
        toggle.focus();
      }
    });
  }

  /* ─── Launch-pending controls ─── */

  // Buttons awaiting a verified download/checkout URL have no href;
  // keep them out of the tab order so keyboard users are not trapped.
  document.querySelectorAll('[aria-disabled="true"]').forEach(function (el) {
    el.setAttribute('tabindex', '-1');
  });

  /* ─── Scroll reveal ─── */

  var reveals = document.querySelectorAll('.reveal');

  if (reducedMotion.matches || !('IntersectionObserver' in window)) {
    reveals.forEach(function (el) { el.classList.add('is-visible'); });
  } else {
    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

    reveals.forEach(function (el) { revealObserver.observe(el); });
  }

  /* ─── Pause decorative animation when off-screen ─── */

  if ('IntersectionObserver' in window) {
    var animated = document.querySelectorAll('.portal');
    var animObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        var state = entry.isIntersecting ? 'running' : 'paused';
        entry.target.style.animationPlayState = state;
        entry.target.querySelectorAll('*').forEach(function (child) {
          child.style.animationPlayState = state;
        });
      });
    });
    animated.forEach(function (el) { animObserver.observe(el); });
  }

  /* ─── Gallery lightbox ─── */

  var dialog = document.querySelector('.lightbox');
  var gallery = document.querySelector('[data-gallery]');

  if (dialog && gallery && typeof dialog.showModal === 'function') {
    var dialogImg = dialog.querySelector('img');
    var dialogTitle = dialog.querySelector('[data-lightbox-title]');
    var opener = null;

    gallery.addEventListener('click', function (e) {
      var button = e.target.closest('button[data-full]');
      if (!button) return;
      opener = button;
      dialogImg.src = button.getAttribute('data-full');
      dialogImg.alt = button.querySelector('img').alt;
      dialogTitle.textContent = button.getAttribute('data-title');
      dialog.showModal();
    });

    dialog.querySelector('.lightbox-close').addEventListener('click', function () {
      dialog.close();
    });

    // Click on the backdrop closes the dialog.
    dialog.addEventListener('click', function (e) {
      if (e.target === dialog) dialog.close();
    });

    dialog.addEventListener('close', function () {
      dialogImg.removeAttribute('src');
      if (opener) opener.focus();
    });
  } else if (gallery) {
    // No <dialog> support: open the full-size image directly.
    gallery.addEventListener('click', function (e) {
      var button = e.target.closest('button[data-full]');
      if (button) window.location.href = button.getAttribute('data-full');
    });
  }
})();
