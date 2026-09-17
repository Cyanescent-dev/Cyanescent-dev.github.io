/* ═══════════════════════════════════════════════════════════════
   Cyanescent Player — Website Scripts
   Minimal vanilla JS for navigation, scroll reveals, and
   reduced-motion awareness.
   ═══════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  /* ─── Reduced Motion Detection ─── */

  const prefersReducedMotion = window.matchMedia(
    '(prefers-reduced-motion: reduce)'
  );

  /* ─── Mobile Navigation Toggle ─── */

  const navToggle = document.querySelector('.nav-toggle');
  const navLinks = document.getElementById('nav-links');

  if (navToggle && navLinks) {
    navToggle.addEventListener('click', function () {
      const isOpen = navLinks.classList.toggle('is-open');
      navToggle.setAttribute('aria-expanded', String(isOpen));
    });

    // Close menu when a link is clicked
    navLinks.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        navLinks.classList.remove('is-open');
        navToggle.setAttribute('aria-expanded', 'false');
      });
    });

    // Close menu on Escape key
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && navLinks.classList.contains('is-open')) {
        navLinks.classList.remove('is-open');
        navToggle.setAttribute('aria-expanded', 'false');
        navToggle.focus();
      }
    });
  }

  /* ─── Smooth Scroll for Anchor Links ─── */

  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      const targetId = this.getAttribute('href');
      if (targetId === '#' || targetId.includes('PLACEHOLDER')) return;

      const target = document.querySelector(targetId);
      if (!target) return;

      e.preventDefault();

      const navHeight = document.querySelector('.site-nav')
        ? document.querySelector('.site-nav').offsetHeight
        : 0;

      const targetPosition =
        target.getBoundingClientRect().top + window.scrollY - navHeight;

      if (prefersReducedMotion.matches) {
        window.scrollTo(0, targetPosition);
      } else {
        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth',
        });
      }

      // Update URL without scroll jump
      history.pushState(null, '', targetId);
    });
  });

  /* ─── Scroll Reveal (IntersectionObserver) ─── */

  if (!prefersReducedMotion.matches) {
    const revealElements = document.querySelectorAll('.reveal');

    if ('IntersectionObserver' in window && revealElements.length > 0) {
      const revealObserver = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              entry.target.classList.add('is-visible');
              revealObserver.unobserve(entry.target);
            }
          });
        },
        {
          threshold: 0.1,
          rootMargin: '0px 0px -40px 0px',
        }
      );

      revealElements.forEach(function (el) {
        revealObserver.observe(el);
      });
    }
  } else {
    // If reduced motion, make everything visible immediately
    document.querySelectorAll('.reveal').forEach(function (el) {
      el.classList.add('is-visible');
    });
  }

  /* ─── Navigation Background Opacity on Scroll ─── */

  const siteNav = document.querySelector('.site-nav');

  if (siteNav) {
    let lastScrollY = 0;
    let ticking = false;

    function updateNav() {
      const scrollY = window.scrollY;
      if (scrollY > 80) {
        siteNav.classList.add('is-scrolled');
      } else {
        siteNav.classList.remove('is-scrolled');
      }
      ticking = false;
    }

    window.addEventListener('scroll', function () {
      lastScrollY = window.scrollY;
      if (!ticking) {
        requestAnimationFrame(updateNav);
        ticking = true;
      }
    }, { passive: true });

    // Run once on load
    updateNav();
  }

  /* ─── Pause Hero Animation When Not Visible ─── */

  const heroBg = document.querySelector('.hero-bg');

  if (heroBg && !prefersReducedMotion.matches && 'IntersectionObserver' in window) {
    const heroObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            heroBg.style.animationPlayState = 'running';
          } else {
            heroBg.style.animationPlayState = 'paused';
          }
        });
      },
      { threshold: 0 }
    );

    heroObserver.observe(heroBg);
  }

  /* ─── Pause Video Placeholder Glow When Not Visible ─── */

  const videoPlayIcon = document.querySelector('.video-play-icon');

  if (videoPlayIcon && !prefersReducedMotion.matches && 'IntersectionObserver' in window) {
    const videoObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            videoPlayIcon.style.animationPlayState = 'running';
          } else {
            videoPlayIcon.style.animationPlayState = 'paused';
          }
        });
      },
      { threshold: 0 }
    );

    videoObserver.observe(videoPlayIcon);
  }

})();
