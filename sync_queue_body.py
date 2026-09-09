import json, pathlib, re

updates = [
    'best-sunglasses-for-kids-uv-protection-they-ll-actually-wear.html',
    'best-eyeglass-frames-for-men-2026-style-guide.html',
    'night-driving-glasses-do-yellow-lenses-actually-help-.html',
]
q = json.load(open('content-queue.json', encoding='utf-8'))
for item in q:
    fn = item.get('filename', '')
    if fn in updates:
        c = (pathlib.Path('articles') / fn).read_text(encoding='utf-8')
        m = re.search(r'<article>(.*?)(?=<div class="info-box")', c, re.S)
        if m:
            item['body_html'] = m.group(1).strip()
            print('queue synced:', fn, '| body chars:', len(item['body_html']))
json.dump(q, open('content-queue.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('queue saved')
