# Changelog

## v0.2.0 (2025-10-27)

Perfil de usuario, mejoras en dashboard y navegación, módulo de noticias y páginas legales.

### Nuevo
- Perfil de usuario (`/perfil`):
	- Edición de nombre, usuario, correo, empresa y tema (claro/oscuro).
	- Cambio de contraseña con verificación de la actual y confirmación.
	- Subida de avatar (png/jpg/jpeg/gif/webp) con guardado en `static/img/avatars`.
- Noticias: módulo con listado, detalle y formulario; soporte de `image_url` en alta/edición; plantillas con imagen opcional.
- Páginas legales: Términos y condiciones y Política de privacidad (blueprint de páginas estáticas).
- Contacto: plantilla y JS para el formulario.

### Cambios
- Dashboard: encabezado centrado (“Panel principal de control”) y tarjeta de perfil arriba a la derecha; eliminación del saludo duplicado.
- Tarjetas de módulos con métricas visibles (productos/clientes/ventas) y hover sutil.
- Navegación: burbuja flotante y menú central visibles solo en la página de inicio; ocultos en dashboard y módulos internos.
- CSS: nueva utilidad `avatar-64` y ajustes menores en componentes.

### Notas
- No se requieren migraciones. Los campos nuevos del usuario (`company`, `avatar_url`, `theme`) se añaden progresivamente al editar el perfil o en registros nuevos.
- Si no ves cambios de estilo, refresca con limpieza de caché del navegador.

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
