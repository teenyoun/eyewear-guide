import re, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import daily

# sanity check normalization
for t in ['sports', 'Sunglasses', 'Blue Light Glasses', 'Reading Glasses', 'Glasses Care', 'Prescription Glasses']:
    print(f'  {t!r} -> {daily.normalize_pick_category(t)!r}')

base = pathlib.Path(__file__).parent
target = base / 'articles' / 'glasses-vs-contacts-for-sports-what-athletes-actually-wear.html'
html = target.read_text(encoding='utf-8')
block = daily.picks_section_html('sports')
print('picks block length:', len(block))
if block and 'pick-card' not in html:
    marker = '<div class="info-box">'
    idx = html.find(marker)
    if idx == -1:
        idx = html.find('</article>')
    html = html[:idx] + block + html[idx:]
    target.write_text(html, encoding='utf-8')
    print('inserted into', target.name)
else:
    print('skip insert (already has cards or no block)')
