#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Publish scheduled Pinterest pins from pins-queue.json.

Usage:
    python3 publish_pins.py            # publish today's due pins (max 3)
    python3 publish_pins.py --dry-run  # fill everything, stop before clicking publish
    python3 publish_pins.py --limit 1  # publish at most N

Only records with status == "pending" and date <= today are eligible.
Never edits a record before the permalink is verified.
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time

REPO = os.path.expanduser("~/eyewear-guide")
QUEUE = os.path.join(REPO, "pins-queue.json")
COOKIE = os.path.expanduser("~/.publisher-cookies/pinterest.json")
BOARD = "Eyewear Guide"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36")
STEALTH = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
window.chrome = { runtime: {} };
"""


def log(msg):
    print("[%s] %s" % (dt.datetime.now().strftime("%H:%M:%S"), msg), flush=True)


def load_queue():
    with open(QUEUE, "rb") as f:
        raw = f.read()
    return json.loads(raw.decode("utf-8")), raw.count(b"\n") == raw.count(b"\r\n")


def mark_published(rec, pin_url):
    """Update one record in place.

    Never re-serialises the whole file: a full json.dumps rewrites every line's
    layout, so a single publish showed up as a 500-line diff. The record is
    located by its unique image path and only its status and pin_url lines are
    touched, then the result is re-parsed to prove nothing else moved.
    """
    raw = open(QUEUE, "rb").read()
    crlf = raw.count(b"\n") == raw.count(b"\r\n")
    text = raw.decode("utf-8")
    anchor = '"image": %s' % json.dumps(rec["image"], ensure_ascii=False)
    idx = text.find(anchor)
    assert idx != -1, "record not found by image anchor: " + rec["image"]
    start = text.rfind("{", 0, idx)
    end = text.find("}", idx)
    block = text[start:end]

    assert block.count('"status": "pending"') == 1, "unexpected status lines in record"
    new_block = block.replace('"status": "pending"', '"status": "published"', 1)
    if '"pin_url": ""' in new_block:
        new_block = new_block.replace('"pin_url": ""', '"pin_url": %s' % json.dumps(pin_url), 1)
    elif '"pin_url":' in new_block:
        import re as _re
        new_block = _re.sub(r'"pin_url":\s*"[^"]*"', '"pin_url": %s' % json.dumps(pin_url), new_block, count=1)
    else:
        raise AssertionError("no pin_url field in record")

    out = text[:start] + new_block + text[end:]
    before = json.loads(text)
    after = json.loads(out)
    assert len(before) == len(after)
    changed = [i for i in range(len(before)) if before[i] != after[i]]
    assert len(changed) == 1, "expected exactly one changed record, got %d" % len(changed)
    # Locate by the unique image path, not by dict equality: main() already
    # mutated rec's status/pin_url before calling us, so rec no longer equals
    # the still-pending object parsed out of the file.
    matches = [i for i, r in enumerate(before) if r.get("image") == rec["image"]]
    assert len(matches) == 1, "image anchor is not unique: %s" % rec["image"]
    target = matches[0]
    assert changed[0] == target, "changed the wrong record"
    assert after[target]["status"] == "published" and after[target]["pin_url"] == pin_url

    tmp = QUEUE + ".tmp"
    with open(tmp, "wb") as f:
        f.write(out.encode("utf-8"))
    os.replace(tmp, QUEUE)
    return target, crlf


def due_records(data, limit, today=None):
    today = today or dt.date.today().isoformat()
    out = []
    for r in data:
        if r.get("status") == "pending" and (r.get("date") or today) <= today:
            out.append(r)
    out.sort(key=lambda r: (r.get("date") or "", r.get("image") or ""))
    return out[:limit]


TOKEN_FILE = os.path.expanduser("~/.github-token")


def push_with_token():
    """Push using the token file, restoring the clean remote afterwards."""
    try:
        token = open(TOKEN_FILE, encoding="utf-8").read().strip()
    except OSError:
        return 128, "no token file"
    if not token:
        return 128, "empty token"
    _, orig = git("remote", "get-url", "origin")
    orig = orig.strip()
    if not orig.startswith("https://github.com/"):
        return 128, "unexpected remote " + orig
    inj = orig.replace("https://github.com/", "https://%s@github.com/" % token)
    git("remote", "set-url", "origin", inj)
    try:
        code, out = git("push", "origin", "HEAD:main")
    finally:
        git("remote", "set-url", "origin", orig)
    safe = out.replace(token, "***")
    return code, safe


def git(*args):
    p = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def add_cookies(ctx):
    with open(COOKIE, encoding="utf-8") as f:
        cookies = json.load(f)
    fixed = []
    for c in cookies:
        item = {
            "name": c.get("name"),
            "value": c.get("value"),
            "domain": c.get("domain") or ".pinterest.com",
            "path": c.get("path") or "/",
        }
        exp = c.get("expirationDate") or c.get("expires")
        if exp:
            item["expires"] = float(exp)
        if "sameSite" in c and c["sameSite"] in ("Strict", "Lax", "None"):
            item["sameSite"] = c["sameSite"]
        if c.get("httpOnly") is not None:
            item["httpOnly"] = bool(c["httpOnly"])
        if c.get("secure") is not None:
            item["secure"] = bool(c["secure"])
        fixed.append(item)
    ctx.add_cookies(fixed)
    return len(fixed)


def wait_file_input(page, budget=180):
    end = time.time() + budget
    while time.time() < end:
        try:
            n = page.locator('input[type=file]').count()
        except Exception:
            n = 0
        if n:
            return True
        page.wait_for_timeout(2000)
    return False


def find_permalink(page):
    """Read a pin id from the page URL or any rendered link after publishing."""
    m = re.search(r"/pin/(\d{6,25})", page.url or "")
    if m:
        return "https://www.pinterest.com/pin/%s/" % m.group(1)
    pats = [
        'a[href*="/pin/"]',
    ]
    for sel in pats:
        try:
            links = page.locator(sel)
            for i in range(min(links.count(), 40)):
                href = links.nth(i).get_attribute("href") or ""
                m = re.search(r"/pin/(\d{6,25})", href)
                if m:
                    return "https://www.pinterest.com/pin/%s/" % m.group(1)
        except Exception:
            continue
    return None


def publish_one(ctx, rec, dry_run):
    img = os.path.join(REPO, rec["image"])
    if not os.path.exists(img):
        return None, "image missing: " + img
    page = ctx.new_page()
    try:
        page.goto("https://www.pinterest.com/pin-creation-tool/", wait_until="domcontentloaded", timeout=90000)
        if not wait_file_input(page):
            return None, "file input never appeared (hydration)"
        page.set_input_files("input[type=file]", img)
        log("uploaded " + os.path.basename(img))
        page.wait_for_timeout(12000)

        try:
            page.get_by_text("知道了", exact=True).first.click(timeout=4000)
        except Exception:
            pass

        title_box = page.locator('input[placeholder*="简要描述"], input[placeholder*="title" i]').first
        title_box.fill(rec["title"])

        desc = rec.get("description") or ""
        if desc:
            ed = page.locator('div[contenteditable="true"][aria-label*="描述"]').first
            ed.click()
            ed.type(desc, delay=8)

        link_box = page.locator('input[type=url]').first
        link_box.fill(rec["link"])
        link_box.press("Tab")

        # board
        try:
            board_txt = page.locator('[data-test-id=board-dropdown-select-button]').first.inner_text()
            if BOARD not in board_txt:
                page.locator('[data-test-id=board-dropdown-select-button]').first.click(timeout=8000)
                page.get_by_text(BOARD, exact=True).first.click(timeout=8000)
        except Exception as e:
            log("board step note: %s" % e)

        # AI toggles must be off
        try:
            boxes = page.locator('input[type=checkbox]')
            for i in range(boxes.count()):
                b = boxes.nth(i)
                if b.is_checked():
                    b.uncheck(force=True)
        except Exception as e:
            log("toggle step note: %s" % e)

        page.wait_for_timeout(1500)
        if dry_run:
            js = """() => {
              const t = document.querySelector('input[placeholder*="\u7b80\u8981\u63cf\u8ff0"]');
              const l = document.querySelector('input[type=url]');
              const d = document.querySelector('div[contenteditable="true"]');
              const b = document.querySelector('[data-test-id=board-dropdown-select-button]');
              const cbs = [...document.querySelectorAll('input[type=checkbox]')].map(c => c.checked);
              return {title: t ? t.value : null, link: l ? l.value : null,
                      desc: d ? d.innerText.slice(0, 50) : null,
                      board: b ? b.innerText : null, checks: cbs};
            }"""
            return None, "DRY-RUN ok " + repr(page.evaluate(js))

        btn = None
        cands = []
        try:
            cands.append(page.get_by_role("button", name=re.compile(r"^\u53d1\u5e03$")).first)
        except Exception:
            pass
        cands.append(page.locator('button[data-test-id=storyboard-creation-nav-done]').first)
        for cand in cands:
            try:
                if cand.count() and cand.is_enabled():
                    btn = cand
                    break
            except Exception:
                continue
        if btn is None:
            return None, "publish button not found or disabled"
        btn.click()
        log("clicked publish")

        deadline = time.time() + 60
        while time.time() < deadline:
            page.wait_for_timeout(2000)
            href = find_permalink(page)
            if href:
                return href, "published"
        return None, "no permalink after publish"
    finally:
        try:
            page.close()
        except Exception:
            pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=3)
    ap.add_argument("--date", default=None, help="treat this YYYY-MM-DD as today")
    args = ap.parse_args()

    data, crlf = load_queue()
    todo = due_records(data, args.limit, args.date)
    log("due pins: %d" % len(todo))
    if not todo:
        return 0

    from playwright.sync_api import sync_playwright
    ok = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="chromium",
                                    args=["--disable-blink-features=AutomationControlled"])
        ctx = browser.new_context(user_agent=UA, viewport={"width": 1440, "height": 960})
        ctx.add_init_script(STEALTH)
        n = add_cookies(ctx)
        log("cookies loaded: %d" % n)
        page0 = ctx.new_page()
        page0.goto("https://www.pinterest.com/", wait_until="domcontentloaded", timeout=60000)
        page0.wait_for_timeout(3000)
        logged = "login" not in page0.url
        log("logged in: %s (%s)" % (logged, page0.url))
        page0.close()
        if not logged:
            browser.close()
            return 3

        for rec in todo:
            log("publishing: " + rec["title"][:60])
            href, note = publish_one(ctx, rec, args.dry_run)
            log("result: %s | %s" % (href or "-", note))
            if href and not args.dry_run:
                rec["status"] = "published"
                rec["pin_url"] = href
                pos, crlf2 = mark_published(rec, href)
                log("record #%d marked published (file keeps its own layout, crlf=%s)" % (pos + 1, crlf2))
                ok += 1
                time.sleep(20)
        browser.close()

    if args.dry_run or not ok:
        return 0 if args.dry_run else 4

    code, out = git("add", "pins-queue.json")
    code, out = git("commit", "-m", "pins: publish %d scheduled pin(s) on %s" % (ok, dt.date.today()))
    log("commit: %s" % out.splitlines()[0] if out else "commit: nothing")
    code, out = push_with_token()
    log("push rc=%d %s" % (code, out.splitlines()[-1] if out else ""))
    return 0 if code == 0 else 5


if __name__ == "__main__":
    sys.exit(main())
