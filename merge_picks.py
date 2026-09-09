import json, pathlib, datetime

blurbs = {
    'B086WQ1CL8': "Amber wayfarer frames that block 99% of blue light — our pick for evening screen use and winding down before bed.",
    'B077QDGWX8': "The best-reviewed gaming pair on Amazon (17,000+ ratings): clear yellow lenses that cut screen glare without heavy tint.",
    'B00LJOQ5NW': "A 5-pack of solid readers for men — keep one at the desk, one in the car, one in the bag and never hunt for glasses again.",
    'B07PNMMRCY': "Four stylish women's readers in one set — mix round, cat-eye and square frames to match outfits instead of one boring pair.",
    'B07MRD7118': "Three pairs of polarized shades with UV400 for the price of one — throw them in the car, office and beach bag without worry.",
    'B00SMRN2DU': "Wraparound sports sunglasses with polarized UV400 lenses that stay put on runs and rides — a budget pick that outlasts its price.",
}

cats = {
    'blue-light': 'Blue Light',
    'reading': 'Reading',
    'sunglasses': 'Sunglasses',
}

batch = json.loads((pathlib.Path('picks_batch1.json')).read_text(encoding='utf-8'))
picks = []
for item in batch:
    picks.append({
        'category': cats.get(item['category'], item['category']),
        'name': item['name'],
        'asin': item['asin'],
        'price': item['price'],
        'img_url': item['img_url'],
        'link_url': item['link_url'],
        'source': item.get('source', 'ogimage'),
        'blurb': blurbs.get(item['asin'], ''),
        'added_date': datetime.date.today().isoformat(),
        'last_checked': '',
        'img_ok': None,
        'link_ok': None,
    })
out = pathlib.Path('picks.json')
data = json.loads(out.read_text(encoding='utf-8')) if out.exists() else []
seen = {x['asin'] for x in data}
added = 0
for p in picks:
    if p['asin'] not in seen:
        data.append(p)
        seen.add(p['asin'])
        added += 1
out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
print(f'picks.json total={len(data)} added={added}')
for x in data:
    print(' -', x['category'], '|', x['asin'], '|', x['name'][:45], '| $', x['price'])
