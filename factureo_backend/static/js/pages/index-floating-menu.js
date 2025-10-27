(function(){
  const ready = (fn) =>
    document.readyState !== 'loading' ? fn() : document.addEventListener('DOMContentLoaded', fn);

  ready(() => {
    const links = Array.from(document.querySelectorAll('.floating-menu .fm-link'));
    if (!links.length) return;

    const bySection = new Map(links.map(a => [a.dataset.section, a]));
    const sections = Array.from(bySection.keys())
      .map(id => document.getElementById(id))
      .filter(Boolean);
    const menu = document.getElementById('floatingMenu');
    const fab = document.querySelector('.floating-fab');
    const mdUp = window.matchMedia('(min-width: 768px)');

    // Smooth scrolling on click
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    links.forEach(a => {
      a.addEventListener('click', (e) => {
        const targetId = a.getAttribute('href')?.slice(1);
        if (!targetId) return;
        const targetEl = document.getElementById(targetId);
        if (!targetEl) return;
        e.preventDefault();
        if (!prefersReduced && 'scrollIntoView' in targetEl) {
          targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
          const y = targetEl.getBoundingClientRect().top + window.pageYOffset;
          window.scrollTo(0, y);
        }
        history.replaceState(null, '', '#' + targetId);
        // Close on mobile after navigating
        if (fab && !mdUp.matches) {
          closeMobileMenu();
        }
      });
    });

    // Active section highlighting via IntersectionObserver
    const statusEl = document.getElementById('fm-status');
    const setActive = (id) => {
      links.forEach(l => {
        const active = l.dataset.section === id;
        l.classList.toggle('active', active);
        l.setAttribute('aria-current', active ? 'true' : 'false');
      });
      if (statusEl) {
        const activeLink = bySection.get(id);
        if (activeLink) statusEl.textContent = `Sección activa: ${activeLink.title || id}`;
      }
    };

    // Include top sentinel for "inicio" if section exists
    const observerOptions = { root: null, rootMargin: '0px 0px -60% 0px', threshold: [0, 0.25, 0.5, 1] };
    const obs = new IntersectionObserver((entries) => {
      // Find the most visible section
      let best = { id: null, ratio: 0 };
      for (const entry of entries) {
        if (entry.isIntersecting && entry.intersectionRatio >= best.ratio) {
          best = { id: entry.target.id, ratio: entry.intersectionRatio };
        }
      }
      if (best.id) setActive(best.id);
    }, observerOptions);

    sections.forEach(sec => obs.observe(sec));

    // Initialize active based on current hash or first section
    const initial = (location.hash || '#inicio').slice(1);
    if (bySection.has(initial)) setActive(initial);

    // Mobile FAB toggle
    const openMobileMenu = () => {
      if (!menu) return;
      menu.classList.remove('d-none');
      menu.classList.add('d-flex');
      menu.setAttribute('aria-hidden', 'false');
      if (fab) {
        fab.setAttribute('aria-expanded', 'true');
        fab.innerHTML = '<i class="bi bi-x-lg" aria-hidden="true"></i><span class="visually-hidden">Cerrar menú</span>';
      }
    };
    const closeMobileMenu = () => {
      if (!menu) return;
      // Mantener comportamiento responsive: en desktop el menú ya es visible por d-md-flex
      if (!mdUp.matches) {
        menu.classList.add('d-none');
        menu.classList.remove('d-flex');
        menu.setAttribute('aria-hidden', 'true');
      }
      if (fab) {
        fab.setAttribute('aria-expanded', 'false');
        fab.innerHTML = '<i class="bi bi-plus-lg" aria-hidden="true"></i><span class="visually-hidden">Menú de secciones</span>';
      }
    };

    if (fab && menu) {
      fab.addEventListener('click', (e) => {
        e.stopPropagation();
        const expanded = fab.getAttribute('aria-expanded') === 'true';
        if (expanded) closeMobileMenu(); else openMobileMenu();
      });
      // Cerrar al hacer click fuera
      document.addEventListener('click', (e) => {
        if (!menu.classList.contains('d-none') && !menu.contains(e.target) && e.target !== fab) {
          closeMobileMenu();
        }
      });
      // Sincronizar en resize: si pasamos a desktop, aseguramos visible; si bajamos a mobile, cerramos
      mdUp.addEventListener('change', (ev) => {
        if (ev.matches) {
          // desktop
          menu.classList.remove('d-none');
          menu.classList.add('d-md-flex');
          menu.setAttribute('aria-hidden', 'false');
          if (fab) fab.setAttribute('aria-expanded', 'false');
        } else {
          // mobile
          closeMobileMenu();
        }
      });
    }
  });
})();
