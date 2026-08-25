#!/usr/bin/env python3
"""EyewearGuide daily health check.
Checks: article count vs queue, sitemap consistency, HTTP availability,
canonical correctness, git/deploy status. Prints structured report.
Exit code 0 = all OK, 1 = at least one ERROR.
"""
import json, re, subprocess, sys, urllib.request
from pathlib import Path

BASE = Path(__file__).parent
DOMAIN = "https://glasses.teenyoun.com"
SITEMAP_URL = DOMAIN + "/sitemap.xml"
CHECK_HTTP_N = 3  # how many articles to HTTP-check

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; EyewearGuideHealthCheck/1.0)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")

results = []  # (level, item, detail)
def ok(item, detail): results.append(("OK", item, detail))
def warn(item, detail): results.append(("WARN", item, detail))
def err(item, detail): results.append(("ERROR", item, detail))

# 1. Local article count vs queue pending
try:
    articles = sorted((BASE / "articles").glob("*.html"))
    a_count = len(articles)
    queue = json.loads((BASE / "content-queue.json").read_text(encoding="utf-8"))
    pending = sum(1 for q in queue if q.get("status") == "pending")
    ok("文章数", f"{a_count} 篇在线, 队列 pending {pending}")
except Exception as e:
    err("文章统计", str(e))
    a_count, pending = -1, -1

# 2. Sitemap fetch + entry consistency
try:
    status, sm = fetch(SITEMAP_URL)
    if status != 200:
        err("sitemap HTTP", f"status {status}")
    else:
        locs = re.findall(r"<loc>(.*?)</loc>", sm)
        sitemap_count = len(locs)
        if sitemap_count != a_count + 1:  # sitemap includes homepage
            warn("sitemap 一致性", f"sitemap {sitemap_count} 条 vs 文章 {a_count} 篇+首页")
        else:
            ok("sitemap", f"{sitemap_count} 条, 与文章数一致")
        bad = [l for l in locs if "glasses.teenyoun.com" not in l]
        if bad:
            err("sitemap 域名", f"{len(bad)} 条非新域名: {bad[:2]}")
except Exception as e:
    err("sitemap 抓取", str(e))

# 3. HTTP check newest articles
try:
    newest = sorted(articles, key=lambda p: p.stat().st_mtime, reverse=True)[:CHECK_HTTP_N]
    for p in newest:
        url = f"{DOMAIN}/articles/{p.name}"
        try:
            st, _ = fetch(url)
            if st == 200:
                ok("页面可访问", f"{p.name} ({st})")
            else:
                err("页面可访问", f"{p.name} HTTP {st}")
        except Exception as e:
            err("页面可访问", f"{p.name} {e}")
except Exception as e:
    err("HTTP 检查", str(e))

# 4. Canonical spot check (3 newest + 3 oldest)
try:
    sample = sorted(articles, key=lambda p: p.stat().st_mtime, reverse=True)[:3] + sorted(articles)[:3]
    for p in sample:
        html = p.read_text(encoding="utf-8", errors="replace")
        m = re.search(r'<link rel="canonical" href="([^"]+)"', html)
        expected = f"{DOMAIN}/articles/{p.name}"
        if m and m.group(1) == expected:
            ok("canonical", p.name)
        else:
            err("canonical", f"{p.name} -> {m.group(1) if m else '缺失'}")
except Exception as e:
    err("canonical 检查", str(e))

# 5. Git status (unpushed commits / last commit)
try:
    out = subprocess.run(["git", "log", "-1", "--oneline"], cwd=BASE, capture_output=True, text=True)
    last_commit = out.stdout.strip()
    unpushed = subprocess.run(["git", "status", "--porcelain"], cwd=BASE, capture_output=True, text=True)
    dirty = [l for l in unpushed.stdout.splitlines() if l.strip()]
    if dirty:
        warn("git 状态", f"未提交文件 {len(dirty)} 个")
    else:
        ok("git 状态", last_commit)
except Exception as e:
    err("git 检查", str(e))

# 6. Latest article freshness (should be today or yesterday)
try:
    newest = sorted(articles, key=lambda p: p.stat().st_mtime, reverse=True)[0]
    age_days = (__import__("datetime").date.today() - __import__("datetime").date.fromtimestamp(newest.stat().st_mtime)).days
    if age_days <= 1:
        ok("最新文章", f"{newest.name} ({age_days}天前)")
    else:
        err("最新文章", f"{newest.name} 已 {age_days} 天未更新!")
except Exception as e:
    err("新鲜度检查", str(e))

# Report
print("=" * 56)
print("EyewearGuide 每日健康检查")
print("=" * 56)
has_error = False
for level, item, detail in results:
    mark = {"OK": "[OK]  ", "WARN": "[WARN]", "ERROR": "[ERR] "}[level]
    print(f"{mark} {item}: {detail}")
    if level == "ERROR":
        has_error = True
print("=" * 56)
print(f"检查完成: {len([r for r in results if r[0]=='OK'])} OK / "
      f"{len([r for r in results if r[0]=='WARN'])} WARN / "
      f"{len([r for r in results if r[0]=='ERROR'])} ERROR")
sys.exit(1 if has_error else 0)
