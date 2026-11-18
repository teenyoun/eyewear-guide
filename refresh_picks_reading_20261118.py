# -*- coding: utf-8 -*-
# Reading 分类轮换（2026-11-18）：新增 2 款，按 added_date 最早替换，保持每类 3 款
# 数据来源：2026-11-18 浏览器渲染 amazon.com/s?k=reading+glasses 搜索结果 + 详情页 DOM
# 图片直链取 #landingImage 的 data-old-hires，规范化为 _AC_SL1500_
# Usage: python refresh_picks_reading_20261118.py
import json, pathlib

ROOT = pathlib.Path(__file__).parent
PICKS = ROOT / 'picks.json'
CAT = 'Reading'
TARGET = 3
TODAY = '2026-11-18'

NEW = [
    {
        "category": CAT,
        "name": "Kerecsen Reading Glasses 5 Pairs Fashion Ladies Readers Spring Hinge with Pattern Print Eyeglasses for Women (Mix Color -2, 1.75)",
        "asin": "B0B5KC35MN",
        "price": 9.99,
        "img_url": "https://m.media-amazon.com/images/I/61pBlcjivzL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B0B5KC35MN?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "An Amazon's Choice five-pair set of assorted pattern-print women's readers at $9.99 (33 percent off the $14.99 typical price), rated 4.7 stars from 681 ratings with 700-plus bought in the past month and a #10 rank in Amazon's Reading Glasses chart; the listing specifies spring-hinge temples on lightweight plastic frames with 2.13-inch lenses on a 19 mm bridge, 13 cm arms and a 13.5 cm frame width, with this ASIN carrying +1.75 magnification.",
        "added_date": TODAY,
        "img_ok": None,
        "link_ok": None,
        "last_checked": "",
    },
    {
        "category": CAT,
        "name": "JJWELL 3 Pack Reading Glasses for Men Blue Light Blocking Anti Eyestrain UV | Lightweight Metal Rectangle Semi Rimless Readers for Men, Half Frame Spring Hinge Eyeglasses with Pouches 150",
        "asin": "B091Q3477J",
        "price": 19.99,
        "img_url": "https://m.media-amazon.com/images/I/61gd3Cz2GOS._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B091Q3477J?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "An Amazon's Choice three-pack of men's readers at $19.99 (about $6.66 a pair), rated 4.5 stars from 1,183 ratings with 1K-plus bought in the past month and a #23 rank in Amazon's Reading Glasses chart; the listing pairs a textured metal semi-rimless rectangle frame and spring hinges with silicone nose pads, lenses it rates at 97 percent blue-light resistance plus UV400 protection, +1.50 magnification, and pouches with an anti-fog cloth in the box.",
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
