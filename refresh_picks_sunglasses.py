# -*- coding: utf-8 -*-
# Sunglasses 分类轮换（2026-10-09）：新增 2 款，替换该分类 added_date 最早的条目
# Usage: python refresh_picks_sunglasses.py
import json, pathlib

ROOT = pathlib.Path(__file__).parent
PICKS = ROOT / 'picks.json'
CAT = 'Sunglasses'
TARGET = 3          # 每分类保持 3 款
TODAY = '2026-10-09'
# added_date 并列时的处置规则：本集合中的 ASIN 并列时后置（优先保留）。
# 现有两条 10-03：B09NVX1CK3(KastKing Huzzah) 与 B07PBLGCGZ(mxnx aviator) 并列。
# 保留 KastKing：类目 #3 畅销 + Amazon's Choice + 运动包裹款式；
# 且本轮新增的 Luenx 已是男式方框飞行员款，保留 mxnx 会使两副款式重叠。
RETAIN_ON_TIE = {'B09NVX1CK3'}

NEW = [
    {
        "category": CAT,
        "name": "Luenx Aviator Polarized Sunglasses for Men: Square UV400 Driving",
        "asin": "B07Z8Q3GV9",
        "price": 16.99,
        "img_url": "https://m.media-amazon.com/images/I/71E5WD1ok9L._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B07Z8Q3GV9?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "A square-aviator frame at $16.99 that ranks #4 in Amazon's Men's Sunglasses chart - 4.5 stars from 8,471 ratings with 5K+ bought in the past month; the listing specifies a 61 mm metal frame with polarized TAC (tri-acetate cellulose) lenses and UV400 protection, and the box adds a soft pouch, cloth, gift carton and a polarized test card.",
        "added_date": TODAY,
        "img_ok": None,
        "link_ok": None,
        "last_checked": "",
    },
    {
        "category": CAT,
        "name": "CARFIA Polarized Men's Sunglasses UV400 Protection Cool Man Shades CA5354",
        "asin": "B07JKG6QB6",
        "price": 49.0,
        "img_url": "https://m.media-amazon.com/images/I/51OXExfjMRS._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B07JKG6QB6?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "The premium pick at $49.00: 4.6 stars from 4,812 ratings with 1K+ bought in the past month, ranked #88 in Amazon's Men's Sunglasses chart; the listing describes handcrafted hypoallergenic acetate frames it says never fade, shatterproof polarized lenses with UV400 protection, anti-glare coating and a leather case in the box.",
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
