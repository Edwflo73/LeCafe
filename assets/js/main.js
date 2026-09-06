  // header scroll state
  const header = document.getElementById('siteHeader');
  window.addEventListener('scroll', () => {
    header.classList.toggle('scrolled', window.scrollY > 40);
  });

  // footer "volver arriba" — smooth scroll to top of current page
  document.querySelectorAll('.js-top').forEach(a => {
    a.addEventListener('click', (e) => {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });

  // mobile menu
  const burger = document.getElementById('burgerBtn');
  const panel = document.getElementById('mobilePanel');
  burger.addEventListener('click', () => {
    const open = panel.classList.toggle('open');
    burger.classList.toggle('open', open);
  });
  panel.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
    panel.classList.remove('open');
    burger.classList.remove('open');
  }));

  // menu tabs
  const tabBtns = document.querySelectorAll('.tab-btn');
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');
      document.querySelectorAll('.menu-panel').forEach(p => p.classList.remove('active'));
      document.getElementById('panel-' + btn.dataset.tab).classList.add('active');
    });
  });

  // scroll reveal
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('is-visible');
        observer.unobserve(e.target);
      }
    });
  }, { threshold: 0.12 });
  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

  // menu tabs — replays every time the row scrolls back into view (unlike
  // .reveal above, this observer never unobserves: it just toggles the class
  // on and off as the row crosses the viewport edge)
  const tabsAnimObserver = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      e.target.classList.toggle('is-visible', e.isIntersecting);
    });
  }, { threshold: 0.2 });
  document.querySelectorAll('.tabs-animate').forEach(el => tabsAnimObserver.observe(el));

  // reservation form -> compose whatsapp message (only present on ubicacion.html)
  const resForm = document.getElementById('resForm');
  if (resForm) {
    resForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const name = document.getElementById('f-name').value || 'Sin nombre';
      const date = document.getElementById('f-date').value || 'por confirmar';
      const time = document.getElementById('f-time').value || 'por confirmar';
      const people = document.getElementById('f-people').value || '2';
      const notes = document.getElementById('f-notes').value || '';
      const msg = `Hola, soy ${name}. Quiero reservar mesa para ${people} persona(s) el ${date} a las ${time}. ${notes}`;
      window.open('https://wa.me/522294334031?text=' + encodeURIComponent(msg), '_blank');
    });
  }

  // photo gallery + lightbox
  (function(){
    const galleryButtons = Array.from(document.querySelectorAll('.gallery-item'));
    const linkedImgs = Array.from(document.querySelectorAll('img.gallery-linked'));

    // build a single ordered list: hero, espacio, then all gallery strip photos
    const items = [];
    linkedImgs.forEach(img => {
      items.push({ src: img.src, caption: img.dataset.galleryCaption || '' });
    });
    galleryButtons.forEach(btn => {
      items.push({ src: btn.dataset.gallerySrc, caption: btn.dataset.galleryCaption || '' });
    });

    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightboxImg');
    const lightboxCaption = document.getElementById('lightboxCaption');
    const lightboxCounter = document.getElementById('lightboxCounter');
    let current = 0;

    function render(){
      const item = items[current];
      lightboxImg.src = item.src;
      lightboxImg.alt = item.caption;
      lightboxCaption.textContent = item.caption;
      lightboxCounter.textContent = (current + 1) + ' / ' + items.length;
    }
    function open(index){
      current = index;
      render();
      lightbox.classList.add('open');
      document.body.style.overflow = 'hidden';
    }
    function close(){
      lightbox.classList.remove('open');
      document.body.style.overflow = '';
    }
    function next(){ current = (current + 1) % items.length; render(); }
    function prev(){ current = (current - 1 + items.length) % items.length; render(); }

    linkedImgs.forEach((img, i) => {
      img.style.cursor = 'zoom-in';
      img.addEventListener('click', () => open(i));
    });
    galleryButtons.forEach((btn, i) => {
      btn.addEventListener('click', () => open(linkedImgs.length + i));
    });

    document.getElementById('lightboxClose').addEventListener('click', close);
    document.getElementById('lightboxNext').addEventListener('click', next);
    document.getElementById('lightboxPrev').addEventListener('click', prev);
    lightbox.addEventListener('click', (e) => { if (e.target === lightbox) close(); });
    document.addEventListener('keydown', (e) => {
      if (!lightbox.classList.contains('open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowRight') next();
      if (e.key === 'ArrowLeft') prev();
    });
  })();

  // Note: the latte art scroll reveal (.latte-scene) needs no JS — it's driven by
  // native CSS scroll-driven animations (animation-timeline: view()), with a plain
  // CSS @supports fallback for browsers that don't implement it yet. See style.css.
