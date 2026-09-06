from playwright.sync_api import sync_playwright
import json

pages = ['index.html', 'menu.html', 'nosotros.html', 'ubicacion.html']

with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
    for name in pages:
        pg = b.new_page(viewport={'width':1280,'height':900})
        pg.goto(f'http://localhost:8799/{name}', wait_until='networkidle')
        pg.evaluate("document.documentElement.style.scrollBehavior='auto'")
        height = pg.evaluate("document.body.scrollHeight")
        y = 0
        while y < height:
            pg.evaluate(f"window.scrollTo(0,{y})")
            pg.wait_for_timeout(100)
            y += 400
        pg.evaluate("window.scrollTo(0,0)")
        pg.wait_for_timeout(200)

        data = pg.evaluate("""
        () => {
          const main = document.querySelector('main') || document.body;
          const kids = Array.from(document.body.querySelectorAll('body > *, main > *'));
          // Get all top-level visible block elements (header, main's direct sections, footer)
          const nodes = Array.from(document.querySelectorAll('body > header, body > div.mobile-panel, main > section, body > footer, .page-intro-bar'));
          const results = [];
          let prevBottom = null;
          nodes.forEach(el => {
            const r = el.getBoundingClientRect();
            const cs = getComputedStyle(el);
            const tag = el.tagName.toLowerCase() + (el.id ? '#'+el.id : '') + (el.className ? '.'+el.className.split(' ').join('.') : '');
            results.push({
              tag,
              top: Math.round(r.top + window.scrollY),
              bottom: Math.round(r.bottom + window.scrollY),
              paddingTop: cs.paddingTop,
              paddingBottom: cs.paddingBottom,
              marginTop: cs.marginTop,
              marginBottom: cs.marginBottom,
              gapFromPrev: prevBottom !== null ? Math.round((r.top + window.scrollY) - prevBottom) : null
            });
            prevBottom = r.bottom + window.scrollY;
          });
          return results;
        }
        """)
        print(f"=== {name} ===")
        for d in data:
            gap = d['gapFromPrev']
            flag = "  <<< LARGE GAP" if gap is not None and gap > 150 else ""
            print(f"  {d['tag']:60s} pad-top={d['paddingTop']:>8s} pad-bot={d['paddingBottom']:>8s} gapFromPrev={str(gap):>6s}{flag}")
        pg.close()
    b.close()
    print("done")
