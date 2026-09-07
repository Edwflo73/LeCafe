// Convierte el <link rel="preload" as="style"> de Google Fonts en un
// stylesheet activo una vez cargado, sin bloquear el render inicial.
// Externo (no inline) porque el CSP del sitio no permite 'unsafe-inline'
// en script-src.
(function () {
  var link = document.getElementById('gfontsPreload');
  if (!link) return;
  link.addEventListener('load', function () {
    link.rel = 'stylesheet';
  });
  // Fallback por si el evento "load" ya se disparó antes de que corriera este script.
  if (link.sheet) link.rel = 'stylesheet';
})();
