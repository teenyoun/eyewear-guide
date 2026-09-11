import pathlib, re, sys

base = pathlib.Path(__file__).parent
sys.path.insert(0, str(base))
import daily

pairs = [
    ('body_drafts/measure-face.html', 'how-to-measure-your-face-for-glasses-at-home-3-easy-methods.html', None),
    ('body_drafts/read-prescription.html', 'how-to-read-your-glasses-prescription-od-os-sph-cyl-explained.html', None),
    ('body_drafts/sports-running.html', 'best-sports-sunglasses-for-running-stay-cool-and-see-clearly.html', 'sports'),
]

for draft, target, picks_cat in pairs:
    body = (base / draft).read_text(encoding='utf-8').strip()
    path = base / 'articles' / target
    html = path.read_text(encoding='utf-8')

    if '<h2>' in html.split('<article>')[1].split('</article>')[0]:
        print('SKIP (already has content):', target)
        continue

    extra = ''
    if picks_cat:
        extra = daily.picks_section_html(picks_cat)

    marker = '<div class="info-box">'
    idx = html.find(marker)
    if idx == -1:
        idx = html.find('</article>')
    html = html[:idx] + body + extra + '\n' + html[idx:]
    path.write_text(html, encoding='utf-8')

    words = len(re.sub(r'<[^>]+>', ' ', body).split())
    print(f'OK {target} | words={words} | picks={len(extra)}')
