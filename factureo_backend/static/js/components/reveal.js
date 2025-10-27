(function () {
    const ready = (fn) => document.readyState !== 'loading' ? fn() : document.addEventListener('DOMContentLoaded', fn);
    ready(() => {
        const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        const all = Array.from(document.querySelectorAll('[data-reveal]'));
        if (!all.length) return;

        // Inicialización: marcar estado inicial
        all.forEach(el => {
            el.classList.add('reveal-init');
            const delay = el.getAttribute('data-reveal-delay');
            const duration = el.getAttribute('data-reveal-duration');
            if (delay) el.style.transitionDelay = `${parseInt(delay, 10)}ms`;
            if (duration) el.style.transitionDuration = `${parseInt(duration, 10)}ms`;
        });

        // Observer
        const obs = new IntersectionObserver((entries) => {
            for (const entry of entries) {
                if (entry.isIntersecting) {
                    const el = entry.target;
                    el.classList.add('in-view');
                    el.classList.remove('reveal-init');
                    obs.unobserve(el);

                    // Manejo de stagger en hijos si aplica
                    const stagger = parseInt(el.getAttribute('data-reveal-stagger') || '0', 10);
                    if (stagger > 0) {
                        const childEffect = el.getAttribute('data-reveal-children') || 'fade-up';
                        const children = el.querySelectorAll('[data-reveal-child], .card');
                        let i = 0;
                        children.forEach(ch => {
                            if (!ch.hasAttribute('data-reveal')) ch.setAttribute('data-reveal', childEffect);
                            ch.classList.add('reveal-init');
                            ch.style.transitionDelay = `${i * stagger}ms`;
                            // Observar cada hijo para revelar con su propio umbral mínimo
                            childObs.observe(ch);
                            i++;
                        });
                    }
                }
            }
        }, { root: null, rootMargin: '0px 0px -10% 0px', threshold: 0.15 });

        const childObs = new IntersectionObserver((entries) => {
            for (const entry of entries) {
                if (entry.isIntersecting) {
                    const el = entry.target;
                    el.classList.add('in-view');
                    el.classList.remove('reveal-init');
                    childObs.unobserve(el);
                }
            }
        }, { root: null, rootMargin: '0px 0px -10% 0px', threshold: 0.05 });

        // Activar observer principal
        all.forEach(el => obs.observe(el));

        // Reduce motion
        if (prefersReduced) {
            all.forEach(el => {
                el.classList.add('in-view');
                el.classList.remove('reveal-init');
            });
            obs.disconnect();
            childObs.disconnect();
        }
    });
})();
