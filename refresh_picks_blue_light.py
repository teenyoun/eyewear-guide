# -*- coding: utf-8 -*-
# Blue Light 分类轮换（2026-10-11）：新增 2 款，替换该分类 added_date 最早的条目
# Usage: python refresh_picks_blue_light.py
import json, pathlib

ROOT = pathlib.Path(__file__).parent
PICKS = ROOT / 'picks.json'
CAT = 'Blue Light'
TARGET = 3          # 每分类保持 3 款
TODAY = '2026-10-11'
# added_date 并列时的处置规则：本集合中的 ASIN 并列时后置（优先保留）。
# 现有两条 10-05 并列：B07W781XWF(livho) 与 B08NC6Y832(MIGSIR 6 件套)。
# 保留 livho：Computer Blue Light Blocking 类目 #1 畅销、120,157 评分、单品装；
# 且本轮新增的 MEETSUN 已是 3 件套，若再留 MIGSIR 6 件套会出现两款多件套。
RETAIN_ON_TIE = {'B07W781XWF'}

NEW = [
    {
        "category": CAT,
        "name": "MEETSUN Blue Light Blocking Glasses, Anti Eye Strain Headache (Sleep Better),Computer Reading Glasses UV400 Transparent Lens (Black+Leopard+Tortoise, 53)",
        "asin": "B087THJC2C",
        "price": 14.98,
        "img_url": "https://m.media-amazon.com/images/I/71elCVUx43L._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B087THJC2C?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "A three-pack for $14.98 - about $4.99 a pair - rated 4.4 stars from 46,844 ratings with 500-plus bought in the past month and a #83 rank in Amazon's Computer Blue Light Blocking Glasses chart; the listing describes clear UV400 transparent lenses the brand says block harsh blue light, a lightweight non-prescription unisex frame, and colourways in black, leopard and tortoise.",
        "added_date": TODAY,
        "img_ok": None,
        "link_ok": None,
        "last_checked": "",
    },
    {
        "category": CAT,
        "name": "ANYLUV Blue Light Blocking Glasses Men Computer Gaming Glasses Lightweight Al-Mg Metal Anti Eyestrain Eye Protection",
        "asin": "B07RGHSMGF",
        "price": 21.99,
        "img_url": "https://m.media-amazon.com/images/I/71bJg5w-gAL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B07RGHSMGF?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "An Amazon's Choice single pair at $21.99, rated 4.4 stars from 14,669 ratings with 2K-plus bought in the past month and a #26 rank in Amazon's Computer Blue Light Blocking Glasses chart; the listing specifies a lightweight aluminium-magnesium (Al-Mg) metal frame with polycarbonate lenses aimed at computer and gaming use.",
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
