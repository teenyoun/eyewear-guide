# -*- coding: utf-8 -*-
# Sunglasses 分类轮换（2026-10-21）：新增 2 款，替换该分类 added_date 最早的 2 条
# Usage: python refresh_picks_sunglasses_20261021.py
#
# 轮换判据：以 picks.json 各分类「最新 added_date」为准 —— Blue Light 2026-10-17、
# Reading 2026-10-19、Sunglasses 2026-10-15（三者最旧）→ 本轮应轮 Sunglasses。
# 该分类现有 3 款，新增 2 款 → 淘汰 added_date 最早的 2 条：
#   B07Z8Q3GV9 (2026-10-09) 必淘汰；
#   10-15 并列的两条按「当前需求信号」取强者保留：
#     B0BKSKCYX7 = Men's Sunglasses #1 Best Seller、10K+/月、5,024 评 → 保留
#     B07MW4R1X3 = Men's Sunglasses #4、4K+/月、43,301 评（2 件套）→ 淘汰
import json, pathlib

ROOT = pathlib.Path(__file__).parent
PICKS = ROOT / 'picks.json'
CAT = 'Sunglasses'
TARGET = 3
TODAY = '2026-10-21'
RETAIN_ON_TIE = {'B0BKSKCYX7'}

NEW = [
    {
        "category": CAT,
        "name": "Polarized Sports Wrap Around Sunglasses Men Fishing Running Golf",
        "asin": "B0D97BWLZ4",
        "price": 16.89,
        "img_url": "https://m.media-amazon.com/images/I/71FmGCjYEkL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B0D97BWLZ4?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "Three wrap-around sport pairs for $16.89 (list $25.99) - about $5.63 each - rated 4.5 stars from 5,598 ratings with 2K-plus bought in the past month and a #7 rank in Amazon's Sunglasses chart; the listing specifies a polycarbonate frame with tri-acetate cellulose (TAC) polarized lenses and non-slip rubber nose pads, and the box holds one glasses case, a cloth and pouch plus three neck straps and a polarization test card.",
        "added_date": TODAY,
        "img_ok": None,
        "link_ok": None,
        "last_checked": "",
    },
    {
        "category": CAT,
        "name": "Lamicall 24g Polarized Sports Sunglasses for Men Women - UV400 Protection Sun Glasses for Baseball Running Cycling Fishing",
        "asin": "B0DYV736NT",
        "price": 21.99,
        "img_url": "https://m.media-amazon.com/images/I/51QRgSdOm4L._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B0DYV736NT?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "An ultralight sports shield at $21.99 (15 percent off the $25.99 list) carrying the #1 Best Seller badge in Amazon's Powersports Sunglasses chart - 4.4 stars from 1,594 ratings with 4K-plus bought in the past month; the listing specifies a semi-rimless TR90 frame at 24 g with tri-acetate cellulose (TAC) lenses, silicone temple tips, UV400 protection and a two-year warranty.",
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
        print('NO_NEW_ITEMS (all candidate ASINs already in picks.json)')
        return

    pos = {id(p): i for i, p in enumerate(data)}
    existing = [p for p in data if p.get('category') == CAT]
    ordered = sorted(
        existing,
        key=lambda p: (p.get('added_date', ''), 1 if p.get('asin') in RETAIN_ON_TIE else 0, pos[id(p)]),
    )
    overflow = len(existing) + len(new_items) - TARGET
    drop = ordered[:overflow] if overflow > 0 else []
    drop_ids = {id(p) for p in drop}

    out = [p for p in data if id(p) not in drop_ids] + new_items
    PICKS.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')

    print('picks.json total=%d -> %d | added=%d | dropped=%d' % (before, len(out), len(new_items), len(drop)))
    for n in new_items:
        print('  + ', CAT, '|', n['asin'], '| $', n['price'], '|', n['name'][:50])
    for d in drop:
        print('  - ', d.get('category'), '|', d.get('asin'), '| added', d.get('added_date'), '|', d.get('name', '')[:50])
    if skipped:
        print('  skipped (ASIN already present):', ', '.join(skipped))
    for c in ('Blue Light', 'Reading', 'Sunglasses'):
        items = [p for p in out if p.get('category') == c]
        print('  [%s] %d: ' % (c, len(items)) + ', '.join('%s(%s)' % (p['asin'], p.get('added_date')) for p in items))


if __name__ == '__main__':
    main()
