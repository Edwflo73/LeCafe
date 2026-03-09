const sections = document.querySelectorAll('.reveal');

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) {
        return;
      }
      entry.target.classList.add('in');
      observer.unobserve(entry.target);
    });
  },
  { threshold: 0.16 }
);

sections.forEach((section) => observer.observe(section));

const carousel = document.querySelector('[data-carousel]');

if (carousel) {
  const slides = [...carousel.querySelectorAll('[data-carousel-slide]')];
  const dots = [...carousel.querySelectorAll('[data-carousel-dot]')];
  const prevBtn = carousel.querySelector('[data-carousel-prev]');
  const nextBtn = carousel.querySelector('[data-carousel-next]');

  let index = 0;
  let autoplayId = null;
  let paused = false;
  let touchStartX = 0;
  let touchEndX = 0;

  const setActive = (nextIndex) => {
    index = (nextIndex + slides.length) % slides.length;

    slides.forEach((slide, i) => {
      slide.classList.toggle('is-active', i === index);
    });

    dots.forEach((dot, i) => {
      dot.classList.toggle('is-active', i === index);
      dot.setAttribute('aria-selected', i === index ? 'true' : 'false');
      dot.setAttribute('tabindex', i === index ? '0' : '-1');
    });
  };

  const next = () => setActive(index + 1);
  const prev = () => setActive(index - 1);

  const stopAutoplay = () => {
    if (autoplayId) {
      window.clearInterval(autoplayId);
      autoplayId = null;
    }
  };

  const startAutoplay = () => {
    if (paused) {
      return;
    }
    stopAutoplay();
    autoplayId = window.setInterval(next, 7000);
  };

  prevBtn?.addEventListener('click', () => {
    prev();
    startAutoplay();
  });

  nextBtn?.addEventListener('click', () => {
    next();
    startAutoplay();
  });

  dots.forEach((dot, dotIndex) => {
    dot.addEventListener('click', () => {
      setActive(dotIndex);
      startAutoplay();
    });
  });

  carousel.addEventListener('mouseenter', () => {
    paused = true;
    stopAutoplay();
  });

  carousel.addEventListener('mouseleave', () => {
    paused = false;
    startAutoplay();
  });

  carousel.addEventListener('focusin', () => {
    paused = true;
    stopAutoplay();
  });

  carousel.addEventListener('focusout', () => {
    paused = false;
    startAutoplay();
  });

  carousel.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowLeft') {
      prev();
      startAutoplay();
    }
    if (event.key === 'ArrowRight') {
      next();
      startAutoplay();
    }
  });

  carousel.addEventListener(
    'touchstart',
    (event) => {
      touchStartX = event.changedTouches[0].screenX;
    },
    { passive: true }
  );

  carousel.addEventListener(
    'touchend',
    (event) => {
      touchEndX = event.changedTouches[0].screenX;
      const delta = touchEndX - touchStartX;
      if (Math.abs(delta) < 40) {
        return;
      }
      if (delta > 0) {
        prev();
      } else {
        next();
      }
      startAutoplay();
    },
    { passive: true }
  );

  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      stopAutoplay();
    } else {
      startAutoplay();
    }
  });

  setActive(0);
  startAutoplay();
}
