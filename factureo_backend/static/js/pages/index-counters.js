(function () {
    const ready = (fn) => document.readyState !== 'loading' ? fn() : document.addEventListener('DOMContentLoaded', fn);

    function easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
    }

    function formatNumber(value, decimals) {
        const factor = Math.pow(10, decimals);
        return (Math.round(value * factor) / factor).toFixed(decimals);
    }

    function startCount(el) {
        if (el.dataset.counterStarted === '1') return; // evitar doble inicio
        el.dataset.counterStarted = '1';

        const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        const start = parseFloat(el.getAttribute('data-counter-start') || '0');
        const end = parseFloat(el.getAttribute('data-counter-end') || '0');
        const duration = parseInt(el.getAttribute('data-counter-duration') || '1400', 10);
        const decimals = parseInt(el.getAttribute('data-counter-decimals') || '0', 10);
        const prefix = el.getAttribute('data-counter-prefix') || '';
        const suffix = el.getAttribute('data-counter-suffix') || '';

        const render = (v) => {
            const text = `${prefix}${formatNumber(v, decimals)}${suffix}`;
            el.textContent = text;
        };

        if (prefersReduced || duration <= 0 || isNaN(end)) {
            render(end);
            return;
        }

        const startTime = performance.now();

        function tick(now) {
            const elapsed = now - startTime;
            const t = Math.max(0, Math.min(1, elapsed / duration));
            const eased = easeOutCubic(t);
            const value = start + (end - start) * eased;
            render(value);
            if (t < 1) {
                requestAnimationFrame(tick);
            } else {
                // asegurar valor final exacto
                render(end);
            }
        }

        requestAnimationFrame(tick);
    }

    ready(() => {
        const counters = Array.from(document.querySelectorAll('.counter[data-counter-end]'));
        if (!counters.length) return;

        // Inicial: poner valor de inicio (para evitar parpadeo)
        counters.forEach(el => {
            const start = parseFloat(el.getAttribute('data-counter-start') || '0');
            const decimals = parseInt(el.getAttribute('data-counter-decimals') || '0', 10);
            const prefix = el.getAttribute('data-counter-prefix') || '';
            const suffix = el.getAttribute('data-counter-suffix') || '';
            el.textContent = `${prefix}${formatNumber(start, decimals)}${suffix}`;
        });

        // Estrategia 1: Sincronizar con reveal: observar la .card ancestro y arrancar cuando tenga 'in-view'
        counters.forEach(el => {
            const parentCard = el.closest('.card');
            if (!parentCard) return; // si no hay card, se usará IntersectionObserver como fallback

            if (parentCard.classList.contains('in-view')) {
                startCount(el);
                return;
            }

            const mo = new MutationObserver((mutations, observer) => {
                if (parentCard.classList.contains('in-view')) {
                    startCount(el);
                    observer.disconnect();
                }
            });
            mo.observe(parentCard, { attributes: true, attributeFilter: ['class'] });
        });

        // Estrategia 2 (fallback): cuando el propio contador entre al viewport
        const obs = new IntersectionObserver((entries, observer) => {
            for (const entry of entries) {
                if (entry.isIntersecting) {
                    const el = entry.target;
                    startCount(el);
                    observer.unobserve(el);
                }
            }
        }, { root: null, rootMargin: '0px 0px -10% 0px', threshold: 0.25 });

        counters.forEach(el => obs.observe(el));
    });
})();
