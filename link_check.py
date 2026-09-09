# 每日精选链接检查：检查 picks.json 中所有图片/详情页链接有效性
# Usage: python link_check.py [--verbose]
import json, pathlib, urllib.request, datetime, sys

ROOT = pathlib.Path(__file__).parent
PICKS = ROOT / 'picks.json'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')

def check(url, timeout=15):
    """Return True if URL returns HTTP 200 (HEAD, fallback GET)."""
    req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status == 200
    except Exception:
        pass
    # fallback GET
    req2 = urllib.request.Request(url, method='GET', headers={'User-Agent': UA, 'Range': 'bytes=0-0'})
    try:
        with urllib.request.urlopen(req2, timeout=timeout) as r:
            return r.status in (200, 206)
    except Exception:
        return False

def main():
    verbose = '--verbose' in sys.argv
    if not PICKS.exists():
        print('NO_PICKS')
        return
    data = json.loads(PICKS.read_text(encoding='utf-8'))
    if not data:
        print('PICKS_EMPTY')
        return
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    dead = []
    for item in data:
        img_ok = check(item.get('img_url', ''))
        link_ok = check(item.get('link_url', ''))
        item['img_ok'] = img_ok
        item['link_ok'] = link_ok
        item['last_checked'] = now
        if not (img_ok and link_ok):
            dead.append(item)
        if verbose:
            print(f"{item.get('name','?')[:40]:42s} img={'OK' if img_ok else 'DEAD'} link={'OK' if link_ok else 'DEAD'}")
    PICKS.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f"[{now}] checked={len(data)} dead={len(dead)}")
    for d in dead:
        print('  DEAD:', d.get('name', '?'), '|', d.get('link_url', ''))

if __name__ == '__main__':
    main()
