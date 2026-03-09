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

const menu = document.querySelector('[data-menu]');

if (menu) {
  const tabs = [...menu.querySelectorAll('[data-menu-tab]')];
  const panels = [...menu.querySelectorAll('[data-menu-panel]')];
  const filters = [...menu.querySelectorAll('[data-menu-filter]')];
  const search = menu.querySelector('[data-menu-search]');

  let activeTab = 'solo';
  let activeFilter = 'all';

  const applyTab = (tabId) => {
    activeTab = tabId;

    tabs.forEach((tab) => {
      const isActive = tab.dataset.menuTab === tabId;
      tab.classList.toggle('is-active', isActive);
      tab.setAttribute('aria-selected', isActive ? 'true' : 'false');
    });

    panels.forEach((panel) => {
      panel.classList.toggle('is-active', panel.dataset.menuPanel === tabId);
    });

    applyMenuFilters();
  };

  const applyMenuFilters = () => {
    const term = (search?.value || '').trim().toLowerCase();

    panels.forEach((panel) => {
      const isCurrentPanel = panel.dataset.menuPanel === activeTab;
      const items = [...panel.querySelectorAll('[data-menu-item]')];
      const empty = panel.querySelector('.menu-empty');
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

        const visible = isCurrentPanel && matchesSearch && matchesFilter;
        item.classList.toggle('is-hidden', !visible);

        if (visible) {
          visibleCount += 1;
        }
      });

      empty?.classList.toggle('is-visible', isCurrentPanel && visibleCount === 0);
    });
  };

  tabs.forEach((tab) => {
    tab.addEventListener('click', () => applyTab(tab.dataset.menuTab));
  });

  filters.forEach((filter) => {
    filter.addEventListener('click', () => {
      activeFilter = filter.dataset.menuFilter || 'all';
      filters.forEach((btn) => btn.classList.toggle('is-active', btn === filter));
      applyMenuFilters();
    });
  });

  search?.addEventListener('input', applyMenuFilters);

  applyTab(activeTab);
}
