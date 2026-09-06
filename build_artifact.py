import re, base64, os

import sys
root = '/tmp/lecafe_check'
SOURCE = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
html = open(f'{root}/{SOURCE}', encoding='utf-8').read()
css = open(f'{root}/assets/css/style.css', encoding='utf-8').read()
js = open(f'{root}/assets/js/main.js', encoding='utf-8').read()

def data_uri(path, mime):
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('ascii')
    return f'data:{mime};base64,{b64}'

# Inline fonts referenced in CSS via url('../fonts/xxx.woff2')
def replace_font(m):
    fname = m.group(1)
    fpath = f'{root}/assets/fonts/{fname}'
    uri = data_uri(fpath, 'font/woff2')
    return f"url({uri})"

css = re.sub(r"url\('\.\./fonts/([^']+)'\)", replace_font, css)

# Inline images referenced in HTML: src="assets/images/xxx.webp"
def replace_img_src(m):
    attr = m.group(1)
    fname = m.group(2)
    fpath = f'{root}/assets/images/{fname}'
    uri = data_uri(fpath, 'image/webp')
    return f'{attr}="{uri}"'

html = re.sub(r'(src)="assets/images/([^"]+)"', replace_img_src, html)
html = re.sub(r'(data-gallery-src)="assets/images/([^"]+)"', replace_img_src, html)

# Remove preload links for fonts/images (no longer needed, would 404 as relative paths)
html = re.sub(r'\n?<link rel="preload"[^>]*>', '', html)

# Replace external stylesheet link with inline <style>
html = html.replace(
    '<link rel="stylesheet" href="assets/css/style.css">',
    f'<style>\n{css}\n</style>'
)

# Replace external script with inline <script>
html = html.replace(
    '<script src="assets/js/main.js" defer></script>',
    f'<script>\n{js}\n</script>'
)

# Strip DOCTYPE/html/head/body wrapper tags per Artifact publish contract,
# but keep their contents (title, meta, google fonts link, style, body content, script)
# Remove opening tags
html = re.sub(r'<!doctype html>\s*', '', html, flags=re.IGNORECASE)
html = re.sub(r'<html[^>]*>', '', html, flags=re.IGNORECASE)
html = re.sub(r'</html>\s*$', '', html, flags=re.IGNORECASE)
html = re.sub(r'<head>', '', html, flags=re.IGNORECASE)
html = re.sub(r'</head>', '', html, flags=re.IGNORECASE)
html = re.sub(r'<body[^>]*>', '', html, flags=re.IGNORECASE)
html = re.sub(r'</body>\s*$', '', html, flags=re.IGNORECASE)

# Remove charset/viewport meta (Artifact skeleton supplies these)
html = re.sub(r'<meta charset="[^"]*">\s*\n?', '', html, flags=re.IGNORECASE)
html = re.sub(r'<meta name="viewport"[^>]*>\s*\n?', '', html, flags=re.IGNORECASE)

with open(f'{root}/preview-artifact.html', 'w', encoding='utf-8') as f:
    f.write(html.strip() + '\n')

print("built, size:", os.path.getsize(f'{root}/preview-artifact.html'))
