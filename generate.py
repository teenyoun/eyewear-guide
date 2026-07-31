#!/usr/bin/env python3
"""
EyewearGuide Content Automation Script
========================================
Generates new articles from a content pipeline JSON file,
inserts affiliate links, updates sitemap and homepage.

Usage:
  python generate.py articles.json          # Generate articles from JSON
  python generate.py --sitemap-only         # Only rebuild sitemap + homepage
  python generate.py --config config.json   # Set affiliate tags and domain
"""

import json, os, sys, re
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
ARTICLES_DIR = BASE_DIR / "articles"
DEFAULT_CONFIG = {
    "domain": "https://YOUR-DOMAIN.com",
    "amazon_tag": "YOUR-TAG-20",
    "amazon_affiliate_base": "https://www.amazon.com/dp/",
    "site_name": "EyewearGuide",
    "affiliate_disclosure": (
        "As an Amazon Associate, we earn from qualifying purchases. "
        "We only recommend products we have tested and believe in."
    ),
}

# Article HTML template
ARTICLE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | {site_name}</title>
<meta name="description" content="{meta_description}">
<link rel="stylesheet" href="../css/style.css">
</head>
<body>
<header class="site-header">
  <div class="header-inner">
    <a href="../index.html" class="site-title">{site_name_span}</a>
    <nav class="site-nav">
      <a href="../index.html">Home</a>
      <a href="best-blue-light-glasses.html">Blue Light</a>
      <a href="best-reading-glasses-men.html">Reading</a>
      <a href="best-online-glasses-stores.html">Prescription</a>
    </nav>
  </div>
</header>
<main>
<nav class="breadcrumb"><a href="../index.html">Home</a> &rsaquo; <strong>{category}</strong></nav>
<article>
<h1>{title}</h1>
<p class="byline">{date_str} &middot; {read_time}</p>
{body_html}
{affiliate_section}
</article>
</main>
<footer class="site-footer">
  <p>&copy; {year} {site_name}. All rights reserved.</p>
  <p class="disclaimer">{affiliate_disclosure}</p>
