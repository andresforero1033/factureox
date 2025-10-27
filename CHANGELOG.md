# Changelog

## v0.1.0 (2025-10-27)

Primera iteración de la interfaz con navegación flotante y microinteracciones.

### Nuevo
- Navbar flotante en desktop: logo a la izquierda (sin fondo), menú central tipo pill y acciones (login/registro o dashboard/salir) en burbuja a la derecha con iconos.
- Móvil: logo centrado arriba; burbuja de autenticación vertical fija en el borde derecho; menú central oculto (se usa barra inferior de secciones).
- Menú flotante de secciones: lateral en desktop y barra inferior en móvil. Incluye scroll suave y resaltado automático de la sección activa.
- Transiciones on scroll (reveal on scroll) con IntersectionObserver, variantes (fade, fade-up, left/right, zoom-in) y stagger en secciones de cards.
- Favicon SVG agregado y referenciado en la plantilla base.

### Cambios
- Padding lateral progresivo para `.hero-full` y `.section-full` (mobile, tablet, desktop, XL) para dar mejor respiración.
- Modularización de estilos (base/layout/components/pages) y limpieza de compatibilidad (evitando `color-mix` sin fallback, respetando `prefers-reduced-motion`).

### Notas
- Si se desea, se puede añadir un `apple-touch-icon` (180x180 PNG) para iOS y un `manifest.json` para PWA en entregas futuras.
