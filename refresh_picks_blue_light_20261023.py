# -*- coding: utf-8 -*-
# Blue Light 分类轮换（2026-10-23）：新增 2 款，替换该分类 added_date 最早的条目
# 数据来源：2026-10-23 浏览器读 Amazon 详情页 DOM + web_fetch 复核文本字段
# Usage: python refresh_picks_blue_light_20261023.py
import json, pathlib

ROOT = pathlib.Path(__file__).parent
PICKS = ROOT / 'picks.json'
CAT = 'Blue Light'
TARGET = 3
TODAY = '2026-10-23'

# 并列处置：现有 10-17 两条 = B0B2R4NR2F(Oilway, 6,720 评分, 类别#13, 月销3K+, $8.99)
#                              与 B0GYNQZMB6(TIJN, 53,232 评分, 类别#12, 月销2K+, $9.99)。
# 保留 TIJN：评分基数与类别排名更优（信号更强者）。

NEW = [
    {
        "category": CAT,
        "name": "ANRRI Blue Light Glasses for Men Women, Lightweight Computer Glasses | Square Black Frame, Anti-Glare Lens, Comfortable for Everyday Screens",
        "asin": "B07GRPXNX4",
        "price": 25.95,
        "img_url": "https://m.media-amazon.com/images/I/51xx2lqShfL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B07GRPXNX4?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "An Amazon's Choice single pair at $25.95, rated 4.5 stars from 34,409 ratings with 900-plus bought in the past month and a #74 rank in Amazon's Computer Blue Light Blocking Glasses chart; the listing specifies an 18 g TR90 rectangular full-rim frame (143 mm wide, 52 mm lens, 19 mm bridge, 145 mm arms) with polycarbonate anti-glare lenses the brand says clear blue light without a yellow tint, and the box holds a case, cleaning cloth and blue light test card.",
        "added_date": TODAY,
        "img_ok": None,
        "link_ok": None,
        "last_checked": "",
    },
    {
        "category": CAT,
        "name": "MAXJULI Blue Light Blocking Glasses, Computer Reading/Gaming/TV/Phones Glasses for Women Men (Transparent)",
        "asin": "B081RLZWG7",
        "price": 6.99,
        "img_url": "https://m.media-amazon.com/images/I/51yeBfRCRUL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B081RLZWG7?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "A $6.99 clear-lens pair rated 4.4 stars from 37,830 ratings with 600-plus bought in the past month and the #34 rank in Amazon's Computer Blue Light Blocking Glasses chart; the listing describes a transparent square full-rim plastic frame at 1.44 oz with 52 mm lenses, an 18 mm bridge and 137 mm arms, and a polycarbonate lens it credits with blue-light filtering and UV400 protection.",
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
