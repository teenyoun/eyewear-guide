#!/usr/bin/env python3
"""
Daily Maintenance Script for EyewearGuide
===========================================
Runs daily to:
  1. Check content queue for new articles → generate HTML
  2. Rebuild sitemap & homepage
  3. Validate internal links
  4. Git commit & push to deploy

Usage: python daily.py
       python daily.py --dry-run   (preview without making changes)
"""

import json, os, re, sys
from datetime import datetime
from pathlib import Path
import subprocess

BASE_DIR = Path(__file__).parent
ARTICLES_DIR = BASE_DIR / "articles"
QUEUE_FILE = BASE_DIR / "content-queue.json"
LOG_FILE = BASE_DIR / "daily-log.txt"
CONFIG_FILE = BASE_DIR / "config.json"
SITEMAP_FILE = BASE_DIR / "sitemap.xml"
HOMEPAGE_FILE = BASE_DIR / "index.html"

DRY_RUN = "--dry-run" in sys.argv
TAG = "eyewearguide-20"
SITE_URL = "https://glasses.teenyoun.com"

# HTML article template with SEO best practices
ARTICLE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | EyewearGuide</title>
<meta name="description" content="{meta_desc}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{meta_desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<link rel="stylesheet" href="../css/style.css">
</head>
<body>
<header class="site-header">
  <div class="header-inner">
    <a href="../index.html" class="site-title">Eyewear<span>Guide</span></a>
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
</article>
</main>
<footer class="site-footer">
  <p>&copy; {year} EyewearGuide. All rights reserved.</p>
  <p class="disclaimer">As an Amazon Associate, we earn from qualifying purchases. We only recommend products we have tested and believe in.</p>
</footer>
</body>
</html>
"""


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower().strip(" -"))


def load_queue():
    if not QUEUE_FILE.exists():
        return []
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else data.get("articles", [])


def save_queue(queue):
    if not DRY_RUN:
        with open(QUEUE_FILE, "w", encoding="utf-8") as f:
            json.dump(queue, f, indent=2, ensure_ascii=False)


def generate_article(article):
    """Generate a single article HTML file."""
    now = datetime.now()
    filename = slugify(article["title"]) + ".html"
    filepath = ARTICLES_DIR / filename

    # Insert Amazon affiliate links into body
    body = article.get("body_html", "")
    body = body.replace("{TAG}", TAG)

    # Auto-link product mentions to Amazon search
    product_pattern = re.compile(r'\[\[AMAZON:(.+?)(?::(.+?))?\]\]')
    body = product_pattern.sub(
        lambda m: f'<a href="https://www.amazon.com/s?k={m.group(1).replace(" ", "+")}&tag={TAG}" rel="nofollow sponsored">{m.group(2) or m.group(1)}</a>',
        body
    )

    # Add internal links section based on category
    internal_links = get_internal_links(article.get("category", ""), article.get("title", ""))

    html = ARTICLE_HTML.format(
        title=article["title"],
        meta_desc=article.get("meta_description", article["title"]),
        canonical=f"{SITE_URL}/articles/{filename}",
        category=article.get("category", "Eyewear"),
        date_str=now.strftime("%B %d, %Y"),
        read_time=article.get("read_time", "6 min read"),
        body_html=body + internal_links,
        year=now.year,
    )

    if not DRY_RUN:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

    return filename


def get_internal_links(category, current_title):
    """Return contextual internal links based on article category."""
    links = {
        "Blue Light Glasses": [
            ("best-blue-light-glasses.html", "Best Blue Light Glasses of 2026"),
            ("do-blue-light-glasses-work.html", "Do Blue Light Glasses Really Work?"),
            ("blue-light-glasses-vs-anti-glare.html", "Blue Light vs Anti-Glare"),
        ],
        "Reading Glasses": [
            ("best-reading-glasses-men.html", "Best Reading Glasses for Men"),
            ("best-reading-glasses-women.html", "Best Reading Glasses for Women"),
            ("reading-glasses-strength-guide.html", "Reading Glasses Strength Guide"),
        ],
        "Prescription Glasses": [
            ("best-online-glasses-stores.html", "Best Online Glasses Stores"),
            ("cheap-prescription-glasses-online.html", "Cheap Prescription Glasses Online"),
        ],
        "Sunglasses": [
            ("best-sunglasses-for-driving.html", "Best Sunglasses for Driving"),
        ],
        "Kids Eyewear": [
            ("kids-glasses-buying-guide.html", "Kids Glasses Buying Guide"),
        ],
        "Glasses Care": [
            ("how-to-clean-glasses-properly-avoid-scratches-and-damage.html", "How to Clean Glasses Properly"),
            ("best-anti-fog-glasses-for-mask-wearers-2026.html", "Best Anti-Fog Glasses"),
        ],
    }

    cat_links = links.get(category, [])
    # Filter out self-link
    cat_links = [(url, label) for url, label in cat_links if label not in current_title]

    if not cat_links:
        # Default related links
        cat_links = [
            ("best-blue-light-glasses.html", "Best Blue Light Glasses"),
            ("best-online-glasses-stores.html", "Best Online Glasses Stores"),
        ]

    html = '\n<div class="info-box">\n<strong>Related Guides:</strong>\n<ul>\n'
    for url, label in cat_links[:3]:
        html += f'  <li><a href="{url}">{label}</a></li>\n'
    html += '</ul>\n</div>\n'
    return html


def rebuild_sitemap(articles):
    """Regenerate sitemap.xml with all articles."""
    urls = [f'<url><loc>{SITE_URL}/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>']
    for art in articles:
        priority = "0.9" if "best" in art["filename"].lower() else "0.7"
        urls.append(
            f'<url><loc>{SITE_URL}/articles/{art["filename"]}</loc>'
            f'<changefreq>monthly</changefreq><priority>{priority}</priority></url>'
        )
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += "\n".join(urls) + "\n</urlset>\n"
    if not DRY_RUN:
        with open(SITEMAP_FILE, "w", encoding="utf-8") as f:
            f.write(xml)
    return len(urls) - 1


def rebuild_homepage(articles):
    """Regenerate index.html with latest articles."""
    cards = []
    for art in articles[:15]:
        cards.append(
            f'    <a href="articles/{art["filename"]}" class="article-card">\n'
            f'      <div>\n        <h3>{art["title"]}</h3>\n'
            f'        <p class="excerpt">{art.get("description", "")[:120]}...</p>\n'
            f'      </div>\n    </a>'
        )

    now = datetime.now()
    html = f"""<!DOCTYPE html>
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
    <p>Expert reviews and honest buying guides to help you choose the best eyewear — updated {now.strftime('%B %Y')}.</p>
  </section>
  <h2 style="margin-bottom:16px;">Latest Guides & Reviews</h2>
  <div class="article-list">
{chr(10).join(cards)}
  </div>
