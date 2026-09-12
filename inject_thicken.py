import re, io, pathlib

PAIRS = [
    ('best-glasses-for-round-faces-frame-shapes-that-flatter.html', 'body_drafts/round-faces-body.html'),
    ('photochromic-vs-prescription-sunglasses-which-is-better-.html', 'body_drafts/photochromic-body.html'),
    ('computer-glasses-vs-reading-glasses-what-s-the-difference-.html', 'body_drafts/computer-vs-reading-body.html'),
]

for target, draft in PAIRS:
    path = pathlib.Path('articles') / target
    html = io.open(path, encoding='utf-8').read()
    body = io.open(draft, encoding='utf-8').read().strip()

    m = re.search(r'<article>(.*?)</article>', html, re.S)
    inner = m.group(1)

    head = re.search(r'(<h1>.*?</h1>\s*<p class="byline">.*?</p>)', inner, re.S)
    if not head:
        print('NO HEAD:', target)
        continue
    tail = re.search(r'(<div class="info-box">.*?</div>)', inner, re.S)

    before_words = len(re.sub(r'<[^>]+>', ' ', inner).split())
    new_inner = '\n' + head.group(1) + '\n' + body + '\n'
    if tail:
        new_inner += tail.group(1) + '\n'
    new_inner += '\n'

    new_html = html[:m.start(1)] + new_inner + html[m.end(1):]
    io.open(path, 'w', encoding='utf-8', newline='').write(new_html)

    chk = re.search(r'<article>(.*?)</article>', new_html, re.S).group(1)
    after_words = len(re.sub(r'<[^>]+>', ' ', chk).split())
    print(target)
    print('   before:', before_words, '-> after:', after_words,
          '| info-box kept:', bool(tail),
          '| pick-card:', 'pick-card' in html,
          '| h1:', chk.count('<h1>'), '| byline:', chk.count('class="byline"'))
