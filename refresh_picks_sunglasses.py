# -*- coding: utf-8 -*-
# Sunglasses 分类轮换（2026-10-15）：新增 2 款，替换该分类 added_date 最早的条目
# Usage: python refresh_picks_sunglasses.py
import json, pathlib

ROOT = pathlib.Path(__file__).parent
PICKS = ROOT / 'picks.json'
CAT = 'Sunglasses'
TARGET = 3          # 每分类保持 3 款
TODAY = '2026-10-15'
# added_date 并列时的处置规则：本集合中的 ASIN 并列时后置（优先保留）。
# 本轮入选后集合为 B09NVX1CK3(10-03) 与并列的两条 10-09：
#   B07Z8Q3GV9(Luenx aviator) / B07JKG6QB6(CARFIA CA5354)。
# 保留 B07Z8Q3GV9：类目 #4 畅销、8,471 评分、5K+/月购买量，强于 #88 / 1K+ 的 CARFIA。
RETAIN_ON_TIE = {'B07Z8Q3GV9'}

NEW = [
    {
        "category": CAT,
        "name": "FEIDUSUN Sunglasses Men Polarized Sunglasses for Mens and Womens,Black Retro Sun Glasses Driving Fishing UV Protection",
        "asin": "B0BKSKCYX7",
        "price": 9.99,
        "img_url": "https://m.media-amazon.com/images/I/51ABDkq99LL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B0BKSKCYX7?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "A $9.99 deal pick (list $15.99) holding the #1 Best Seller slot in Amazon's Men's Sunglasses chart - 4.4 stars from 5,024 ratings with 10K-plus bought in the past month; the listing credits TAC lenses with UVA/UVB protection plus an anti-glare HD polarized coating it says cuts glare off roads, water and snow, in a retro square matte-black frame it describes as lightweight, flexible and durable.",
        "added_date": TODAY,
        "img_ok": None,
        "link_ok": None,
        "last_checked": "",
    },
    {
        "category": CAT,
        "name": "KALIYADI Polarized Sunglasses for Men and Women Semi-Rimless Frame Driving Sun glasses UV Blocking",
        "asin": "B07MW4R1X3",
        "price": 16.99,
        "img_url": "https://m.media-amazon.com/images/I/61KQXq71FJL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B07MW4R1X3?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "A two-pack for $16.99 (list $17.99) - about $8.50 a pair - rated 4.5 stars from 43,301 ratings with 4K-plus bought in the past month and a #4 rank in Amazon's Men's Sunglasses chart; the listing describes a semi-rimless frame built from ultra-light materials with shatterproof HD polarized lenses for truer colour and less reflected glare, and each pair ships with its own microfiber pouch and cleaning cloth.",
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

    pos = {id(p): i for i, p in enumerate(data)}   # 列表原始位置，用于 added_date 并列时的稳定排序
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

    print(f'picks.json total={before} -> {len(out)} | added={len(new_items)} | dropped={len(drop)}')
    for n in new_items:
        print('  + ', CAT, '|', n['asin'], '| $', n['price'], '|', n['name'][:50])
    for d in drop:
        print('  - ', d.get('category'), '|', d.get('asin'), '| added', d.get('added_date'), '|', d.get('name', '')[:50])
    if skipped:
        print('  skipped (ASIN already present):', ', '.join(skipped))
    for c in ('Blue Light', 'Reading', 'Sunglasses'):
        items = [p for p in out if p.get('category') == c]
        print(f'  [{c}] {len(items)}: ' + ', '.join(f"{p['asin']}({p.get('added_date')})" for p in items))


if __name__ == '__main__':
    main()
