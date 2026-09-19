import json, pathlib, re

base = pathlib.Path(__file__).parent
live = {}
for f in (base / 'articles').glob('*.html'):
    t = f.read_text(encoding='utf-8', errors='ignore')
    if 'name="robots" content="noindex' in t:
        continue
    live[f.name] = t

print('LIVE: {0}'.format(len(live)))
pins = json.loads((base / 'pins-queue.json').read_text(encoding='utf-8'))
pinned = set(p['link'].split('/articles/')[-1] for p in pins if '/articles/' in p.get('link', ''))
unpinned = sorted(set(live) - pinned)
print('pins recorded: {0} | never pinned: {1}'.format(len(pins), len(unpinned)))
for s in unpinned:
    print('   ', s)

q = json.loads((base / 'content-queue.json').read_text(encoding='utf-8'))
pending = [a for a in q if a.get('status') == 'pending']
print('PENDING: {0}'.format(len(pending)))
