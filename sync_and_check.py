import pathlib, re, json, subprocess

base = pathlib.Path(__file__).parent

# 1) rescan all articles
rows = []
for f in sorted((base / 'articles').glob('*.html'), key=lambda p: p.stat().st_mtime, reverse=True):
    c = f.read_text(encoding='utf-8', errors='ignore')
    m = re.search(r'<article>(.*?)</article>', c, re.S)
    words = len(re.sub(r'<[^>]+>', ' ', m.group(1) if m else '').split())
    rows.append((words, f.name))
shells = [(w, n) for w, n in rows if w < 100]
thins = [(w, n) for w, n in rows if 100 <= w < 300]
print('TOTAL:', len(rows))
print('SHELLS remaining:', len(shells))
for w, n in shells:
    print('  ', w, n)
print('THIN remaining:', len(thins))
for w, n in thins:
    print('  ', w, n)

# 2) sync queue body records for the 3 fixed articles
fixes = {
    'how-to-measure-your-face-for-glasses-at-home-3-easy-methods.html': 'body_drafts/measure-face.html',
    'how-to-read-your-glasses-prescription-od-os-sph-cyl-explained.html': 'body_drafts/read-prescription.html',
    'best-sports-sunglasses-for-running-stay-cool-and-see-clearly.html': 'body_drafts/sports-running.html',
}
q = json.load(open(base / 'content-queue.json', encoding='utf-8'))
synced = []
for item in q:
    fn = item.get('filename', '')
    if fn in fixes:
        item['body_html'] = (base / fixes[fn]).read_text(encoding='utf-8')
        synced.append(fn)
json.dump(q, open(base / 'content-queue.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('queue synced:', len(synced))

# 3) commit only (push executed separately with token injected from secrets)
subprocess.run(['git', 'add', '-A'], cwd=base, check=True, capture_output=True)
subprocess.run(['git', 'commit', '-m', 'fix 3 shell articles: measure-face, read-prescription, sports-running'], cwd=base, check=True, capture_output=True)
print('committed')
