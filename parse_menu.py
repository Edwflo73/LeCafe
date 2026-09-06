import re, json

def clean(s):
    s = re.sub(r'<[^>]+>', '', s or '').strip()
    s = s.replace('&aacute;','á').replace('&eacute;','é').replace('&iacute;','í').replace('&oacute;','ó').replace('&uacute;','ú').replace('&ntilde;','ñ')
    return s

def price_number(p):
    m = re.search(r'([\d.]+)', p)
    return m.group(1) if m else p

TAB_LABELS = {
    'especialidades': 'Especialidades de la casa',
    'frappe': 'Frappé',
    'alimentos': 'Alimentos',
    'frias': 'Bebidas frías',
    'calientes': 'Bebidas calientes',
}

ITEM_RE = re.compile(
    r'<div class="menu-item">\s*'
    r'<div class="mi-name-wrap">\s*'
    r'<div class="mi-name">(.*?)</div>\s*'
    r'(?:<div class="mi-desc">(.*?)</div>\s*)?'
    r'</div>\s*'
    r'<div class="mi-leader"></div>\s*'
    r'<div class="mi-price">(.*?)</div>\s*'
    r'</div>',
    re.DOTALL
)

def extract_items(chunk):
    items = []
    for name_raw, desc_raw, price_raw in ITEM_RE.findall(chunk):
        tag_m = re.search(r'<span class="mi-tag">(.*?)</span>', name_raw)
        tag = clean(tag_m.group(1)) if tag_m else None
        name = clean(re.sub(r'<span class="mi-tag">.*?</span>', '', name_raw))
        desc = clean(desc_raw) if desc_raw else None
        item = {"@type": "MenuItem", "name": name}
        if desc:
            item["description"] = desc
        if tag:
            item["menuAddOn"] = tag  # informal use: keeps the badge text (e.g. "Especial", "Con café")
        item["offers"] = {"@type": "Offer", "price": price_number(clean(price_raw)), "priceCurrency": "MXN"}
        items.append(item)
    return items

def build_menu_jsonld(menu_html):
    sections = []
    panel_re = re.compile(r'<div class="menu-panel"[^>]*id="panel-([a-z]+)">(.*?)</div>\s*</div>\s*(?=<div class="menu-panel"|</div>\s*</div>\s*</div>\s*<div class="menu-cta)', re.DOTALL)
    # fallback simpler split: by known panel ids in order
    ids = ['especialidades', 'frappe', 'alimentos', 'frias', 'calientes']
    starts = {}
    for pid in ids:
        m = re.search(rf'<div class="menu-panel[^"]*"[^>]*id="panel-{pid}">', menu_html)
        starts[pid] = m.start() if m else None
    ordered = [p for p in ids if starts[p] is not None]
    for idx, pid in enumerate(ordered):
        start = starts[pid]
        end = starts[ordered[idx+1]] if idx+1 < len(ordered) else len(menu_html)
        chunk = menu_html[start:end]
        # split on subheads
        subhead_matches = list(re.finditer(r'<div class="menu-subhead">(.*?)</div>', chunk))
        if not subhead_matches:
            main_items = extract_items(chunk)
            sections.append({
                "@type": "MenuSection",
                "name": TAB_LABELS[pid],
                "hasMenuItem": main_items,
            })
        else:
            first_sub_start = subhead_matches[0].start()
            main_chunk = chunk[:first_sub_start]
            main_items = extract_items(main_chunk)
            section_obj = {"@type": "MenuSection", "name": TAB_LABELS[pid]}
            if main_items:
                section_obj["hasMenuItem"] = main_items
            subsections = []
            for i, sm in enumerate(subhead_matches):
                sub_name = clean(sm.group(1))
                sub_start = sm.end()
                sub_end = subhead_matches[i+1].start() if i+1 < len(subhead_matches) else len(chunk)
                sub_chunk = chunk[sub_start:sub_end]
                subsections.append({
                    "@type": "MenuSection",
                    "name": sub_name,
                    "hasMenuItem": extract_items(sub_chunk),
                })
            section_obj["hasMenuSection"] = subsections
            sections.append(section_obj)
    return {
        "@type": "Menu",
        "name": "Menú Le Café",
        "hasMenuSection": sections,
    }

if __name__ == '__main__':
    html = open('/tmp/lecafe_check/menu.html', encoding='utf-8').read()
    menu_jsonld = build_menu_jsonld(html)
    total_items = sum(
        len(s.get("hasMenuItem", [])) + sum(len(sub.get("hasMenuItem", [])) for sub in s.get("hasMenuSection", []))
        for s in menu_jsonld["hasMenuSection"]
    )
    print("sections:", [s["name"] for s in menu_jsonld["hasMenuSection"]])
    print("total items parsed:", total_items)
    print(json.dumps(menu_jsonld, ensure_ascii=False, indent=2)[:2000])
