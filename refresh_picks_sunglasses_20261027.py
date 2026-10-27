# -*- coding: utf-8 -*-
# Sunglasses 分类轮换（2026-10-27）：新增 2 款，替换该分类 added_date 最早的 2 条
# Usage: python refresh_picks_sunglasses_20261027.py
#
# 轮换判据：以 picks.json 各分类「最新 added_date」为准 —— Blue Light 2026-10-23、
# Reading 2026-10-25、Sunglasses 2026-10-21（三者最旧）→ 本轮应轮 Sunglasses。
# 该分类现有 3 款，新增 2 款 → 淘汰 added_date 最早的 2 条：
#   B0BKSKCYX7 (2026-10-15) 必淘汰（且上一轮 link_check 已为 link_ok=false）；
#   10-21 并列的两条按「当前需求信号」取强者保留：
#     B0DYV736NT = Men's Powersports #1 Best Seller、4K+/月、1,594 评 → 保留
#     B0D97BWLZ4 = #7、2K+/月、5,598 评（3 件套）→ 淘汰
#
# 选品：B0C7KYKTL5 = 详情页标题区自带 Amazon's Choice 徽章、5K+/月、4,029 评；
#       B01LYQK0YX = 27,164 评、Men's Sunglasses #10、2K+/月、单副装。
# 主动放弃 B07MW4R1X3（KALIYADI，43,339 评）：该 ASIN 于 2026-10-21 刚被本页淘汰，
# 6 天内回购会造成榜单churn，改为引入从未上过榜的高评新品。
import json, pathlib

ROOT = pathlib.Path(__file__).parent
PICKS = ROOT / 'picks.json'
CAT = 'Sunglasses'
TARGET = 3
TODAY = '2026-10-27'
RETAIN_ON_TIE = {'B0DYV736NT'}

NEW = [
    {
        "category": CAT,
        "name": "Square Polarized Sunglasses for Men and Women Lightweight Frame Sun Glasses with UV Protection",
        "asin": "B0C7KYKTL5",
        "price": 12.99,
        "img_url": "https://m.media-amazon.com/images/I/71aBQnp4XbL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B0C7KYKTL5?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "An Amazon's Choice single pair at $12.99 (35 percent off the $19.99 list) rated 4.5 stars from 4,029 ratings with 5K-plus bought in the past month and a #17 rank in Amazon's Men's Sunglasses chart; the listing describes a square frame with adjustable metal gripper hinges and TAC polarized lenses it credits with UVA/UVB protection and glare reduction, aimed at driving, fishing and cycling.",
        "added_date": TODAY,
        "img_ok": None,
        "link_ok": None,
        "last_checked": "",
    },
    {
        "category": CAT,
        "name": "SUNGAIT Ultra Lightweight Rectangular Polarized Sunglasses Men UV400 Protection",
        "asin": "B01LYQK0YX",
        "price": 16.99,
        "img_url": "https://m.media-amazon.com/images/I/51BDws-WvKL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B01LYQK0YX?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "A $16.99 single pair rated 4.6 stars from 27,164 ratings with 2K-plus bought in the past month and a #10 rank in Amazon's Men's Sunglasses chart; the listing specifies a 25 g Al-Mg metal rectangular frame with spring-loaded hinges and adjustable silicone nose pads, UV400 lenses measuring 62 mm wide by 42 mm high on a 16 mm bridge with 135 mm temples, and a package that adds a pouch, cleaning cloth and mini screwdriver.",
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
