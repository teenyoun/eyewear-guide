import json, re, pathlib

base = pathlib.Path(__file__).parent
src = base / 'body_drafts' / 'black-friday-body.html'
html = src.read_text(encoding='utf-8')

fails = []
words = len(re.sub(r'<[^>]+>', ' ', html).split())
print('words: {0}'.format(words))
if words < 850:
    fails.append('word count too low')

if 'omitted chars' in html or '<omitted' in html:
    fails.append('TRUNCATION MARKER PRESENT')

# internal links must resolve to real local files
for m in re.findall(r'href="([^"]+)"', html):
    if m.startswith('http'):
        if 'tag=eyewearguide-20' not in m:
            fails.append('affiliate link missing tag: {0}'.format(m))
        if '/dp/' not in m:
            fails.append('affiliate link not /dp/: {0}'.format(m))
    else:
        if not (base / 'articles' / m).exists() and not (base / m).exists():
            fails.append('missing internal link target: {0}'.format(m))

if re.search(r'(cart|gp/aws|buy-now|checkout)', html, re.I):
    fails.append('cart-type affiliate link present')

# every affiliate anchor must carry rel=nofollow sponsored
for a in re.findall(r'<a [^>]*amazon\.com[^>]*>', html):
    if 'nofollow sponsored' not in a:
        fails.append('missing rel on: {0}'.format(a[:70]))

print('FAILS: {0}'.format(fails if fails else 'none'))

if not fails:
    q = json.loads((base / 'content-queue.json').read_text(encoding='utf-8'))
    hit = 0
    for a in q:
        if a.get('status') == 'pending' and a['title'].startswith('Black Friday Glasses Deals 2026'):
            a['body_html'] = html
            hit += 1
    (base / 'content-queue.json').write_text(json.dumps(q, ensure_ascii=False, indent=1), encoding='utf-8')
    print('queue updated: {0} item(s)'.format(hit))
    for a in q:
        if a.get('status') == 'pending':
            w = len(re.sub(r'<[^>]+>', ' ', a.get('body_html', '') or '').split())
            print('   {0:5d}w | {1}'.format(w, a['title'][:65]))
