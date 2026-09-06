from playwright.sync_api import sync_playwright
import re

BASE = 'http://localhost:8799/'
pages = ['index.html', 'menu.html', 'nosotros.html', 'ubicacion.html', 'privacidad.html']

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
    all_ok = True

    for name in pages:
        pg = browser.new_page(viewport={'width':1280,'height':900})
        failed_requests = []
        console_errors = []
        page_errors = []
        pg.on('requestfailed', lambda req: failed_requests.append((req.url, req.failure)))
        pg.on('console', lambda msg: console_errors.append(msg.text) if msg.type == 'error' and 'net::ERR' not in msg.text else None)
        pg.on('pageerror', lambda exc: page_errors.append(str(exc)))

        responses = {}
        def on_response(resp):
            responses[resp.url] = resp.status
        pg.on('response', on_response)

        pg.goto(BASE + name, wait_until='networkidle')

        # check all local resource responses for non-200 (excluding external fonts which fail in sandbox)
        bad = [(u,s) for u,s in responses.items() if s >= 400 and 'fonts.g' not in u]
        # check internal hrefs to other local pages / assets
        hrefs = pg.eval_on_selector_all('a[href]', 'els => els.map(e => e.getAttribute("href"))')
        local_html_links = sorted(set(h for h in hrefs if h and h.endswith('.html') and not h.startswith('http')))

        print(f"=== {name} ===")
        print("  local .html links found:", local_html_links)
        print("  bad resource responses:", bad)
        print("  failed requests (non-font):", [f for f in failed_requests if 'fonts.g' not in f[0]])
        print("  console errors:", console_errors)
        print("  page errors:", page_errors)

        if bad or page_errors or console_errors:
            all_ok = False

        pg.close()

    # functional checks
    pg = browser.new_page(viewport={'width':1280,'height':900})
    pg.goto(BASE + 'menu.html', wait_until='networkidle')
    pg.click('.tab-btn[data-tab="frappe"]')
    active_panel = pg.eval_on_selector('.menu-panel.active', 'el => el.id')
    print("menu.html tab click -> active panel:", active_panel)
    if active_panel != 'panel-frappe':
        all_ok = False
    pg.close()

    pg = browser.new_page(viewport={'width':1280,'height':900})
    pg.goto(BASE + 'nosotros.html', wait_until='networkidle')
    pg.click('.gallery-item >> nth=0')
    pg.wait_for_timeout(200)
    lb_open = pg.eval_on_selector('#lightbox', 'el => el.classList.contains("open")')
    print("nosotros.html lightbox opens on click:", lb_open)
    if not lb_open:
        all_ok = False
    pg.close()

    pg = browser.new_page(viewport={'width':1280,'height':900})
    opened_urls = []
    def on_popup(popup):
        opened_urls.append(popup.url)
    pg.on('popup', on_popup)
    pg.goto(BASE + 'ubicacion.html', wait_until='networkidle')
    pg.fill('#f-name', 'Prueba QA')
    pg.click('button[type="submit"]')
    pg.wait_for_timeout(300)
    print("ubicacion.html reservation form opened popup:", opened_urls)
    if not opened_urls or 'wa.me' not in opened_urls[0]:
        all_ok = False
    pg.close()

    pg = browser.new_page(viewport={'width':1280,'height':900})
    pg.goto(BASE + 'index.html', wait_until='networkidle')
    pg.click('a.f-legal')
    pg.wait_for_load_state('networkidle')
    on_privacidad = pg.url.endswith('privacidad.html')
    h1_text = pg.eval_on_selector('.legal-content h1', 'el => el.textContent') if on_privacidad else None
    print("footer 'Aviso de privacidad' link -> url:", pg.url, "| h1:", h1_text)
    if not on_privacidad or h1_text != 'Aviso de Privacidad':
        all_ok = False
    pg.close()

    browser.close()
    print("\nALL_OK =", all_ok)
