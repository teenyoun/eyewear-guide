# IndexNow 提交脚本：首次全量(--all)或每日增量(默认，取最近 commit 新增文章)
# Usage: python indexnow_submit.py [--all]
import json, sys, pathlib, os, subprocess, urllib.request, datetime

ROOT = pathlib.Path(__file__).parent
HOST = 'glasses.teenyoun.com'
API = 'https://api.indexnow.org/indexnow'

def load_key():
    cfg = json.loads((ROOT / 'config.json').read_text(encoding='utf-8'))
    key = cfg.get('indexnow_key')
    if not key:
        print('ERROR: no indexnow_key in config.json')
        sys.exit(1)
    return key

def article_url(name):
    return f'https://{HOST}/articles/{name}'

def collect_urls(all_flag):
    if all_flag:
        urls = [f'https://{HOST}/']
        for f in sorted((ROOT / 'articles').glob('*.html')):
            urls.append(article_url(f.name))
        return urls
    # incremental: files changed since last commit (article publish)
    r = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1'],
                       cwd=str(ROOT), capture_output=True, text=True)
    files = [ln.strip() for ln in r.stdout.splitlines()
             if ln.strip().startswith('articles/') and ln.strip().endswith('.html')]
    urls = [article_url(os.path.basename(f)) for f in files]
    if not urls:
        arts = sorted((ROOT / 'articles').glob('*.html'),
                      key=lambda p: p.stat().st_mtime, reverse=True)
        if arts:
            urls = [article_url(arts[0].name)]
    return urls

def main():
    all_flag = '--all' in sys.argv
    key = load_key()
    urls = collect_urls(all_flag)
    if not urls:
        print('NO_URLS')
        return
    payload = {
        'host': HOST,
        'key': key,
        'keyLocation': f'https://{HOST}/{key}.txt',
        'urlList': urls,
    }
    req = urllib.request.Request(
        API, data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json; charset=utf-8'},
        method='POST')
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        body = resp.read().decode('utf-8', 'ignore')[:300]
        print(f'[{datetime.datetime.now():%Y-%m-%d %H:%M}] '
              f'STATUS={resp.status} mode={"all" if all_flag else "incr"} urls={len(urls)}')
        print(body)
    except urllib.error.HTTPError as e:
        print(f'[{datetime.datetime.now():%Y-%m-%d %H:%M}] HTTP {e.code}: '
              f'{e.read().decode("utf-8", "ignore")[:300]}')
        sys.exit(2)
    except Exception as e:
        print(f'ERROR: {e}')
        sys.exit(3)

if __name__ == '__main__':
    main()
