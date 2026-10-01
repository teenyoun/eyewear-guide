import pathlib

base = pathlib.Path(__file__).parent
SITE = 'https://teenyoun.com'

# alias slug -> real article slug (verified existing)
aliases = {
    'blue-light-glasses-vs-anti-glare': 'anti-reflective-coating-vs-blue-light-filter-worth-paying-for-both-',
    'progressive-lenses-vs-bifocals-vs-single-vision-which-do-you-need': 'progressive-lenses-vs-bifocals-vs-single-vision-which-do-you-need-',
    'night-driving-glasses-do-yellow-lenses-actually-help': 'night-driving-glasses-do-yellow-lenses-actually-help-',
    'best-sunglasses-for-kids-uv-protection-theyll-actually-wear': 'best-sunglasses-for-kids-uv-protection-they-ll-actually-wear',
    'best-womens-sunglasses-2026-classic-to-trendy': 'best-women-s-sunglasses-2026-classic-to-trendy',
    'how-to-read-your-glasses-prescription-sph-cyl-axis-explained': 'how-to-read-your-glasses-prescription-od-os-sph-cyl-explained',
    'progressive-lens-adaptation-how-to-get-used-to-them-fast': 'progressive-lens-adaptation-week-by-week-adjustment-guide',
}

TPL = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="0; url={url}">
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="{url}">
<title>Redirecting - Eyewear Guide</title>
<style>body{{font-family:system-ui,sans-serif;max-width:640px;margin:80px auto;padding:0 20px;text-align:center;color:#333}}
a{{color:#1a73e8}}</style>
</head>
<body>
<p>This page has moved.</p>
<p><a href="{url}">Continue to the article &rarr;</a></p>
</body>
</html>
'''

count = 0
for alias, real in aliases.items():
    target = base / 'articles' / f'{real}.html'
    if not target.exists():
        print(f'SKIP (missing target): {alias} -> {real}')
        continue
    url = f'{SITE}/articles/{real}.html'
    (base / 'articles' / f'{alias}.html').write_text(TPL.format(url=url), encoding='utf-8')
    # also drop the alias into articles dir only; not added to sitemap by rebuild (sitemap scans only known list? verify) 
    count += 1
    print(f'alias created: {alias} -> {real}')
print('total aliases:', count)
