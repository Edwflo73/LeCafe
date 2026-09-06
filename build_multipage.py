import re, json, sys
sys.path.insert(0, '/tmp/lecafe_check')
from parse_menu import build_menu_jsonld

root = '/tmp/lecafe_check'
src = open(f'{root}/index.html.bak', encoding='utf-8').read()

def between(a, b, s=src):
    i = s.index(a)
    j = s.index(b, i)
    return s[i:j]

SVG_DEFS   = between('<svg width="0" height="0"', '<header id="siteHeader">')
SVG_DEFS   = SVG_DEFS.replace('style="position:absolute"', 'class="svg-defs-hidden"')
HEADER     = between('<header id="siteHeader">', '<div class="mobile-panel"')
MOBILE     = between('<div class="mobile-panel" id="mobilePanel">', '<main>')
HERO       = between('<section id="inicio" class="hero">', '<section id="menu" class="menu-section">')
MENU_SEC   = between('<section id="menu" class="menu-section">', '<section class="latte-scene"')
LATTE      = between('<section class="latte-scene"', '<section id="espacio">')
ESPACIO    = between('<section id="espacio">', '<section class="gallery-section">')
GALLERY    = between('<section class="gallery-section">', '<section class="origin-band">')
ORIGIN     = between('<section class="origin-band">', '<section id="visitanos"')
VISITANOS  = between('<section id="visitanos" class="visit">', '</main>')
FOOTER     = between('<footer>', '</footer>')
LIGHTBOX   = between('<div class="lightbox" id="lightbox">', '<script src="assets/js/main.js"')

# NOTE: `between(a, b)` returns `s[i:j]` where `i` is the index of the START of
# marker `a` — so the result ALREADY begins with `a` itself, and (since these
# blocks are siblings in the source, not nested) it already ends with that same
# block's own true closing tag, right before marker `b` begins. Manually
# re-prepending/re-appending the tags here was double-wrapping every block
# (e.g. "<section id=\"espacio\"><section id=\"espacio\">...</section></section>"),
# which silently doubled this site's `section{padding:130px 0}` rule at every
# one of these boundaries. Fixed: these blocks are already complete and
# correctly tagged as extracted — only trim trailing whitespace where needed.
MOBILE    = MOBILE.rstrip()
LIGHTBOX  = LIGHTBOX.rstrip()

# ---- shared nav (4 pages) ----
def nav(active):
    def cls(name):
        return ' class="active"' if name == active else ''
    return f'''<header id="siteHeader">
  <div class="wrap nav-inner">
    <a href="index.html" class="logo">
      <svg class="logo-img" viewBox="0 0 815 300.85" aria-hidden="false" role="img" aria-label="Le Café — Café de especialidad"><use href="#lecafe-logo-full"/></svg>
    </a>
    <nav class="primary-links">
      <a href="index.html"{cls('inicio')}>Inicio</a>
      <a href="menu.html"{cls('menu')}>Menú</a>
      <a href="nosotros.html"{cls('nosotros')}>Nosotros</a>
      <a href="ubicacion.html"{cls('ubicacion')}>Ubicación</a>
    </nav>
    <div class="nav-cta">
      <a href="ubicacion.html#reservar" class="btn btn-solid nav-cta-btn">Reservar</a>
      <button class="burger" id="burgerBtn" aria-label="Abrir menú"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>

<div class="mobile-panel" id="mobilePanel">
  <a href="index.html"{cls('inicio')}>Inicio</a>
  <a href="menu.html"{cls('menu')}>Menú</a>
  <a href="nosotros.html"{cls('nosotros')}>Nosotros</a>
  <a href="ubicacion.html"{cls('ubicacion')}>Ubicación</a>
  <a href="ubicacion.html#reservar" class="btn btn-solid mp-cta">Reservar mesa</a>
</div>'''

