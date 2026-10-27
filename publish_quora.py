#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Publish one Quora answer from the server (headed Chromium under xvfb).

Run:
    xvfb-run -a python3 publish_quora.py --url <question-url> --text-file <file> --dry-run
    xvfb-run -a python3 publish_quora.py --url <question-url> --text-file <file>

Dry-run stops right before clicking Post and reports the editor state.
Success is only claimed when an /answer/ permalink is read back and loads.
"""
import argparse, json, os, re, sys, time
from playwright.sync_api import sync_playwright

COOKIE = os.path.expanduser("~/.publisher-cookies/quora.json")
PROFILE = os.path.expanduser("~/.publisher-profile/quora")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36")


def log(m):
    print("[%s] %s" % (time.strftime("%H:%M:%S"), m), flush=True)


def add_cookies(ctx):
    fixed = []
    for c in json.load(open(COOKIE, encoding="utf-8")):
        it = {"name": c.get("name"), "value": c.get("value"),
              "domain": c.get("domain") or ".quora.com", "path": c.get("path") or "/"}
        e = c.get("expirationDate") or c.get("expires")
        if e:
            it["expires"] = float(e)
        if c.get("sameSite") in ("Strict", "Lax", "None"):
            it["sameSite"] = c["sameSite"]
        if c.get("httpOnly") is not None:
            it["httpOnly"] = bool(c["httpOnly"])
        if c.get("secure") is not None:
            it["secure"] = bool(c["secure"])
        fixed.append(it)
    ctx.add_cookies(fixed)
    return len(fixed)


def click_first(page, names, timeout=8000):
    for n in names:
        try:
            loc = page.get_by_role("button", name=re.compile(n, re.I)).first
            if loc.count() and loc.is_visible():
                loc.click(timeout=timeout)
                return n
        except Exception:
            continue
    try:
        loc = page.get_by_text(re.compile(names[0], re.I)).first
        if loc.count():
            loc.click(timeout=timeout)
            return names[0] + " (text)"
    except Exception:
        pass
    return None


def find_answer_permalink(page):
    hrefs = page.eval_on_selector_all(
        'a[href*="/answer/"]', "els => els.map(e => e.getAttribute('href'))")
    for h in hrefs or []:
        m = re.search(r"/answer/([A-Za-z0-9\-]+)", h)
        if m:
            return "https://www.quora.com" + h if h.startswith("/") else h
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--text-file", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    text = open(args.text_file, encoding="utf-8").read().strip()
    assert text, "empty answer text"
    assert "&sup" not in text and "&deg" not in text, "HTML entities are forbidden on Quora"
    log("answer chars: %d" % len(text))

    with sync_playwright() as p:
        # A persistent profile keeps Cloudflare's clearance cookie between runs,
        # which is what makes a daily cron job viable at all.
        ctx = p.chromium.launch_persistent_context(
            PROFILE, headless=False, channel="chromium",
            viewport={"width": 1366, "height": 950}, user_agent=UA,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"])
        ctx.add_init_script(
            "Object.defineProperty(navigator,'webdriver',{get:()=>undefined});"
            "Object.defineProperty(navigator,'plugins',{get:()=>[1,2,3,4,5]});"
            "window.chrome={runtime:{}};")
        log("cookies: %d" % add_cookies(ctx))
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        # up to 3 navigation attempts: the interstitial sometimes never clears
        opened = False
        for attempt in range(3):
            page.goto(args.url, wait_until="domcontentloaded", timeout=90000)
            for i in range(16):
                page.wait_for_timeout(3000)
                if "Just a moment" not in page.title() and \
                        "Performing security verification" not in page.inner_text("body")[:300]:
                    log("page ready on attempt %d (~%ds)" % (attempt + 1, 3 * (i + 1)))
                    opened = True
                    break
            if opened:
                break
            log("challenge still up, attempt %d/3 failed" % (attempt + 1))
        if not opened:
            log("BLOCKED by Cloudflare challenge after 3 attempts")
            ctx.close()
            return 3
        page.wait_for_timeout(2000)
        body = page.inner_text("body")[:400]
        log("question: " + page.title()[:90])
        if re.search(r"You've written an answer|You have written an answer", body):
            log("already answered this question — aborting")
            ctx.close()
            return 4

        clicked = click_first(page, ["^Answer$", "^Answer this question$", "^\\u56de\\u7b54$"])
        log("answer button: %s" % clicked)
        page.wait_for_timeout(5000)

        editor = None
        for sel in ['div[contenteditable="true"]', 'div[role="textbox"]', '[contenteditable="true"]']:
            loc = page.locator(sel).first
            try:
                if loc.count() and loc.is_visible():
                    editor = loc
                    break
            except Exception:
                continue
        if editor is None:
            log("editor did not appear")
            ctx.close()
            return 5

        editor.click()
        page.wait_for_timeout(800)
        editor.type(text, delay=6)
        page.wait_for_timeout(2500)
        typed = editor.inner_text()
        log("typed chars in editor: %d" % len(typed))
        if len(typed) < len(text) * 0.8:
            log("editor content shorter than source — refusing to post")
            ctx.close()
            return 6

        btns = page.eval_on_selector_all(
            'button, [role="button"]',
            "els => els.map(e => (e.innerText||'').trim()).filter(t => t && t.length < 25)")
        log("buttons now: %s" % sorted(set(btns))[:20])

        if args.dry_run:
            log("DRY-RUN: stopping before Post")
            ctx.close()
            return 0

        posted = click_first(page, ["^Post$", "^\\u53d1\\u5e03$", "^Publish$"], timeout=10000)
        log("post button: %s" % posted)
        if not posted:
            ctx.close()
            return 7

        deadline = time.time() + 60
        link = None
        while time.time() < deadline:
            page.wait_for_timeout(3000)
            link = find_answer_permalink(page)
            if link:
                break
        log("permalink: %s" % (link or "-"))
        ctx.close()
        if not link:
            return 8
        print("PERMALINK=" + link)
        return 0


if __name__ == "__main__":
    sys.exit(main())
