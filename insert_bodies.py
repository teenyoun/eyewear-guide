import re, pathlib, sys

pairs = [
    ('best-sunglasses-for-kids-uv-protection-they-ll-actually-wear.html', 'body_drafts/kids-sunglasses-body.html'),
    ('best-eyeglass-frames-for-men-2026-style-guide.html', 'body_drafts/men-frames-body.html'),
    ('night-driving-glasses-do-yellow-lenses-actually-help-.html', 'body_drafts/night-driving-body.html'),
]
for target, draft in pairs:
    path = pathlib.Path('articles') / target
    html = path.read_text(encoding='utf-8')
    body = pathlib.Path(draft).read_text(encoding='utf-8').strip()
    m = re.search(r'(<p class="byline">.*?</p>)', html, re.S)
    if not m:
        print('NO BYLINE:', target)
        continue
    new_html = html[:m.end()] + '\n' + body + '\n' + html[m.end():]
    path.write_text(new_html, encoding='utf-8')
    art = re.search(r'<article>(.*?)</article>', new_html, re.S).group(1)
    words = len(re.sub(r'<[^>]+>', ' ', art).split())
    print(target, '-> words in article:', words)