# ---- shared footer (4 pages) ----
FOOTER_SHARED = '''<footer>
  <div class="wrap">
    <div class="f-grid">
      <div class="f-col f-brand">
        <svg class="logo-img" viewBox="0 0 815 300.85" aria-hidden="false" role="img" aria-label="Le Café — Café de especialidad"><use href="#lecafe-logo-full"/></svg>
        <p class="f-tagline">Café de especialidad en un jardín de Boca del Río.</p>
      </div>
      <div class="f-col">
        <div class="f-heading">Explorar</div>
        <a href="index.html">Inicio</a>
        <a href="menu.html">Menú</a>
        <a href="nosotros.html">Nosotros</a>
        <a href="ubicacion.html">Ubicación</a>
      </div>
      <div class="f-col">
        <div class="f-heading">Visítanos</div>
        <a href="https://maps.app.goo.gl/ACNYhi43NhBxyR7bA" target="_blank" rel="noopener">Isauro Acosta 311, Boca del Río</a>
        <span class="f-static">Viernes a lunes · 6pm–11pm</span>
        <a href="tel:+522294334031">+52 229 433 4031</a>
      </div>
      <div class="f-col">
        <div class="f-heading">Síguenos</div>
        <a href="https://www.instagram.com/le_cafe_especialidad" target="_blank" rel="noopener">Instagram</a>
        <a href="https://wa.me/522294334031" target="_blank" rel="noopener">WhatsApp</a>
      </div>
    </div>
    <div class="f-bottom">
      <div class="f-copy-group">
        <div class="f-copy">Le Café © 2026 — Boca del Río, Veracruz</div>
        <div class="f-credit">
          <span class="f-credit-long">Diseño y desarrollo por <a href="https://edstudio.mx" target="_blank" rel="noopener">Ed Studio</a></span>
          <span class="f-credit-short">Sitio por <a href="https://edstudio.mx" target="_blank" rel="noopener">Ed Studio</a></span>
        </div>
      </div>
      <a href="privacidad.html" class="f-legal">Aviso de privacidad</a>
      <a href="#" class="f-top js-top">Volver arriba ↑</a>
    </div>
  </div>
</footer>'''

GEO_LAT = '19.1381161'
GEO_LNG = '-96.1238693'

GA_MEASUREMENT_ID = 'G-6ZZYTC47K1'
GSC_VERIFICATION = 'N-lbnRRbzmtrFEPTqTCxTFEpPr0qcYYvZm0_xP77fjc'

def page(title, description, canonical, active_nav, body_sections, extra_head='', robots='index, follow, max-image-preview:large'):
    return f'''<!--
  Lecafé · sitio web
  Diseño y desarrollo: Ed Studio · edstudio.mx
  2026
-->
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="author" content="Ed Studio — edstudio.mx">
<meta name="designer" content="Ed Studio">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canonical}">
<meta name="google-site-verification" content="{GSC_VERIFICATION}">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' https://www.googletagmanager.com; style-src 'self' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; frame-src https://www.google.com; connect-src 'self' https://www.google-analytics.com https://*.google-analytics.com https://*.analytics.google.com https://www.googletagmanager.com; object-src 'none'; base-uri 'self'; form-action 'self' https://wa.me; upgrade-insecure-requests">

<!-- Geo / NAP (Boca del Río, Veracruz) -->
<meta name="geo.region" content="MX-VER">
<meta name="geo.placename" content="Boca del Río, Veracruz">
<meta name="geo.position" content="{GEO_LAT};{GEO_LNG}">
<meta name="ICBM" content="{GEO_LAT}, {GEO_LNG}">

<!-- Open Graph / redes sociales -->
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="https://lecafe.mx/assets/images/hero.webp">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_MX">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="Le Café">

<!-- Twitter / X Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="https://lecafe.mx/assets/images/hero.webp">

<!-- Favicon (isotipo de marca real) -->
<link rel="icon" type="image/svg+xml" href="favicon.svg">

<!-- Preconexión y precarga de recursos críticos (mejora el tiempo de carga percibido) -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Nunito:ital,wght@0,400;0,500;0,600;0,700;0,800;0,900;1,600;1,700;1,800&display=swap" rel="stylesheet">
<link rel="preload" href="assets/fonts/LostaMasta-Bold.woff2" as="font" type="font/woff2" crossorigin>

<link rel="stylesheet" href="assets/css/style.css">

<!-- Google tag (gtag.js) — init lives in assets/js/ga.js (external file, not
     inline) because the site's CSP has no 'unsafe-inline' for script-src. -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
<script src="assets/js/ga.js"></script>

{extra_head}
</head>
<body>

{SVG_DEFS}
{nav(active_nav)}

<main>

{body_sections}

</main>

{FOOTER_SHARED}

{LIGHTBOX}

<script src="assets/js/main.js" defer></script>

</body>
</html>
'''

