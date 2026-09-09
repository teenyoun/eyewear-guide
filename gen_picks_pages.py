# 生成分类精选页：从 picks.json 渲染 picks-{category}.html（大图卡片）
# Usage: python gen_picks_pages.py
import json, pathlib, re, datetime
from html import escape

ROOT = pathlib.Path(__file__).parent
PICKS = ROOT / 'picks.json'
OUT_DIR = ROOT  # pages live at site root (not in articles/ to keep them out of article lists)

CATEGORY_META = {
    'Blue Light': {
        'title': 'Blue Light Glasses Picks',
        'h1': 'Best Blue Light Glasses - Editor Picks',
        'intro': (
            '<p>Screen time is not going anywhere, and neither is the eye strain that comes with it. '
            'Blue light glasses filter the high-energy wavelengths emitted by monitors, phones and TVs '
            'that can disrupt sleep and tire the eyes during long sessions. The picks below are chosen '
            'for real, measurable filter strength - not just a marketing tint - plus frame comfort for '
            'all-day wear and honest value at their price point.</p>'
            '<p>Wondering whether you actually need them? Read our evidence-based take on '
            '<a href="articles/do-blue-light-glasses-work.html">do blue light glasses really work</a>, '
            'then compare lens options in our '
            '<a href="articles/anti-reflective-coating-vs-blue-light-filter-worth-paying-for-both-.html">AR vs blue-light filter guide</a>.</p>'
        ),
        'related': [
            ('articles/do-blue-light-glasses-work.html', 'Do Blue Light Glasses Really Work?'),
            ('articles/best-blue-light-glasses.html', 'Best Blue Light Glasses of 2026'),
            ('articles/blue-light-glasses-for-gaming-2026-do-gamers-actually-need-them-.html', 'Blue Light Glasses for Gaming'),
            ('articles/best-blue-light-glasses-for-kids-screen-protection-for-young-eyes-2026.html', 'Kids & Screens: Blue Light Guide'),
        ],
    },
    'Reading': {
        'title': 'Reading Glasses Picks',
        'h1': 'Best Reading Glasses - Editor Picks',
        'intro': (
            '<p>Reading glasses are the one purchase most people make wrong: they grab whatever is on '
            'the rack and end up with a pair that blurs at their working distance or slides down the nose '
            'all day. The right strength comes from a simple test, not a guess - hold a book at your '
            'normal reading distance and find the power that makes it crisp. The picks below are '
            'multi-pack value buys and comfort-first frames that survive the desk drawer, the car and '
            'the couch.</p>'
            '<p>Not sure what strength you need? Start with our '
            '<a href="articles/reading-glasses-strength-guide.html">reading glasses strength guide</a> '
            'and check our comparison of '
            '<a href="articles/computer-glasses-vs-reading-glasses-what-s-the-difference-.html">computer vs reading glasses</a>.</p>'
        ),
        'related': [
            ('articles/reading-glasses-strength-guide.html', 'Reading Glasses Strength Guide'),
            ('articles/best-reading-glasses-men.html', 'Best Reading Glasses for Men'),
            ('articles/best-reading-glasses-women.html', 'Best Reading Glasses for Women'),
            ('articles/how-to-measure-pupillary-distance-at-home-3-easy-methods.html', 'How to Measure PD at Home'),
        ],
    },
    'Sunglasses': {
        'title': 'Sunglasses Picks',
        'h1': 'Best Sunglasses - Editor Picks',
        'intro': (
            '<p>A good pair of sunglasses is the cheapest health insurance you will ever buy: UV400 '
            'lenses block 99-100% of UVA/UVB and protect the eyes from cumulative damage linked to '
            'cataracts and macular degeneration. Beyond protection, lens tint and polarization decide '
            'how well you actually see - polarized lenses cut glare off water, roads and snow, while '
            'brown and amber tints boost contrast on green courses and trails.</p>'
            '<p>Learn the difference between lens claims in our '
            '<a href="articles/polarized-vs-uv400-what-s-the-difference-and-do-you-need-both-.html">polarized vs UV400 explainer</a> '
            'and find the right frame for the driver in your family with our '
            '<a href="articles/best-sunglasses-for-driving.html">driving sunglasses guide</a>.</p>'
        ),
        'related': [
            ('articles/best-sunglasses-for-driving.html', 'Best Sunglasses for Driving'),
            ('articles/polarized-vs-uv400-what-s-the-difference-and-do-you-need-both-.html', 'Polarized vs UV400 Explained'),
            ('articles/best-golf-sunglasses-2026-see-the-ball-read-the-green.html', 'Best Golf Sunglasses'),
            ('articles/best-sports-sunglasses-for-running-stay-cool-and-see-clearly.html', 'Sport Sunglasses for Running'),
        ],
    },
}

