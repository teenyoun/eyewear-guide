# -*- coding: utf-8 -*-
# Blue Light 分类轮换（2026-11-10）：新增 2 款，替换该分类 added_date 最早的条目
# 数据来源：2026-11-10 浏览器渲染 amazon.com/s?k=blue+light+blocking+glasses 搜索结果 + 详情页 DOM
# 图片直链取 #landingImage 的 data-old-hires，规范化为 _AC_SL1500_
# Usage: python refresh_picks_blue_light_20261110.py
import json, pathlib

ROOT = pathlib.Path(__file__).parent
PICKS = ROOT / 'picks.json'
CAT = 'Blue Light'
TARGET = 3
TODAY = '2026-11-10'

NEW = [
    {
        "category": CAT,
        "name": "Blue Light Glasses Men, Al-Mg Metal Computer Gaming Glasses Blue Light Blocking Clear Lens, Feather-Light Hand-Polished Alloy Frame, All-Day Comfort Fit, Gift-Ready Kit",
        "asin": "B0D8VZ1395",
        "price": 20.69,
        "img_url": "https://m.media-amazon.com/images/I/815QJSi7KiL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B0D8VZ1395?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "A $20.69 pair (10 percent off the $22.99 list) rated 4.4 stars from 1,396 ratings with 3K-plus bought in the past month and a #7 rank in Amazon's Computer Blue Light Blocking Glasses chart; the listing specifies a 22.6 g Al-Mg metal full-rim square frame (58 mm lenses, 18 mm bridge, 140 mm arms) with spring hinges and adjustable nose pads, clear polycarbonate lenses it says filter blue-violet glare without a yellow cast, and a gift box that adds a foldable hard case, dust pouch and microfiber cloth.",
        "added_date": TODAY,
        "img_ok": None,
        "link_ok": None,
        "last_checked": "",
    },
    {
        "category": CAT,
        "name": "Blue Light Blocking Glasses Anti Eyestrain Computer Gaming Glasses Vintage Half Frame UV Clear Lens for Women Men",
        "asin": "B07Z8PHTSS",
        "price": 11.99,
        "img_url": "https://m.media-amazon.com/images/I/61-0EpsPCGL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B07Z8PHTSS?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "A $11.99 pair rated 4.4 stars from 19,445 ratings with 1K-plus bought in the past month and a #27 rank in Amazon's Computer Blue Light Blocking Glasses chart; the listing describes a 1.58 oz semi-rimless plastic half-frame with 51 mm polycarbonate lenses on a 21 mm bridge and 140 mm arms, marketed to cut blue light, glare and eye strain, and shipped with a lens wipe, paper box and pouch.",
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