BASE_URL = 'https://lecafe.mx/'

# ---------------------------------------------------------------
# Shared structured data (schema.org)
# ---------------------------------------------------------------
BUSINESS_ID = BASE_URL + '#business'

BUSINESS = {
    "@type": "CafeOrCoffeeShop",
    "@id": BUSINESS_ID,
    "name": "Le Café",
    "image": BASE_URL + "assets/images/hero.webp",
    "url": BASE_URL,
    "telephone": "+522294334031",
    "servesCuisine": "Café de especialidad",
    "priceRange": "$$",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "Isauro Acosta 311",
        "addressLocality": "Boca del Río",
        "addressRegion": "Veracruz",
        "postalCode": "94297",
        "addressCountry": "MX"
    },
    "geo": {
        "@type": "GeoCoordinates",
        "latitude": GEO_LAT,
        "longitude": GEO_LNG
    },
    "hasMap": "https://maps.app.goo.gl/ACNYhi43NhBxyR7bA",
    "openingHoursSpecification": [
        {
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Friday", "Saturday", "Sunday", "Monday"],
            "opens": "18:00",
            "closes": "23:00"
        }
    ],
    "amenityFeature": [
        {"@type": "LocationFeatureSpecification", "name": "Jardín / patio al aire libre", "value": True},
        {"@type": "LocationFeatureSpecification", "name": "Wifi", "value": True},
        {"@type": "LocationFeatureSpecification", "name": "Juegos de mesa", "value": True},
        {"@type": "LocationFeatureSpecification", "name": "Barra y molino a la vista", "value": True}
    ],
    "hasMenu": BASE_URL + "menu.html",
    "sameAs": [
        "https://www.instagram.com/le_cafe_especialidad"
    ]
}

def breadcrumb(*crumbs):
    """crumbs: list of (name, url) tuples, in order, ending at the current page."""
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": url}
            for i, (name, url) in enumerate(crumbs)
        ]
    }

def page_intro_bar(eyebrow_text, crumb_label):
    """Slim intro strip for secondary pages: eyebrow + breadcrumb only.
    Replaces a full duplicate H1 hero — the real heading lives in the
    content section right below (promoted to <h1> there) so the page
    doesn't say the same thing twice before the user has scrolled at all."""
    return f'''  <section class="page-intro-bar">
    <div class="wrap reveal">
      <p class="eyebrow"><svg class="mark" viewBox="0 0 325.51 391.4" aria-hidden="true"><use href="#lecafe-mark"/></svg> {eyebrow_text}</p>
      <p class="crumb"><a href="index.html">Inicio</a> / {crumb_label}</p>
    </div>
  </section>'''

def ld_graph(*entities):
    graph = {"@context": "https://schema.org", "@graph": list(entities)}
    return f'''
<!-- Datos estructurados (schema.org) -->
<script type="application/ld+json">
{json.dumps(graph, ensure_ascii=False, indent=2)}
</script>'''

