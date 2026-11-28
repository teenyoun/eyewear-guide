# -*- coding: utf-8 -*-
# Reading 分类轮换（2026-11-28）：新增 2 款，按 added_date 最早替换，保持每类 3 款
# 数据来源：2026-11-28 浏览器 amazon.com/s?k=reading+glasses 搜索结果 + 详情页 DOM
# 图片直链取 #landingImage 的 data-old-hires，规范化为 _AC_SL1500_
# Usage: python refresh_picks_reading_20261128.py
import json, pathlib

ROOT = pathlib.Path(__file__).parent
PICKS = ROOT / 'picks.json'
CAT = 'Reading'
TARGET = 3
TODAY = '2026-11-28'

NEW = [
    {
        "category": CAT,
        "name": "Reading Glasses 5 Pairs Quality Readers Spring Hinge Glasses for Reading for Men and Women (5BLACK, 1.50)",
        "asin": "B0FQNJJ6ZH",
        "price": 9.68,
        "img_url": "https://m.media-amazon.com/images/I/61tDbKnD7UL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B0FQNJJ6ZH?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "A $9.68 five-pair set (25 percent off the $12.99 typical price, about $1.94 a pair) ranked #2 in Amazon's Reading Glasses chart with an Amazon's Choice badge, 4.6 stars from 1,512 ratings and 1K-plus bought in the past month; the NORPERWIS listing specifies full-rim rectangular plastic frames with spring hinges and anti-reflective coated plastic lenses at +1.50, a 5.2 cm lens width on an 18 mm bridge with 14 cm arms, shipped with five soft pouches and a cleaning cloth.",
        "added_date": TODAY,
        "img_ok": None,
        "link_ok": None,
        "last_checked": "",
    },
    {
        "category": CAT,
        "name": "Boost Eyewear 6 Pack Reading Glasses, Traditional Black Frames, for Men and Women, with Comfort Spring Loaded Hinges, Black, 6 Pairs (+1.50)",
        "asin": "B07RZ9KV5S",
        "price": 12.99,
        "img_url": "https://m.media-amazon.com/images/I/712ZBSsZ10L._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B07RZ9KV5S?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "A $12.99 six-pack (about $2.17 a pair) with 4.6 stars from 17,885 ratings, 1K-plus bought in the past month, an Amazon's Choice badge and a #38 rank in Amazon's Reading Glasses chart; Boost Eyewear lists black satin-finish rectangular polycarbonate frames with spring-loaded temple hinges and shatter-resistant lenses carrying a UV protection coating at +1.50, a 5.5 cm lens width on a 16 mm bridge with 10.5 cm arms, plus two microfiber cleaning cloths in the box.",
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
