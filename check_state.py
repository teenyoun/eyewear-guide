import json, pathlib, re, datetime

base = pathlib.Path(__file__).parent
live = {}
for f in sorted((base / 'articles').glob('*.html'), key=lambda p: p.stat().st_mtime, reverse=True):
    t = f.read_text(encoding='utf-8', errors='ignore')
    if 'name="robots" content="noindex' in t:
        continue
    live[f.name] = t

print('LIVE ARTICLES: {0}'.format(len(live)))
files = sorted(live.keys(), key=lambda n: (base / 'articles' / n).stat().st_mtime, reverse=True)
print('newest 3:')
for n in files[:3]:
    m = datetime.datetime.fromtimestamp((base / 'articles' / n).stat().st_mtime)
    mm = re.search(r'<article>(.*?)</article>', live[n], re.S)
    w = len(re.sub(r'<[^>]+>', ' ', mm.group(1) if mm else '').split())
    print('   {0} | {1:5d}w | {2}'.format(m.strftime('%m-%d %H:%M'), w, n))

pins = json.loads((base / 'pins-queue.json').read_text(encoding='utf-8'))
pinned = set(p['link'].split('/articles/')[-1] for p in pins if '/articles/' in p.get('link', ''))
unpinned = sorted(set(live) - pinned)
print('\nlive {0} | pinned {1} | never pinned {2}'.format(len(live), len(pinned), len(unpinned)))
for s in unpinned:
    print('   ', s)

q = json.loads((base / 'content-queue.json').read_text(encoding='utf-8'))
print('\nPENDING:')
for a in q:
    if a.get('status') == 'pending':
        w = len(re.sub(r'<[^>]+>', ' ', a.get('body_html', '') or '').split())
        print('   {0:5d}w | {1}'.format(w, a['title'][:70]))
