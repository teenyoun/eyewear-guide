# -*- coding: utf-8 -*-
# Blue Light 分类轮换（2026-11-08）：新增 2 款，替换该分类 added_date 最早的条目
# 数据来源：2026-11-08 浏览器渲染 amazon.com/s?k=blue+light+blocking+glasses 搜索结果 + 详情页 DOM
# 图片直链取 #landingImage 的 data-old-hires，规范化为 _AC_SL1500_
# Usage: python refresh_picks_blue_light_20261108.py
import json, pathlib

ROOT = pathlib.Path(__file__).parent
PICKS = ROOT / 'picks.json'
CAT = 'Blue Light'
TARGET = 3
TODAY = '2026-11-08'

NEW = [
    {
        "category": CAT,
        "name": "Blue Light Glasses for Woman/Men",
        "asin": "B09M3R2PNT",
        "price": 7.98,
        "img_url": "https://m.media-amazon.com/images/I/71qHOGj-qOL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B09M3R2PNT?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "A $7.98 Amazon's Choice pick (43 percent off the $13.99 list) rated 4.5 stars from 10,172 ratings with 3K-plus bought in the past month and a #11 rank in Amazon's Computer Blue Light Blocking Glasses chart; the listing specifies anti-reflective polycarbonate lenses in a 1.6 oz full-rim rectangular plastic frame with 52 mm lenses, a 14 mm bridge and 140 mm temples, plus UV protection.",
        "added_date": TODAY,
        "img_ok": None,
        "link_ok": None,
        "last_checked": "",
    },
    {
        "category": CAT,
        "name": "Blue Light Blocking Glasses Men Computer Gaming Glasses Lightweight Al-Mg Metal Anti Eyestrain Eye Protection",
        "asin": "B07RGHSMGF",
        "price": 23.99,
        "img_url": "https://m.media-amazon.com/images/I/71bJg5w-gAL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B07RGHSMGF?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "An Amazon's Choice $23.99 pick rated 4.4 stars from 14,742 ratings with 4K-plus bought in the past month and a #15 rank in Amazon's Computer Blue Light Blocking Glasses chart; the listing pairs a full-rim Al-Mg metal square frame (56 mm lenses, 17 mm bridge, 135 mm temples) with low-color-distortion polycarbonate lenses it rates at a 45 percent overall blue-light block rate, packed in a triangular folding gift box.",
        "added_date": TODAY,
        "img_ok": None,
        "link_ok": None,
        "last_checked": "",
    },
]


def main():
    data = json.loads(PICKS.read_text(encoding='utf-8'))
    before = len(data)

    known = {p.get('asin') for p in data}
    new_items = [n for n in NEW if n['asin'] not in known]
    skipped = [n['asin'] for n in NEW if n['asin'] in known]
    if not new_items:
        print('NO_NEW_ITEMS')
        return

    pos = {id(p): i for i, p in enumerate(data)}
    existing = [p for p in data if p.get('category') == CAT]
    ordered = sorted(existing, key=lambda p: (p.get('added_date', ''), pos[id(p)]))
    overflow = len(existing) + len(new_items) - TARGET
    drop = ordered[:overflow] if overflow > 0 else []
    drop_ids = {id(p) for p in drop}

    out = [p for p in data if id(p) not in drop_ids] + new_items
    PICKS.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')

    print('picks.json total=%d -> %d | added=%d | dropped=%d' % (before, len(out), len(new_items), len(drop)))
    for n in new_items:
        print('  + ', CAT, '|', n['asin'], '| $', n['price'], '|', n['name'][:55])
    for d in drop:
        print('  - ', d.get('category'), '|', d.get('asin'), '| added', d.get('added_date'), '|', d.get('name', '')[:50])
    if skipped:
        print('  skipped:', ', '.join(skipped))
    for c in ('Blue Light', 'Reading', 'Sunglasses'):
        items = [p for p in out if p.get('category') == c]
        print('  [%s] %d: ' % (c, len(items)) + ', '.join('%s(%s)' % (p['asin'], p.get('added_date')) for p in items))


if __name__ == '__main__':
    main()
