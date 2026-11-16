# -*- coding: utf-8 -*-
# Blue Light 分类轮换（2026-11-16）：新增 2 款，替换该分类 added_date 最早的条目
# 数据来源：2026-11-16 浏览器渲染 amazon.com/s?k=blue+light+blocking+glasses 搜索结果 + 详情页 DOM
# 图片直链取 #landingImage 的 data-old-hires，规范化为 https://m.media-amazon.com/images/I/XXX._AC_SL1500_.jpg
# Usage: python refresh_picks_blue_light_20261116.py
import json, pathlib

ROOT = pathlib.Path(__file__).parent
PICKS = ROOT / 'picks.json'
CAT = 'Blue Light'
TARGET = 3
TODAY = '2026-11-16'

NEW = [
    {
        "category": CAT,
        "name": "Blue Light Glasses Men, Metal Bluelight Computer Gaming Glasses",
        "asin": "B0DKSZQH78",
        "price": 22.98,
        "img_url": "https://m.media-amazon.com/images/I/7156kR-bPUL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B0DKSZQH78?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "An Amazon's Choice metal-frame pair at $22.98 rated 4.5 stars from 678 ratings with 2K-plus bought in the past month and a #25 rank in Amazon's Computer Blue Light Blocking Glasses chart; the ANYLUV listing describes a full-rim metal frame with polycarbonate lenses it says filter high-energy blue light from screens while keeping low color distortion, sized at 53 mm lenses on a 19 mm bridge with 148 mm temples.",
        "added_date": TODAY,
        "img_ok": True,
        "link_ok": None,
        "last_checked": "",
    },
    {
        "category": CAT,
        "name": "TIJN Olisa Blue Light Blocking Glasses for Women Men,Retro Oval Frame Bluelight Eyeglasses for Gaming Computer Screen Use",
        "asin": "B0D7PXQFLD",
        "price": 11.99,
        "img_url": "https://m.media-amazon.com/images/I/51EhnR6vrtL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B0D7PXQFLD?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "A $11.99 pair (20 percent off the $14.99 list) rated 4.3 stars from 968 ratings with 3K-plus bought in the past month and a #3 rank in Amazon's Women's Eyewear Frames chart; TIJN's listing specifies a 90s-style full-rim oval TR90 frame at 0.776 oz with 49 mm lenses on an 18 mm bridge and 146 mm temples, scratch-resistant polycarbonate lenses with 100% UV400 protection, and a case plus anti-fog cloth in the box.",
        "added_date": TODAY,
        "img_ok": True,
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
