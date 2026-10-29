# -*- coding: utf-8 -*-
# Blue Light 分类轮换（2026-10-29）：新增 2 款，替换该分类 added_date 最早的条目
# 数据来源：2026-10-29 浏览器渲染 Amazon 搜索结果 + 详情页 DOM（价格/评分/图片取自已渲染页面）
# Usage: python refresh_picks_blue_light_20261029.py
import json, pathlib

ROOT = pathlib.Path(__file__).parent
PICKS = ROOT / 'picks.json'
CAT = 'Blue Light'
TARGET = 3
TODAY = '2026-10-29'

NEW = [
    {
        "category": CAT,
        "name": "Benicci Stylish Blue Light Blocking Glasses for Women or Men - Ease Computer and Digital Eye Strain, Dry Eyes, Headaches and Blurry Vision - Instantly Blocks Glare from Computers and Phone Screens w/Case",
        "asin": "B086C66SZ2",
        "price": 21.97,
        "img_url": "https://m.media-amazon.com/images/I/718y8rJhqSL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B086C66SZ2?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "An Amazon's Choice clear-lens pair at $21.97, rated 4.4 stars from 15,260 ratings with 3K-plus bought in the past month and a #43 rank in Amazon's Computer Blue Light Blocking Glasses chart; the listing describes a non-magnifying anti-glare lens that blocks glare from computer and phone screens, shipped with a protective storage case.",
        "added_date": TODAY,
        "img_ok": None,
        "link_ok": None,
        "last_checked": "",
    },
    {
        "category": CAT,
        "name": "ANYLUV Blue Light Blocking Glasses Men Computer Gaming Glasses Lightweight Al-Mg Metal Anti Eyestrain Eye Protection Black Clear 0x",
        "asin": "B07RGHSMGF",
        "price": 23.99,
        "img_url": "https://m.media-amazon.com/images/I/71bJg5w-gAL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B07RGHSMGF?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "An Amazon's Choice men's pair at $23.99, rated 4.4 stars from 14,708 ratings with 3K-plus bought in the past month and a #19 rank in Amazon's Computer Blue Light Blocking Glasses chart; the listing specifies a lightweight Al-Mg metal frame with clear 0.0x non-magnifying lenses, a quoted 45 percent overall blue block rate and a low-color-distortion lens, packed in a folding triangular box.",
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
