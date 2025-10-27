(function(){
  const ready = (fn) => document.readyState !== 'loading' ? fn() : document.addEventListener('DOMContentLoaded', fn);

  function applyTheme(mode, withTransition = false) {
    const html = document.documentElement;
    const body = document.body;

    if (withTransition) {
      html.classList.add('theme-transition');
      window.setTimeout(() => html.classList.remove('theme-transition'), 180);
    }

    html.setAttribute('data-bs-theme', mode);
    body.setAttribute('data-bs-theme', mode);

    if (mode === 'light') {
      html.setAttribute('data-theme', 'light');
      body.setAttribute('data-theme', 'light');
    } else {
      html.removeAttribute('data-theme');
      body.removeAttribute('data-theme');
    }

    // Actualizar iconos
    const toggle = document.getElementById('themeToggle');
    if (toggle) {
      const sun = toggle.querySelector('[data-icon="sun"]');
      const moon = toggle.querySelector('[data-icon="moon"]');
      if (sun && moon) {
        if (mode === 'light') {
          sun.hidden = false; moon.hidden = true;
        } else {
          sun.hidden = true; moon.hidden = false;
        }
      }
      toggle.setAttribute('aria-pressed', mode === 'light' ? 'true' : 'false');
      toggle.setAttribute('title', mode === 'light' ? 'Cambiar a oscuro' : 'Cambiar a claro');
      toggle.setAttribute('aria-label', mode === 'light' ? 'Cambiar a oscuro' : 'Cambiar a claro');
    }
  }

  ready(() => {
    const prefersLight = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)');
    let stored = null;
    try { stored = localStorage.getItem('theme'); } catch (e) {}

    let current = stored || (prefersLight && prefersLight.matches ? 'light' : 'dark');
    applyTheme(current, false);

    const toggle = document.getElementById('themeToggle');
    if (toggle) {
      toggle.addEventListener('click', () => {
        current = current === 'light' ? 'dark' : 'light';
        try { localStorage.setItem('theme', current); } catch (e) {}
        applyTheme(current, true);
      });
    }

    if (prefersLight && prefersLight.addEventListener) {
      // Si no hay preferencia guardada, seguir el sistema en vivo
      prefersLight.addEventListener('change', (e) => {
        let storedNow = null;
        try { storedNow = localStorage.getItem('theme'); } catch (e) {}
        if (!storedNow) {
          current = e.matches ? 'light' : 'dark';
          applyTheme(current, true);
        }
      });
    }
  });
})();