# ---------------------------------------------------------------
# INDEX (Inicio — vitrina)
# ---------------------------------------------------------------
espacio_teaser = '''  <section class="home-teasers" id="descubre">
    <div class="wrap reveal">
      <div class="teaser-grid">
        <div class="teaser-card">
          <div class="teaser-photo">
            <img src="assets/images/espacio.webp" alt="Patio de Le Café con mesas, plantas y luces cálidas al atardecer" width="1400" height="1680" loading="lazy">
          </div>
          <p class="eyebrow"><svg class="mark" viewBox="0 0 325.51 391.4" aria-hidden="true"><use href="#lecafe-mark"/></svg> El espacio</p>
          <h3>Un patio pensado para quedarse.</h3>
          <p>Mesas al aire libre, vegetación real y una atmósfera relajada — un rincón de Boca del Río construido para bajar el ritmo.</p>
          <a href="nosotros.html#espacio" class="btn btn-outline">Conoce el espacio →</a>
        </div>
        <div class="teaser-card">
          <div class="teaser-photo">
            <img src="assets/images/gallery-2-granos.webp" alt="Café recién tostado, listo para moler" width="1000" height="1250" loading="lazy">
          </div>
          <p class="eyebrow"><svg class="mark" viewBox="0 0 325.51 391.4" aria-hidden="true"><use href="#lecafe-mark"/></svg> Café en grano</p>
          <h3>Tueste propio, origen único.</h3>
          <p>El mismo café que te estás tomando ahora, tostado por nosotros. Disponible en grano o molido, para llevar a casa.</p>
          <a href="nosotros.html#origen" class="btn btn-outline">Ver cafés de origen →</a>
        </div>
      </div>
    </div>
  </section>'''

menu_cta = '''  <section class="menu-cta-band">
    <div class="wrap reveal">
      <p class="eyebrow on-dark"><svg class="mark" viewBox="0 0 325.51 391.4" aria-hidden="true"><use href="#lecafe-mark"/></svg> Nuestro menú</p>
      <h2>Especialidades, frappés,<br>alimentos y más.</h2>
      <p>Cinco secciones pensadas para cada momento del día — desde un espresso rápido hasta una tarde entera en el patio.</p>
      <a href="menu.html" class="btn btn-solid">Ver el menú completo →</a>
    </div>
  </section>'''

HERO_FIXED = HERO.replace(
    'href="#menu" class="btn btn-solid">Ver el menú<',
    'href="menu.html" class="btn btn-solid">Ver el menú<'
).replace(
    'href="#visitanos" class="link-plain">Cómo llegar',
    'href="ubicacion.html" class="link-plain">Cómo llegar'
)
assert HERO_FIXED != HERO, "hero CTA hrefs not found — check markup"

index_body = '\n\n'.join([HERO_FIXED, LATTE, espacio_teaser, menu_cta])

index_html = page(
    title='Le Café — Café de Especialidad en Boca del Río',
    description='Café de especialidad en un jardín de Boca del Río, Veracruz. Especialidades de la casa, frappés, café en grano y un patio pensado para quedarse. Viernes a lunes, 6pm–11pm.',
    canonical=BASE_URL,
    active_nav='inicio',
    body_sections=index_body,
    extra_head=ld_graph(
        {"@type": "WebSite", "@id": BASE_URL + "#website", "name": "Le Café", "url": BASE_URL, "inLanguage": "es-MX"},
        BUSINESS,
    )
)

# ---------------------------------------------------------------
# MENU
# ---------------------------------------------------------------
menu_hero = page_intro_bar('Nuestro menú', 'Menú')

MENU_SEC_H1 = MENU_SEC.replace(
    '<h2>Especialidades de la casa<br>y clásicos bien hechos.</h2>',
    '<h1>Especialidades de la casa<br>y clásicos bien hechos.</h1>'
)
assert MENU_SEC_H1 != MENU_SEC, "menu h2->h1 promotion failed — check markup"

# ARIA for the tab pattern: role="tablist"/"tab"/"tabpanel" so a screen reader
# knows these buttons switch panels, and which one is currently selected.
TAB_IDS = ['especialidades', 'frappe', 'alimentos', 'frias', 'calientes']

def add_tabs_aria(html):
    html = html.replace('<div class="tabs tabs-animate" id="tabsRow">', '<div class="tabs tabs-animate" id="tabsRow" role="tablist" aria-label="Categorías del menú">')
    for tid in TAB_IDS:
        html = re.sub(
            rf'<button class="tab-btn( active)?" data-tab="{tid}">([^<]+)</button>',
            lambda m, tid=tid: (
                f'<button class="tab-btn{m.group(1) or ""}" data-tab="{tid}" id="tab-{tid}" '
                f'role="tab" aria-selected="{"true" if m.group(1) else "false"}" '
                f'aria-controls="panel-{tid}">{m.group(2)}</button>'
            ),
            html
        )
        html = re.sub(
            rf'(<div class="menu-panel[^"]*" id="panel-{tid}")>',
            rf'\1 role="tabpanel" aria-labelledby="tab-{tid}">',
            html
        )
    return html