</main>
<footer class="site-footer">
  <p>&copy; {now.year} EyewearGuide. All rights reserved.</p>
  <p class="disclaimer">As an Amazon Associate, we earn from qualifying purchases. This site is reader-supported.</p>
  <p><a href="sitemap.xml">Sitemap</a></p>
</footer>
</body>
</html>"""
    if not DRY_RUN:
        with open(HOMEPAGE_FILE, "w", encoding="utf-8") as f:
            f.write(html)


def scan_articles():
    """Scan for all existing article HTML files."""
    articles = []
    if ARTICLES_DIR.exists():
        for f in sorted(ARTICLES_DIR.glob("*.html"), key=lambda x: x.stat().st_mtime, reverse=True):
            content = f.read_text(encoding="utf-8")
            title_m = re.search(r'<title>(.*?)(?:\s*\|\s*EyewearGuide)?</title>', content)
            desc_m = re.search(r'<meta name="description" content="(.*?)"', content)
            articles.append({
                "filename": f.name,
                "title": title_m.group(1) if title_m else f.stem.replace("-", " ").title(),
                "description": desc_m.group(1) if desc_m else "",
            })
    return articles


def validate_links(articles):
    """Check for broken internal links."""
    valid_files = {a["filename"] for a in articles}
    broken = []
    for art in articles:
        filepath = ARTICLES_DIR / art["filename"]
        content = filepath.read_text(encoding="utf-8")
        hrefs = re.findall(r'href="([^"]+)"', content)
        for href in hrefs:
            if href.endswith(".html") and not href.startswith("http") and not href.startswith(".."):
                if href not in valid_files:
                    broken.append(f"  BROKEN: {art['filename']} → {href}")
    return broken


def git_commit_push(message):
    """Commit and push changes."""
    if DRY_RUN:
        log(f"[DRY RUN] Would commit: {message}")
        return True
    try:
        subprocess.run(["git", "add", "-A"], cwd=BASE_DIR, check=True, capture_output=True)
        result = subprocess.run(["git", "commit", "-m", message], cwd=BASE_DIR, capture_output=True, text=True)
        if "nothing to commit" in result.stdout + result.stderr:
            log("No changes to commit.")
            return True
        subprocess.run(["git", "push"], cwd=BASE_DIR, check=True, capture_output=True)
        log("Pushed to GitHub.")
        return True
    except subprocess.CalledProcessError as e:
        log(f"Git error: {e.stderr}")
        return False


def main():
    log("=" * 50)
    log("Daily maintenance starting...")

    # 1. Process content queue — publish 1 article per day max
    queue = load_queue()
    pending = [a for a in queue if a.get("status") == "pending"]
    new_articles = []

    if pending:
        log(f"Found {len(pending)} pending article(s) in queue. Publishing 1 today.")
        article = pending[0]  # FIFO: first in, first out
        try:
            filename = generate_article(article)
            log(f"  Published: {filename}")
            new_articles.append(filename)
            article["status"] = "published"
            article["filename"] = filename
            article["published_date"] = datetime.now().strftime("%Y-%m-%d")
        except Exception as e:
            log(f"  FAILED: {article.get('title', 'Unknown')} - {e}")
            article["status"] = "failed"
        save_queue(queue)
    else:
        log("No pending articles in queue.")

    # 2. Rebuild sitemap & homepage
    all_articles = scan_articles()
    sitemap_count = rebuild_sitemap(all_articles)
    rebuild_homepage(all_articles)
    log(f"Sitemap rebuilt ({sitemap_count} URLs). Homepage refreshed ({len(all_articles)} articles).")

    # 3. SEO health check
    broken = validate_links(all_articles)
    if broken:
        log(f"WARNING: {len(broken)} broken internal link(s) found:")
        for b in broken:
            log(b)
    else:
        log("SEO check: All internal links OK.")

    # 4. Git push if changes
    commit_msg = f"Daily update: {datetime.now().strftime('%Y-%m-%d')}"
    if new_articles:
        commit_msg = f"New article(s): " + ", ".join(new_articles[:3])

    git_commit_push(commit_msg)
    log(f"Maintenance complete. {len(new_articles)} new articles published.")
    log("=" * 50)


if __name__ == "__main__":
    main()