</footer>
</body>
</html>
"""

AFFILIATE_LINK_TEMPLATE = '<a href="{base}{asin}?tag={tag}" class="btn btn-cta" rel="nofollow sponsored" target="_blank">{label}</a>'


def load_config(config_path=None):
    cfg = DEFAULT_CONFIG.copy()
    if config_path and os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            cfg.update(json.load(f))
    return cfg


def generate_amazon_link(asin, label="Check Price on Amazon", cfg=None):
    cfg = cfg or DEFAULT_CONFIG
    return AFFILIATE_LINK_TEMPLATE.format(
        base=cfg["amazon_affiliate_base"],
        asin=asin,
        tag=cfg["amazon_tag"],
        label=label,
    )


def make_site_name_span(cfg):
    name = cfg["site_name"]
    # Split at uppercase for styling: "EyewearGuide" -> "Eyewear<span>Guide</span>"
    parts = re.split(r'(?=[A-Z][a-z])', name)
    if len(parts) >= 2:
        return f'{parts[0]}<span>{"".join(parts[1:])}</span>'
    return name


def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower().strip(" -"))


def generate_article(article_data, cfg):
    """Generate a single article HTML file from article data dict."""
    required = ["title", "meta_description", "category", "body_html"]
    for key in required:
        if key not in article_data:
            raise ValueError(f"Missing required field: {key}")

    now = datetime.now()
    date_str = article_data.get("date", now.strftime("%B %d, %Y"))
    read_time = article_data.get("read_time", "6 min read")
    body_html = article_data["body_html"]

    # Auto-insert affiliate links for any ASIN references in body
    # Pattern: <!--AFFILIATE:ASIN:Label--> or [AFFILIATE:ASIN]
    body_html = re.sub(
        r'<!--AFFILIATE:([A-Z0-9]{10})(?::([^>]*?))?-->',
        lambda m: generate_amazon_link(m.group(1), m.group(2) or "Check Price on Amazon", cfg),
        body_html
    )

    # Add affiliate CTA section if not already present
    affiliate_section = ""
    if "<!--NO_AFFILIATE_SECTION-->" not in body_html:
        affiliate_section = f'\n<p style="margin-top:32px;"><a href="#" class="btn btn-cta" rel="nofollow">Browse Related Products on Amazon</a></p>\n'

    html = ARTICLE_TEMPLATE.format(
        title=article_data["title"],
        site_name=cfg["site_name"],
        site_name_span=make_site_name_span(cfg),
        meta_description=article_data["meta_description"],
        category=article_data["category"],
        date_str=date_str,
        read_time=read_time,
        body_html=body_html,
        affiliate_section=affiliate_section,
        year=now.year,
        affiliate_disclosure=cfg["affiliate_disclosure"],
    )

    filename = slugify(article_data["title"]) + ".html"
    filepath = ARTICLES_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  Generated: articles/{filename}")
    return filename


def scan_existing_articles():
    """Scan articles directory for existing HTML files."""
    articles = []
    if ARTICLES_DIR.exists():
        for f in sorted(ARTICLES_DIR.glob("*.html")):
            # Extract title from <title> tag
            content = f.read_text(encoding="utf-8")
            title_match = re.search(r'<title>(.*?)(?:\s*\|\s*EyewearGuide)?</title>', content)
            desc_match = re.search(r'<meta name="description" content="(.*?)"', content)
            title = title_match.group(1) if title_match else f.stem.replace("-", " ").title()
            desc = desc_match.group(1) if desc_match else ""
            articles.append({
                "filename": f.name,
                "title": title,
                "description": desc,
            })
    return articles


def rebuild_homepage(articles, cfg):
    """Rebuild index.html with updated article list."""
    article_cards = []
    for i, art in enumerate(articles[:15]):  # Show latest 15
        card = f"""    <a href="articles/{art['filename']}" class="article-card">
      <div>
        <h3>{art['title']}</h3>
        <p class="excerpt">{art['description'][:120]}...</p>
      </div>
    </a>"""
        article_cards.append(card)

    now = datetime.now()
    homepage = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Eyewear Guide - Expert Reviews & Buying Advice for Glasses</title>
<meta name="description" content="Honest reviews, comparisons, and buying guides for blue light glasses, reading glasses, prescription glasses, and sunglasses.">
<link rel="stylesheet" href="css/style.css">
</head>
<body>
<header class="site-header">
  <div class="header-inner">
    <a href="index.html" class="site-title">Eyewear<span>Guide</span></a>
    <nav class="site-nav">
      <a href="index.html">Home</a>
      <a href="articles/best-blue-light-glasses.html">Blue Light</a>
      <a href="articles/best-reading-glasses-men.html">Reading</a>
      <a href="articles/best-online-glasses-stores.html">Prescription</a>
    </nav>
  </div>
</header>
<main>
  <section class="hero">
    <h1>Find the Perfect Pair of Glasses</h1>
    <p>Expert reviews and honest buying guides to help you choose the best eyewear.</p>
  </section>
  <h2 style="margin-bottom:16px;">Latest Guides & Reviews</h2>
  <div class="article-list">
{chr(10).join(article_cards)}
  </div>
</main>
<footer class="site-footer">
  <p>&copy; {now.year} EyewearGuide. All rights reserved.</p>
  <p class="disclaimer">As an Amazon Associate, we earn from qualifying purchases.</p>
  <p><a href="sitemap.xml">Sitemap</a></p>
</footer>
</body>
</html>"""

    with open(BASE_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(homepage)
    print("  Rebuilt: index.html")


def rebuild_sitemap(articles, cfg):
    """Rebuild sitemap.xml with all articles."""
    urls = []
    urls.append(f'<url><loc>{cfg["domain"]}/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>')

    for art in articles:
        priority = "0.9" if "best" in art["filename"].lower() else "0.7"
        urls.append(
            f'<url><loc>{cfg["domain"]}/articles/{art["filename"]}</loc>'
            f'<changefreq>monthly</changefreq><priority>{priority}</priority></url>'
        )

    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += "\n".join(urls)
    sitemap += "\n</urlset>\n"

    with open(BASE_DIR / "sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap)
    print(f"  Rebuilt: sitemap.xml ({len(articles)} articles)")


def main():
    cfg = load_config()

    if "--config" in sys.argv:
        idx = sys.argv.index("--config")
        if idx + 1 < len(sys.argv):
            cfg = load_config(sys.argv[idx + 1])

    if "--sitemap-only" in sys.argv:
        articles = scan_existing_articles()
        rebuild_sitemap(articles, cfg)
        rebuild_homepage(articles, cfg)
        print(f"\nDone. {len(articles)} articles indexed.")
        return

    # Generate articles from JSON input
    if len(sys.argv) < 2:
        print("Usage: python generate.py articles.json [--config config.json]")
        print("       python generate.py --sitemap-only")
        sys.exit(1)

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    articles_data = data if isinstance(data, list) else data.get("articles", [])
    if not articles_data:
        print("Error: No articles found in input file. Expected a list or {{\"articles\": [...]}}")
        sys.exit(1)

    print(f"Generating {len(articles_data)} article(s)...\n")
    new_files = []
    for art in articles_data:
        filename = generate_article(art, cfg)
        new_files.append(filename)

    # Rebuild homepage and sitemap
    all_articles = scan_existing_articles()
    rebuild_sitemap(all_articles, cfg)
    rebuild_homepage(all_articles, cfg)

    print(f"\nDone. {len(new_files)} new articles created. {len(all_articles)} total.")
    print("Next: Upload all files to your web host, then submit sitemap.xml to Google Search Console.")


if __name__ == "__main__":
    main()
