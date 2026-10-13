# -*- coding: utf-8 -*-
# Reading 分类轮换（2026-10-13）：新增 2 款，替换该分类 added_date 最早的条目
# Usage: python refresh_picks_reading.py
import json, pathlib

ROOT = pathlib.Path(__file__).parent
PICKS = ROOT / 'picks.json'
CAT = 'Reading'
TARGET = 3          # 每分类保持 3 款
TODAY = '2026-10-13'
# 并列处置：Reading 中 B08TLRM5BV(SIGVAN) 与 B0D1XT2LW1(XVXV) 同为 10-07。
# 保留 SIGVAN —— 新入的 B0DHH289R6 与 XVXV 高度同质（均为 $9.99 三件装方形抗眩光），
# SIGVAN 为 5 件装花色女款，页面多样性更强。
RETAIN_ON_TIE = {'B08TLRM5BV'}

NEW = [
    {
        "category": CAT,
        "name": "Reading Glasses 5 Pairs Quality Readers Spring Hinge Glasses for Reading for Men and Women (5BLACK, 2.00)",
        "asin": "B0FQNK79XP",
        "price": 10.19,
        "img_url": "https://m.media-amazon.com/images/I/61tDbKnD7UL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B0FQNK79XP?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "Five pairs for $10.19 while the current deal runs (list $13.99) - about $2.04 a pair - an Amazon's Choice pick rated 4.6 stars from 1,677 ratings with 1K+ bought in the past month; the listing includes five soft pouches and a cleaning cloth, with spring-hinge temples and powers from 0.5X to 6.0X.",
        "added_date": TODAY,
        "img_ok": None,
        "link_ok": None,
        "last_checked": "",
    },
    {
        "category": CAT,
        "name": "Reading Glasses for Women Men - Blue Light Blocking Magnifying Readers,Square Anti-Glare Computer Eyeglasses",
        "asin": "B0DHH289R6",
        "price": 9.99,
        "img_url": "https://m.media-amazon.com/images/I/71m2Dfj4MxL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B0DHH289R6?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "Three anti-glare readers for $9.99 (list $11.99) - about $3.33 each - rated 4.4 stars from 2,451 ratings and ranked #8 in Amazon's Reading Glasses chart; the listing describes square lenses the brand says filter blue light for close-up screen work, a 49 mm lens width, a 16 mm bridge and a unisex fit, sold across a range of powers.",
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
