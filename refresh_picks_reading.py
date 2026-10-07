# -*- coding: utf-8 -*-
# Reading 分类轮换（2026-10-07）：新增 2 款，替换该分类 added_date 最早的条目
# Usage: python refresh_picks_reading.py
import json, pathlib

ROOT = pathlib.Path(__file__).parent
PICKS = ROOT / 'picks.json'
CAT = 'Reading'
TARGET = 3          # 每分类保持 3 款
TODAY = '2026-10-07'
# added_date 并列时的处置规则：本集合中的 ASIN 并列时后置（优先保留）。
# B08CR9GRM1 (CCVOO) = Reading 类目 #2 畅销、4,045 评分、单品装；若删它，本分类将只剩三款多件套。
RETAIN_ON_TIE = {'B08CR9GRM1'}

NEW = [
    {
        "category": CAT,
        "name": "XVXV Reading Glasses for Women Men - Blue Light Blocking Readers Oversize Square Anti Glare with Spring Hinge",
        "asin": "B0D1XT2LW1",
        "price": 9.99,
        "img_url": "https://m.media-amazon.com/images/I/61bHtdJzl0L._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B0D1XT2LW1?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "An Amazon's Choice three-pack of oversize square readers at $9.99 - about $3.33 a pair - rated 4.5 stars from 2,622 ratings and ranked #31 in Reading Glasses, with spring-hinge temples and lenses the listing says filter blue light as well as UV; sold in strengths from 0.0X to 4.0X.",
        "added_date": TODAY,
        "img_ok": None,
        "link_ok": None,
        "last_checked": "",
    },
    {
        "category": CAT,
        "name": "SIGVAN Ladies Reading Glasses Blue Light Blocking Spring Hinge Fashion Pattern Print Eyeglasses for Women",
        "asin": "B08TLRM5BV",
        "price": 14.99,
        "img_url": "https://m.media-amazon.com/images/I/71LDIDUb9QL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B08TLRM5BV?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "Five patterned pairs for $14.99 - about $3.00 each - rated 4.6 stars from 1,573 ratings with 700-plus bought in the past month and a #14 rank in Reading Glasses; the listing describes spring-hinge temples, blue-light-filtering lenses to ease screen strain, and a soft pouch plus microfiber cloth in the box, in strengths from 0.0X to 4.0X.",
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
