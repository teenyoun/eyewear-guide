# -*- coding: utf-8 -*-
# Blue Light 分类轮换（2026-10-17）：新增 2 款，替换该分类 added_date 最早的条目
# Usage: python refresh_picks_blue_light.py
import json, pathlib

ROOT = pathlib.Path(__file__).parent
PICKS = ROOT / 'picks.json'
CAT = 'Blue Light'
TARGET = 3          # 每分类保持 3 款
TODAY = '2026-10-17'
# added_date 并列时的处置规则：本集合中的 ASIN 并列时后置（优先保留）。
# 现有集合：B07W781XWF(livho,10-05) 最早，必drop；
# 10-11 并列两条 = B087THJC2C(MEETSUN 3 件套, 46,844 评分, 类别#83, 月销500+)
#                     与 B07RGHSMGF(ANYLUV 单品, Amazon's Choice, 14,669 评分, 类别#26, 月销2K+)。
# 保留 ANYLUV：当前需求信号更强（Amazon's Choice、类别排名 #26 优于 #83、月销 2K+ 优于 500+），
# 且为单品装（沿用上轮"并列时保留信号更强的单品装"判例）。
RETAIN_ON_TIE = {'B07RGHSMGF'}

NEW = [
    {
        "category": CAT,
        "name": "Oilway Blue-Light Blocking Glasses Computer Reading/Gaming/TV/Phones Glasses Fashion Anti Eyestrain Glasses for Women Men",
        "asin": "B0B2R4NR2F",
        "price": 8.99,
        "img_url": "https://m.media-amazon.com/images/I/61dmpT4OwnL._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B0B2R4NR2F?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "An Amazon's Choice single pair at $8.99 while the current 10 percent deal runs (typical price $9.99), rated 4.4 stars from 6,720 ratings with 3K-plus bought in the past month and a #13 rank in Amazon's Computer Blue Light Blocking Glasses chart; the listing describes a square full-rim composite frame with anti-glare polycarbonate lenses, metal hinges, a 52 mm lens width and 14 mm bridge as listed, and a case in the box.",
        "added_date": TODAY,
        "img_ok": None,
        "link_ok": None,
        "last_checked": "",
    },
    {
        "category": CAT,
        "name": "TIJN Blue Light Blocking Glasses for Women Men Square Frame Nerd Eyeglasses Anti Blue Ray Computer Screen Glasses",
        "asin": "B0GYNQZMB6",
        "price": 9.99,
        "img_url": "https://m.media-amazon.com/images/I/51WgPC4u2+L._AC_SL1500_.jpg",
        "link_url": "https://www.amazon.com/dp/B0GYNQZMB6?tag=eyewearguide-20",
        "source": "landingImage-hires",
        "blurb": "An Amazon's Choice single pair at $9.99, rated 4.4 stars from 53,232 ratings with 2K-plus bought in the past month and a #12 rank in Amazon's Computer Blue Light Blocking Glasses chart; the listing describes a square full-rim plastic frame with anti-blue-ray computer screen lenses, an 18 mm bridge and 14 cm temples.",
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