# shared header/footer (mirrors index.html style)
def page_shell(title, h1, nav_links, body_inner, year):
    nav = ''.join(f'      <a href="{u}">{t}</a>\n' for u, t in nav_links)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(title)} | EyewearGuide</title>
<meta name="description" content="{escape(h1)} - hand-picked eyewear tested for quality, comfort and value.">
<meta name="robots" content="index, follow">
<link rel="stylesheet" href="css/style.css">
</head>
<body>
<header class="site-header">
  <div class="header-inner">
    <a href="index.html" class="site-title">Eyewear<span>Guide</span></a>
    <nav class="site-nav">
{nav}    </nav>
  </div>
</header>
<main>
{body_inner}
</main>
<footer class="site-footer">
  <p>&copy; {year} EyewearGuide. All rights reserved.</p>
  <p class="disclaimer">As an Amazon Associate we earn from qualifying purchases. We only recommend products we have tested and believe in.</p>
  <p><a href="sitemap.xml">Sitemap</a></p>
</footer>
</body>
</html>
"""

NAV = [
    ('index.html', 'Home'),
    ('picks-blue-light.html', 'Blue Light Picks'),
    ('picks-reading.html', 'Reading Picks'),
    ('picks-sunglasses.html', 'Sunglass Picks'),
]

def slug(cat):
    return re.sub(r'[^a-z0-9]+', '-', cat.lower()).strip('-')

def render_pick_card(p):
    price = f'<span class="pick-price">${p.get("price", "")}</span>' if p.get('price') else ''
    return f"""      <div class="pick-page-card">
        <img src="{escape(p.get('img_url', ''))}" alt="{escape(p.get('name', ''))}" loading="lazy">
        <div class="pick-page-info">
          <h3>{escape(p.get('name', ''))}</h3>
          <p>{escape(p.get('blurb', ''))}</p>
          <p class="pick-meta">{price} &middot; <a href="{escape(p.get('link_url', ''))}" rel="nofollow sponsored" target="_blank">Check Price on Amazon &rarr;</a></p>
        </div>
      </div>
"""

def build_page(category):
    meta = CATEGORY_META.get(category)
    if not meta:
        return None
    picks = [p for p in load_picks() if p.get('category', '') == category]
    cards = ''.join(render_pick_card(p) for p in picks)
    related = ''.join(
        f'      <li><a href="{escape(u)}">{escape(t)}</a></li>\n' for u, t in meta['related']
    )
    body = f"""  <section class="hero">
    <h1>{escape(meta['h1'])}</h1>
    <p>Hand-picked and hand-tested - updated {datetime.date.today().strftime('%B %Y')}.</p>
  </section>
  <section class="pick-intro">
{meta['intro']}
  </section>
  <section class="editor-picks">
    <h2>This Season's Picks</h2>
    <div class="pick-page-list">
{cards}    </div>
  </section>
  <section class="editor-picks">
    <h2>Related Buying Guides</h2>
    <ul class="related-list">
{related}    </ul>
  </section>
"""
    return page_shell(meta['title'], meta['h1'], NAV, body, datetime.date.today().year)

def load_picks():
    if not PICKS.exists():
        return []
    try:
        data = json.loads(PICKS.read_text(encoding='utf-8'))
        return data if isinstance(data, list) else []
    except Exception:
        return []

def main():
    cats = {p.get('category') for p in load_picks() if p.get('category')}
    written = []
    for cat in sorted(cats):
        html = build_page(cat)
        if html:
            fn = f'picks-{slug(cat)}.html'
            (OUT_DIR / fn).write_text(html, encoding='utf-8')
            written.append(fn)
            print('generated:', fn, '| picks:', sum(1 for p in load_picks() if p.get('category') == cat))
    if not written:
        print('NO_CATEGORIES (picks.json empty or missing categories)')

if __name__ == '__main__':
    main()