MENU_SEC_H1 = add_tabs_aria(MENU_SEC_H1)

menu_body = '\n\n'.join([menu_hero, MENU_SEC_H1])
menu_html = page(
    title='Menú — Le Café | Café de Especialidad en Boca del Río',
    description='Conoce el menú completo de Le Café: especialidades de la casa, frappés, alimentos, bebidas frías y calientes. Café de especialidad en Boca del Río, Veracruz.',
    canonical=BASE_URL + 'menu.html',
    active_nav='menu',
    body_sections=menu_body,
    extra_head=ld_graph(
        breadcrumb(("Inicio", BASE_URL), ("Menú", BASE_URL + "menu.html")),
        {**build_menu_jsonld(MENU_SEC), "@id": BASE_URL + "menu.html#menu"},
        {"@type": "CafeOrCoffeeShop", "@id": BUSINESS_ID, "hasMenu": BASE_URL + "menu.html#menu"},
    )
)

# ---------------------------------------------------------------
# NOSOTROS (Espacio + galería + café en grano)
# ---------------------------------------------------------------
nosotros_hero = page_intro_bar('Nosotros', 'Nosotros')

ESPACIO_H1 = ESPACIO.replace(
    '<h2>Un patio pensado<br>para quedarse.</h2>',
    '<h1>Un patio pensado<br>para quedarse.</h1>'
)
assert ESPACIO_H1 != ESPACIO, "espacio h2->h1 promotion failed — check markup"

games_band = '''  <section class="games-band">
    <div class="wrap reveal">
      <p class="eyebrow"><svg class="mark" viewBox="0 0 325.51 391.4" aria-hidden="true"><use href="#lecafe-mark"/></svg> Para compartir</p>
      <h2>Juegos de mesa para<br>quedarte un rato más.</h2>
      <p class="lead">Además de buen café y comida, en Le Café puedes compartir la mesa con juegos para pasarla sin prisa — ven con amigos, pareja o familia y convierte la visita en un plan para quedarse.</p>
      <div class="games-tags" aria-label="Juegos disponibles en Le Café">
        <span class="mi-tag">Lotería</span>
        <span class="mi-tag">UNO</span>
        <span class="mi-tag">Cartas</span>
        <span class="mi-tag">Retos y dinámicas</span>
      </div>
    </div>
  </section>'''

nosotros_body = '\n\n'.join([nosotros_hero, ESPACIO_H1, games_band, GALLERY, ORIGIN])
nosotros_html = page(
    title='Nosotros — Le Café | El espacio y el café en grano',
    description='Conoce el patio y el espacio de Le Café en Boca del Río, y nuestro café en grano de tueste propio: Valle de Soreq, Valle de Escol, Monte Ararat y El Paraíso.',
    canonical=BASE_URL + 'nosotros.html',
    active_nav='nosotros',
    body_sections=nosotros_body,
    extra_head=ld_graph(
        breadcrumb(("Inicio", BASE_URL), ("Nosotros", BASE_URL + "nosotros.html")),
        {"@type": "CafeOrCoffeeShop", "@id": BUSINESS_ID, "amenityFeature": BUSINESS["amenityFeature"]},
        {
            "@type": "ItemList",
            "name": "Café en grano — tueste propio",
            "itemListElement": [
                {
                    "@type": "Product", "position": 1, "name": "Valle de Soreq",
                    "description": "Coatepec, Veracruz · Tueste alto. Chocolate, cacao amargo moderado, caramelo y poca acidez.",
                    "offers": {"@type": "Offer", "price": "340", "priceCurrency": "MXN", "description": "1 kg · mayoreo desde 9 kg"}
                },
                {
                    "@type": "Product", "position": 2, "name": "Valle de Escol",
                    "description": "Ixhuacán de los Reyes, Veracruz · SCA 83.75. Azúcar moscada, chocolate con leche y naranja.",
                    "offers": {"@type": "Offer", "price": "220", "priceCurrency": "MXN", "description": "desde 250 g"}
                },
                {
                    "@type": "Product", "position": 3, "name": "Monte Ararat",
                    "description": "Guerrero · Typica y Bourbon. Chocolate, nuez y azúcar.",
                    "offers": {"@type": "Offer", "price": "199", "priceCurrency": "MXN", "description": "desde 250 g"}
                },
                {
                    "@type": "Product", "position": 4, "name": "El Paraíso",
                    "description": "Oaxaca · Typica, Bourbon, Caturra y Mundo Novo. Pasas, chocolate amargo, dulce de leche y nueces.",
                    "offers": {"@type": "Offer", "price": "199", "priceCurrency": "MXN", "description": "desde 250 g"}
                }
            ]
        },
    )
)

