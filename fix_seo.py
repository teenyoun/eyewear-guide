"""SEO batch fix: canonical unification, JSON-LD injection, related-guides backfill, robots.txt."""
import os, re, json
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent
ART = BASE / "articles"
DOMAIN = "https://glasses.teenyoun.com"

STOPWORDS = {
    "the","a","an","for","and","or","of","to","in","on","with","best","your","you","how",
    "what","why","vs","2026","glasses","do","are","is","not","guide","top","wear","use","can"
}

def slug_title(fname: str) -> str:
    """Convert slug filename to readable title for link text."""
    t = fname[:-5].replace("-", " ")
    words = t.split()
    keep = [w for w in words if w not in STOPWORDS]
    return " ".join(keep[:4]).title() if keep else t.title()

def extract_title(html: str) -> str:
    m = re.search(r"<title>(.*?)</title>", html, re.S)
    if m:
        t = m.group(1).replace(" | EyewearGuide", "")
        return t.strip()
    return slug_title("")

def extract_desc(html: str) -> str:
    m = re.search(r'<meta name="description" content="([^"]*)"', html)
    return m.group(1) if m else ""

def keyword_related(candidates, current_slug, k=4):
    cur_words = set(re.findall(r"[a-z]+", current_slug[:-5])) - STOPWORDS
    scored = []
    for c in candidates:
        if c == current_slug:
            continue
        cw = set(re.findall(r"[a-z]+", c[:-5])) - STOPWORDS
        score = len(cur_words & cw)
        if score > 0:
            scored.append((score, c))
    scored.sort(key=lambda x: -x[0])
    return [c for _, c in scored[:k]]

files = sorted([f for f in os.listdir(ART) if f.endswith(".html")])
print(f"Articles found: {len(files)}")

fixed_canonical, added_jsonld, added_related = 0, 0, 0

for fname in files:
    path = ART / fname
    html = path.read_text(encoding="utf-8", errors="replace")
    url = f"{DOMAIN}/articles/{fname}"
    orig = html

    # --- 1. Canonical: remove any existing, insert correct one right after description meta ---
    html = re.sub(r'<link rel="canonical"[^>]*>\s*', "", html)
    canon_tag = f'<link rel="canonical" href="{url}">\n'
    if '<link rel="canonical"' not in orig:
        html = html.replace('<meta name="robots" content="index, follow">',
                            '<meta name="robots" content="index, follow">\n' + canon_tag, 1)
        fixed_canonical += 1
    else:
        # was present but wrong (old domain) -> we already removed it; re-insert
        html = html.replace('<meta name="robots" content="index, follow">',
                            '<meta name="robots" content="index, follow">\n' + canon_tag, 1)
        if "teenyoun.github.io" in orig:
            fixed_canonical += 1

    # --- 2. JSON-LD Article schema (skip if already present) ---
    if "application/ld+json" not in html:
        title = extract_title(orig)
        desc = extract_desc(orig)
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d")
        ld = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "description": desc,
            "mainEntityOfPage": url,
            "datePublished": mtime,
            "dateModified": mtime,
            "author": {"@type": "Organization", "name": "EyewearGuide"},
            "publisher": {
                "@type": "Organization",
                "name": "EyewearGuide",
                "logo": {"@type": "ImageObject", "url": f"{DOMAIN}/logo.png"},
            },
        }
        block = '<script type="application/ld+json">\n' + json.dumps(ld, ensure_ascii=False, indent=2) + '\n</script>\n</head>'
        html = html.replace("</head>", block, 1)
        added_jsonld += 1

    # --- 3. Related Guides backfill (only if missing) ---
    if "Related Guides" not in html:
        rel = keyword_related(files, fname)
        if rel:
            lis = "\n".join(f'  <li><a href="{r}">{extract_title((ART / r).read_text(encoding="utf-8", errors="replace"))}</a></li>' for r in rel)
            block = ('<div class="info-box">\n<strong>Related Guides:</strong>\n<ul>\n'
                     + lis + '\n</ul>\n</div>\n\n</article>')
            html = html.replace("</article>", block, 1)
            added_related += 1

    if html != orig:
        path.write_text(html, encoding="utf-8")
        print(f"  updated: {fname}")

# --- 4. robots.txt ---
robots = "User-agent: *\nAllow: /\nSitemap: " + DOMAIN + "/sitemap.xml\n"
(BASE / "robots.txt").write_text(robots, encoding="utf-8")

print(f"\nDone: canonical fixed/added={fixed_canonical}, JSON-LD added={added_jsonld}, related backfilled={added_related}")
