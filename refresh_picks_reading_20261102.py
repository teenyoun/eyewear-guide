# -*- coding: utf-8 -*-
# Reading 分类轮换（2026-11-02）：新增 2 款，替换该分类 added_date 最早的条目
# 数据来源：2026-11-02 浏览器渲染 amazon.com/s?k=reading+glasses 搜索结果 + 详情页 DOM
# 图片直链取 #landingImage 的 data-old-hires，规范化为 _AC_SL1500_
# Usage: python refresh_picks_reading_20261102.py
import json, pathlib

ROOT = pathlib.Path(__file__).parent
PICKS = ROOT / 'picks.json'
CAT = 'Reading'
TARGET = 3
TODAY = '2026-11-02'

NEW = [
    {
        "category": CAT,
        "name": "Boost Eyewear 6 Pack Reading Glasses \u2013 Classic Black Rectangular Frames with Spring Hinges \u2013 Comfortable Eye Glasses Readers for Women & Men (+2.00)",
        "asin": "B07RYBPCCF",
        "price": 12.99,
        "img_url": "https://m.media-amazon.com/images/I/712ZBSsZ10L._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B07RYBPCCF?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "Six pairs of black rectangular readers with spring-loaded temples for $12.99 - about $2.17 a pair - an Amazon's Choice pick rated 4.6 stars from 17,793 ratings with 2K-plus bought in the past month and the #16 rank in Amazon's Reading Glasses chart; the listing gives a 5.5 cm lens width, a 16 mm bridge and 10.5 cm arms, says the lenses and frames are tested shatter-resistant, and adds two microfiber cleaning cloths.",
        "added_date": TODAY,
        "img_ok": None,
        "link_ok": None,
        "last_checked": "",
    },
    {
        "category": CAT,
        "name": "RBPilot Aviator Reading Glasses for Men Women - Blue Light Blocking",
        "asin": "B0BKPKLTNZ",
        "price": 23.99,
        "img_url": "https://m.media-amazon.com/images/I/51mD7YlpwcL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B0BKPKLTNZ?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "A single aviator-frame pair at $23.99 rated 4.4 stars from 304 ratings and ranked #29 in Amazon's Reading Glasses chart; the listing specifies an ultra-light metal frame with braided threaded temples and scratch-resistant resin lenses measuring 54 mm wide by 44 mm high on a 17 mm bridge with 140 mm temples, credits the lenses with blue-light blocking plus UV400 protection, and ships each pair with a cleaning cloth and glasses kit.",
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