# ---------------------------------------------------------------
# UBICACION (mapa, horario, reservación)
# ---------------------------------------------------------------
ubicacion_hero = page_intro_bar('Ubicación y horario', 'Ubicación')

MAP_EMBED = '''<div class="map-embed">
          <iframe src="https://www.google.com/maps?q=Isauro+Acosta+311,+Boca+del+R%C3%ADo,+Veracruz,+94297&z=16&output=embed" width="100%" height="100%" loading="lazy" referrerpolicy="no-referrer-when-downgrade" title="Mapa — Le Café, Boca del Río"></iframe>
        </div>
        <a href="https://maps.app.goo.gl/ACNYhi43NhBxyR7bA" target="_blank" rel="noopener" class="map-open-link">Abrir en Google Maps →</a>'''

OLD_MAP_CARD = '''<a href="https://maps.app.goo.gl/ACNYhi43NhBxyR7bA" target="_blank" rel="noopener" class="map-card">
          <div class="map-placeholder">Mapa — Boca del Río</div>
          <svg class="map-pin" viewBox="0 0 24 32" aria-hidden="true">
            <path d="M12 0C5.4 0 0 5.4 0 12c0 9 12 20 12 20s12-11 12-20c0-6.6-5.4-12-12-12z" fill="#801D1F"/>
            <circle cx="12" cy="12" r="4.5" fill="#FFF7E3"/>
          </svg>
          <span class="map-cta">Abrir en Google Maps →</span>
        </a>'''

assert OLD_MAP_CARD in VISITANOS, "map-card markup not found — check source"

WHATSAPP_SHORTCUT = '''<button type="submit" class="btn btn-solid">Reservar por WhatsApp</button>
          <span class="res-shortcut">¿Prefieres escribir directo? <a href="https://wa.me/522294334031" target="_blank" rel="noopener">Mándanos un WhatsApp →</a></span>
        </form>'''
OLD_FORM_END = '''<button type="submit" class="btn btn-solid">Reservar por WhatsApp</button>
        </form>'''
assert OLD_FORM_END in VISITANOS, "reservation form end markup not found — check source"

VISITANOS_ID = (
    VISITANOS
    .replace(OLD_MAP_CARD, MAP_EMBED)
    .replace(OLD_FORM_END, WHATSAPP_SHORTCUT)
    .replace(
        '<section id="visitanos" class="visit">',
        '<section id="reservar" class="visit">'
    )
    .replace(
        '<h2>Te esperamos<br>en Le Café.</h2>',
        '<h1>Te esperamos<br>en Le Café.</h1>'
    )
)
assert '<h1>Te esperamos<br>en Le Café.</h1>' in VISITANOS_ID, "visitanos h2->h1 promotion failed"

