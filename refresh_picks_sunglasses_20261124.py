# -*- coding: utf-8 -*-
# Sunglasses 分类轮换（2026-11-24）：新增 2 款，按 added_date 最早替换，保持每类 3 款
# 数据来源：2026-11-24 浏览器渲染 amazon.com/s?k=polarized+sunglasses+men 搜索结果 + 详情页 DOM
# 图片直链取 #landingImage 的 data-old-hires，规范化为 _AC_SL1500_
# Usage: python refresh_picks_sunglasses_20261124.py
import json, pathlib

ROOT = pathlib.Path(__file__).parent
PICKS = ROOT / 'picks.json'
CAT = 'Sunglasses'
TARGET = 3
TODAY = '2026-11-24'

NEW = [
    {
        "category": CAT,
        "name": "ZENOTTIC Polarized Sunglasses for Men Lightweight TR90 Frame UV400 Protection Square Sun Glasses",
        "asin": "B07FGVCGVF",
        "price": 26.15,
        "img_url": "https://m.media-amazon.com/images/I/71fLXt38SsL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B07FGVCGVF?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "An Overall Pick square frame at $26.15 (about 23 percent off the $33.99 list) rated 4.4 stars from 21,872 ratings with 2K-plus bought in the past month and a #6 rank in Amazon's Men's Sunglasses chart; the ZENOTTIC listing specifies a lightweight TR90 frame with polarized TAC lenses under a UV400 coating it says blocks 100 percent of UVA, UVB and UVC rays up to 400 nm, 60 mm lenses by 48 mm high on an 18 mm bridge with 135 mm temples and a 140 mm frame width, flex hinges rather than spring hinges, and a box that adds a microfiber pouch, glasses box and polarized test card.",
        "added_date": TODAY,
        "img_ok": None,
        "link_ok": None,
        "last_checked": "",
    },
    {
        "category": CAT,
        "name": "LUENX Aviator Polarized Sunglasses for Men: Square UV400 Driving",
        "asin": "B08R5DZKY9",
        "price": 12.40,
        "img_url": "https://m.media-amazon.com/images/I/71mgPWkGi2L._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B08R5DZKY9?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "A $12.40 square-aviator pair (about 27 percent off the $16.99 list) rated 4.5 stars from 8,708 ratings with 5K-plus bought in the past month and a #3 rank in Amazon's Men's Sunglasses chart; the LUENX listing pairs a metal frame with a striped matte finish, one-piece plastic temples on reinforced metal hinges and adjustable silicone nose pads with polarized TAC lenses it credits with UV400 protection and glare filtering, sized at 61 mm lenses on a 15 mm bridge with a 148 mm frame width, shipped with a cleaning cloth, pouch, carton and polarized test card.",
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
