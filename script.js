const sections = document.querySelectorAll('.reveal');
const disableReveal = window.matchMedia('(max-width: 980px), (pointer: coarse)').matches;

if (disableReveal || !('IntersectionObserver' in window)) {
  sections.forEach((section) => section.classList.add('in'));
} else {
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
    {
      threshold: 0.05,
      rootMargin: '0px 0px -10% 0px',
    }
  );

  sections.forEach((section) => observer.observe(section));
}

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

const menu = document.querySelector('[data-menu]');

if (menu) {
  const panels = [...menu.querySelectorAll('[data-menu-panel]')];
  const filters = [...menu.querySelectorAll('[data-menu-filter]')];
  const search = menu.querySelector('[data-menu-search]');
  let activeFilter = 'all';

  const applyMenuFilters = () => {
    const term = (search?.value || '').trim().toLowerCase();

    panels.forEach((panel) => {
      const items = [...panel.querySelectorAll('[data-menu-item]')];
      const empty = panel.querySelector('.menu-empty');
      const count = panel.querySelector('[data-menu-count]');
      let visibleCount = 0;

      items.forEach((item) => {
        const hasCoffee = item.dataset.hasCoffee === 'yes';
        const name = (item.dataset.name || '').toLowerCase();
        const text = item.textContent.toLowerCase();
        const matchesSearch = !term || name.includes(term) || text.includes(term);
        const matchesFilter =
          activeFilter === 'all' ||
          (activeFilter === 'coffee' && hasCoffee) ||
          (activeFilter === 'nocoffee' && !hasCoffee);

        const visible = matchesSearch && matchesFilter;
        item.classList.toggle('is-hidden', !visible);

        if (visible) {
          visibleCount += 1;
        }
      });

      empty?.classList.toggle('is-visible', visibleCount === 0);

      if (count) {
        count.textContent = `${visibleCount} ${visibleCount === 1 ? 'opcion' : 'opciones'}`;
      }
    });
  };

  filters.forEach((filter) => {
    filter.addEventListener('click', () => {
      activeFilter = filter.dataset.menuFilter || 'all';
      filters.forEach((btn) => btn.classList.toggle('is-active', btn === filter));
      applyMenuFilters();
    });
  });

  search?.addEventListener('input', applyMenuFilters);

  applyMenuFilters();
}

const serviceStatusNodes = [
  ...document.querySelectorAll('[data-service-status], [data-service-status-inline]'),
];

if (serviceStatusNodes.length) {
  const LOCAL_TIME_ZONE = 'America/Mexico_City';
  const OPEN_DAYS = new Set([0, 1, 5, 6]);
  const OPEN_MINUTES = 18 * 60;
  const CLOSE_MINUTES = 23 * 60;
  const weekdayMap = {
    Sun: 0,
    Mon: 1,
    Tue: 2,
    Wed: 3,
    Thu: 4,
    Fri: 5,
    Sat: 6,
  };

  const localTimeFormatter = new Intl.DateTimeFormat('en-US', {
    timeZone: LOCAL_TIME_ZONE,
    weekday: 'short',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });

  const updateServiceStatus = () => {
    const now = new Date();
    const parts = localTimeFormatter.formatToParts(now);
    const weekday = parts.find((part) => part.type === 'weekday')?.value;
    const hour = Number(parts.find((part) => part.type === 'hour')?.value || 0);
    const minute = Number(parts.find((part) => part.type === 'minute')?.value || 0);
    const dayIndex = weekdayMap[weekday] ?? -1;
    const currentMinutes = hour * 60 + minute;
    const isOpen =
      OPEN_DAYS.has(dayIndex) &&
      currentMinutes >= OPEN_MINUTES &&
      currentMinutes < CLOSE_MINUTES;

    serviceStatusNodes.forEach((node) => {
      const isInline = node.hasAttribute('data-service-status-inline');
      node.textContent = isOpen
        ? isInline
          ? 'Abierto ahora'
          : '(El patio de Le Café está abierto)'
        : isInline
          ? 'Cerrado ahora'
          : '(El patio de Le Café está cerrado)';
      node.classList.toggle('is-open', isOpen);
      node.classList.toggle('is-closed', !isOpen);
    });
  };

  updateServiceStatus();
  window.setInterval(updateServiceStatus, 60000);
}
