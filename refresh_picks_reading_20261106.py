# -*- coding: utf-8 -*-
# Reading 分类轮换（2026-11-06）：新增 2 款，替换该分类 added_date 最早的条目
# 数据来源：2026-11-06 浏览器渲染 amazon.com/s?k=reading+glasses 搜索结果 + 详情页 DOM
# 图片直链取 #landingImage 的 data-old-hires，规范化为 _AC_SL1500_
# Usage: python refresh_picks_reading_20261106.py
import json, pathlib

ROOT = pathlib.Path(__file__).parent
PICKS = ROOT / 'picks.json'
CAT = 'Reading'
TARGET = 3
TODAY = '2026-11-06'

NEW = [
    {
        "category": CAT,
        "name": "Kerecsen 6-Pack Reading Glasses Blue Light Blocking, Spring Hinge Readers for Men Women, Computer Eyeglasses",
        "asin": "B0C1VGHJNL",
        "price": 13.99,
        "img_url": "https://m.media-amazon.com/images/I/61PWefr0HCL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B0C1VGHJNL?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "Six pairs of spring-hinge readers for $13.99 (about $2.33 a pair, down from the $16.99 typical price), rated 4.6 stars from 450 ratings with 500-plus bought in the past month and ranked #34 in Amazon's Reading Glasses chart; the listing describes blue-light-blocking high-definition lenses, an adjustable spring-hinge design, and a box that includes six storage bags and two cleaning cloths.",
        "added_date": TODAY,
        "img_ok": None,
        "link_ok": None,
        "last_checked": "",
    },
    {
        "category": CAT,
        "name": "2.0 Reading Glasses Mens, Oversized Readers, 4 Pack Black for Wide Face",
        "asin": "B0GN5P124V",
        "price": 9.49,
        "img_url": "https://m.media-amazon.com/images/I/61oiI6KJGfL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B0GN5P124V?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "An Amazon's Choice 4-pack of oversized black +2.00 readers for $9.49 (about $2.37 a pair), rated 4.5 stars from 725 ratings with 1K-plus bought in the past month and ranked #10 in Amazon's Reading Glasses chart; the listing highlights all-day-comfort spring hinges and scratch-resistant lenses aimed at work and crafts.",
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
