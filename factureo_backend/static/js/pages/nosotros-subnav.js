(function(){
  const onReady = () => {
    const subnav = document.querySelector('#nosotros .nosotros-subnav');
    if (!subnav) return;
    const links = Array.from(subnav.querySelectorAll('a.nav-link'));
    const sections = links
      .map(a => document.querySelector(a.getAttribute('href')))
      .filter(Boolean);

    const getOffset = () => {
      const nav = document.querySelector('.navbar');
      const base = nav ? nav.getBoundingClientRect().height : 72;
      return Math.max(64, Math.min(120, Math.round(base + 8)));
    };

    // Smooth scroll
    links.forEach(a => {
      a.addEventListener('click', (e) => {
        const href = a.getAttribute('href');
        if (!href || !href.startsWith('#')) return;
        const target = document.querySelector(href);
        if (!target) return;
        e.preventDefault();
        const top = target.getBoundingClientRect().top + window.pageYOffset - getOffset();
        window.scrollTo({ top, behavior: 'smooth' });
      });
    });

    // Active link via IntersectionObserver
    const byId = new Map(sections.map(s => [s.id, s]));
    const setActive = (id) => {
      links.forEach(a => a.classList.toggle('active', a.getAttribute('href') === `#${id}`));
      // ensure visibility within subnav scroll
      const active = subnav.querySelector('a.nav-link.active');
      if (active && typeof active.scrollIntoView === 'function') {
        active.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
      }
    };

    let lastActive = null;
    const io = new IntersectionObserver((entries) => {
      // pick the most visible entry
      let best = null; let ratio = 0;
      for (const en of entries) {
        if (en.isIntersecting && en.intersectionRatio > ratio) { best = en; ratio = en.intersectionRatio; }
      }
      const id = best ? best.target.id : null;
      if (id && id !== lastActive) {
        lastActive = id;
        setActive(id);
      }
    }, { root: null, threshold: [0.25, 0.5, 0.75], rootMargin: `-${getOffset()}px 0px -40% 0px` });

    sections.forEach(s => io.observe(s));
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', onReady);
  } else {
    onReady();
  }
})();
