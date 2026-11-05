# -*- coding: utf-8 -*-
# Blue Light 分类轮换（2026-11-05）：新增 2 款，替换该分类 added_date 最早的条目
# 数据来源：2026-11-05 浏览器渲染 amazon.com/s?k=blue+light+blocking+glasses 搜索结果 + 详情页 DOM
# 图片直链取 #landingImage 的 data-old-hires，规范化为 _AC_SL1500_
# Usage: python refresh_picks_blue_light_20261105.py
import json, pathlib

ROOT = pathlib.Path(__file__).parent
PICKS = ROOT / 'picks.json'
CAT = 'Blue Light'
TARGET = 3
TODAY = '2026-11-05'

NEW = [
    {
        "category": CAT,
        "name": "Blue Light Glasses for Men Women, Lightweight Computer Glasses",
        "asin": "B07GRPXNX4",
        "price": 25.95,
        "img_url": "https://m.media-amazon.com/images/I/51xx2lqShfL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B07GRPXNX4?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "An Amazon's Choice pair at $25.95, rated 4.5 stars from 34,417 ratings and ranked #54 in Amazon's Computer Blue Light Blocking Glasses chart; the listing specifies an 18 g flexible Areolite frame with a 143 mm medium-width fit and clear lenses it says filter blue light without a yellow tint, backed by a lifetime warranty.",
        "added_date": TODAY,
        "img_ok": None,
        "link_ok": None,
        "last_checked": "",
    },
    {
        "category": CAT,
        "name": "TIJN Sleep Glasses with Blue Green Light Blocking, Red Light Lens for Computer Gaming, Screen Fatigue & UV Protection",
        "asin": "B0DHGMBZ36",
        "price": 17.99,
        "img_url": "https://m.media-amazon.com/images/I/51PiyDXjiXL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B0DHGMBZ36?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "A $17.99 pair (31 percent off the $25.99 list) with red-tinted lenses rated 4.4 stars from 53,252 ratings and ranked #11 in Amazon's Computer Blue Light Blocking Glasses chart; the listing gives plastic lenses 5.3 cm wide by 42 mm high on an 18 mm bridge with a 135 mm frame width and 14 cm arms, credited with filtering blue and green light plus anti-glare and UV protection.",
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
