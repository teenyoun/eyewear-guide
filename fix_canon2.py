import re
from pathlib import Path

ART = Path("articles")
DOMAIN = "https://glasses.teenyoun.com"
fixed = 0
for f in ART.glob("*.html"):
    html = f.read_text(encoding="utf-8", errors="replace")
    if 'rel="canonical" href="https://glasses.teenyoun.com' in html:
        continue
    url = f"{DOMAIN}/articles/{f.name}"
    html = re.sub(r'<link rel="canonical"[^>]*>\s*', "", html)
    html = re.sub(r'<meta name="robots"[^>]*>\s*', "", html)
    inject = '<meta name="robots" content="index, follow">\n<link rel="canonical" href="' + url + '">\n'
    html = html.replace(
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n' + inject, 1)
    f.write_text(html, encoding="utf-8")
    fixed += 1
    print(f"fixed: {f.name}")
print(f"Total fixed: {fixed}")