faq_data = [
    ("¿Dónde está Le Café?",
     "Le Café está en Boca del Río, Veracruz, cerca de la zona de Veracruz. Estamos en Isauro Acosta 311, C.P. 94297, Boca del Río, México. Abrimos viernes a lunes, 6:00 p.m. a 11:00 p.m."),
    ("¿Le Café está en Veracruz o en Boca del Río?",
     "Estamos físicamente en Boca del Río, Veracruz, una zona muy cercana a la ciudad de Veracruz, por eso mucha gente nos identifica como un lugar de Veracruz."),
    ("¿Qué orígenes de café venden?",
     "Café mexicano de Coatepec (Valle de Soreq), Ixhuacán de los Reyes (Valle de Escol), Guerrero (Monte Ararat) y Oaxaca (El Paraíso) — disponible en grano o molido, en presentaciones de 250 g, 500 g y 1 kg."),
    ("¿Puedo comprar café en grano o molido para llevar a casa?",
     "Sí — vendemos nuestro café de tueste propio en grano o molido, en presentaciones de 250 g, 500 g y 1 kg, con orígenes de Coatepec, Ixhuacán de los Reyes, Guerrero y Oaxaca. Puedes pedirlo directamente por WhatsApp."),
    ("¿Puedo reservar o pedir para recoger?",
     "Sí — reserva por WhatsApp al +52 229 433 4031 o usa el formulario de reserva rápida en esta página. También puedes pedir para recoger en el local, o a domicilio por Rappi."),
    ("¿Le Café tiene servicio a domicilio?",
     "Sí — puedes pedir a domicilio a través de Rappi, o para recoger directamente en el local."),
    ("¿Hay jardín y juegos de mesa?",
     "Sí — contamos con un patio/jardín al aire libre y una selección de juegos de mesa (Lotería, UNO, cartas y más) para compartir mientras disfrutas tu bebida."),
    ("¿Le Café abre todos los días?",
     "No — abrimos viernes, sábado, domingo y lunes, de 6:00 p.m. a 11:00 p.m. Permanecemos cerrados martes, miércoles y jueves."),
    ("¿Cuánto cuesta un café en Le Café?",
     "Los precios van desde $20 por un espresso hasta $99 por bebidas de especialidad como el Big Le o los frappés — nos ubicamos en un rango de precio medio ($$) dentro de las cafeterías de especialidad de la zona."),
    ("¿El carajillo de Le Café tiene alcohol?",
     "No — nuestro Carajillo es una versión sin alcohol, preparada con o sin leche y perfumada con romero fresco de nuestro jardín."),
    ("¿Le Café solo vende bebidas o también hay alimentos?",
     "También tenemos alimentos — hamburguesas, sandwich de atún, quesadillas y pan y postres — además de nuestras bebidas de especialidad."),
    ("¿Cuál es el WhatsApp de Le Café?",
     "Puedes escribirnos al +52 229 433 4031 para reservar mesa, pedir para recoger o resolver cualquier duda."),
]

faq_items_html = '\n'.join(
    f'''      <details class="faq-item">
        <summary>{q}</summary>
        <p>{a}</p>
      </details>''' for q, a in faq_data
)

faq_section = f'''  <section class="faq">
    <div class="wrap reveal">
      <p class="eyebrow"><svg class="mark" viewBox="0 0 325.51 391.4" aria-hidden="true"><use href="#lecafe-mark"/></svg> Preguntas frecuentes</p>
      <h2>Preguntas rápidas,<br>respuesta directa.</h2>
      <div class="faq-list">
{faq_items_html}
      </div>
    </div>
  </section>'''

FAQ_JSONLD = {
    "@type": "FAQPage",
    "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for q, a in faq_data
    ]
}

ubicacion_body = '\n\n'.join([ubicacion_hero, VISITANOS_ID, faq_section])
ubicacion_html = page(
    title='Ubicación y Reservaciones — Le Café | Boca del Río, Veracruz',
    description='Visita Le Café en Isauro Acosta 311, Boca del Río, Veracruz. Horario, mapa y reservaciones rápidas por WhatsApp. Viernes a lunes, 6pm–11pm.',
    canonical=BASE_URL + 'ubicacion.html',
    active_nav='ubicacion',
    body_sections=ubicacion_body,
    extra_head=ld_graph(
        breadcrumb(("Inicio", BASE_URL), ("Ubicación", BASE_URL + "ubicacion.html")),
        BUSINESS,
        FAQ_JSONLD,
    )
)

# ---------------------------------------------------------------
# PRIVACIDAD (Aviso de Privacidad)
# ---------------------------------------------------------------
# Independiente del index.html.bak (no forma parte del sitio de una sola
# página) pero SÍ comparte plantilla page() con las otras 4 — mismo nav,
# footer y CSP, generado aquí para que nunca vuelva a desincronizarse.
privacidad_hero = page_intro_bar('Aviso de privacidad', 'Aviso de privacidad')

privacidad_content = '''  <section class="legal-page">
    <div class="wrap">
      <div class="legal-content">
        <h1>Aviso de Privacidad</h1>
        <p class="legal-updated">Última actualización: 4 de septiembre de 2026</p>

        <p>En Le Café respetamos tu privacidad. Este aviso explica, de forma clara y sencilla, qué información se recopila a través de este sitio web y qué hacemos con ella.</p>

        <h2>¿Qué datos recopilamos?</h2>
        <p>Únicamente a través del formulario de reservación rápida en la sección de <a href="ubicacion.html#reservar" class="legal-link">Ubicación</a>, donde puedes ingresar de forma voluntaria:</p>
        <ul>
          <li>Nombre</li>
          <li>Fecha y hora deseada</li>
          <li>Número de personas</li>
          <li>Comentarios adicionales (opcional)</li>
        </ul>
        <p>No usamos cuentas de usuario ni recopilamos ningún otro dato personal a través del sitio.</p>

        <h2>¿Cómo se usan estos datos?</h2>
        <p>Este sitio no tiene servidor propio ni base de datos: es un sitio estático. Cuando llenas el formulario, tu navegador arma automáticamente un mensaje de WhatsApp con esa información y lo envía directamente a nuestro número de contacto — lo recibimos como cualquier mensaje normal de WhatsApp, únicamente para coordinar tu reservación.</p>
        <p>No almacenamos, vendemos ni compartimos estos datos con terceros. No existe una base de datos de clientes derivada de este formulario.</p>

        <h2>Google Analytics</h2>
        <p>Usamos Google Analytics para entender, de forma agregada, cómo se usa este sitio (por ejemplo, qué páginas se visitan más). Google puede usar cookies para esto. Si prefieres no ser medido, puedes usar el bloqueador de cookies de tu navegador o una extensión de exclusión de Google Analytics.</p>

        <h2>Tus derechos (ARCO)</h2>
        <p>De acuerdo con la Ley Federal de Protección de Datos Personales en Posesión de los Particulares, tienes derecho a acceder, rectificar, cancelar u oponerte al uso de tus datos personales (derechos ARCO). Dado que la única información que recibimos llega directamente a nuestro WhatsApp, puedes ejercer estos derechos simplemente escribiéndonos y pidiendo que eliminemos la conversación.</p>

        <h2>Contacto</h2>
        <p>Si tienes dudas sobre este aviso, puedes escribirnos por <a href="https://wa.me/522294334031" target="_blank" rel="noopener" class="legal-link">WhatsApp</a> o por <a href="https://www.instagram.com/le_cafe_especialidad" target="_blank" rel="noopener" class="legal-link">Instagram</a>.</p>

        <div class="legal-note">
          Este aviso fue redactado como un borrador de buena fe para reflejar honestamente cómo funciona este sitio (sin servidor, sin base de datos). No sustituye asesoría legal — si Le Café lo requiere, se recomienda que un abogado especializado en protección de datos lo revise y valide antes de considerarlo definitivo.
        </div>
      </div>
    </div>
  </section>'''

privacidad_body = '\n\n'.join([privacidad_hero, privacidad_content])
privacidad_html = page(
    title='Aviso de Privacidad — Le Café',
    description='Aviso de privacidad de Le Café: qué datos se recopilan a través del formulario de reservación por WhatsApp, cómo se usan y tus derechos ARCO.',
    canonical=BASE_URL + 'privacidad.html',
    active_nav='privacidad',
    body_sections=privacidad_body,
    robots='noindex, follow',
)

for fname, content in [
    ('index.html', index_html),
    ('menu.html', menu_html),
    ('nosotros.html', nosotros_html),
    ('ubicacion.html', ubicacion_html),
    ('privacidad.html', privacidad_html),
]:
    with open(f'{root}/{fname}', 'w', encoding='utf-8') as f:
        f.write(content)
    print(fname, len(content))
