import json, pathlib, subprocess, shutil, os

base = pathlib.Path(__file__).parent
tmp = pathlib.Path(os.environ.get('TEMP', str(base)))

# 1) record the two pins
p = base / 'pins-queue.json'
q = json.loads(p.read_text(encoding='utf-8'))
q.append({
    'title': 'Best Eyeglass Cases 2026 — Protection, Style & Materials Compared',
    'image': 'pins-batch/pin-45-eyeglass-cases.png',
    'link': 'https://glasses.teenyoun.com/articles/best-eyeglass-cases-2026-protection-style-materials-compared.html',
    'status': 'published',
    'date': '2026-09-16',
    'pin_url': 'https://www.pinterest.com/pin/1055812706414176956/',
})
q.append({
    'title': 'How to Read Your Glasses Prescription — SPH, CYL, AXIS Explained',
    'image': 'pins-batch/pin-46-rx-prescription.png',
    'link': 'https://glasses.teenyoun.com/articles/how-to-read-your-glasses-prescription-sph-cyl-axis-explained.html',
    'status': 'published',
    'date': '2026-09-16',
    'pin_url': 'https://www.pinterest.com/pin/1055812706414176987/',
})
p.write_text(json.dumps(q, ensure_ascii=False, indent=1), encoding='utf-8')
print('pins total: {0}'.format(len(q)))

# 2) archive scratch files
for name in ('check_state.py', 'quora-answer.txt', 'quora-insert.js', 'finish.py'):
    f = base / name
    if f.exists() and name != 'finish.py':
        shutil.move(str(f), str(tmp / ('archive-' + name)))
        print('archived:', name)

# 3) commit + push
subprocess.run(['git', 'add', '-A'], cwd=base, check=True, capture_output=True)
print('staged:\n' + (subprocess.run(['git', 'status', '--short'], cwd=base, capture_output=True, text=True).stdout or '(nothing)'))
subprocess.run(['git', 'commit', '-m', 'matrix 9/16: eyeglass-case + rx-prescription pins (board 94), quora answer'],
               cwd=base, check=True, capture_output=True)
tok = pathlib.Path(r'C:\Users\Administrator\.accio\accounts\1758995702\agents\DID-F456DA-14F456DAU1777026-5875-B06335\agent-core\secrets\github-token.txt').read_text().strip()
subprocess.run(['git', 'remote', 'set-url', 'origin',
                'https://{0}@github.com/teenyoun/eyewear-guide.git'.format(tok)], cwd=base, check=True, capture_output=True)
r = subprocess.run(['git', 'push', 'origin', 'main'], cwd=base, capture_output=True, text=True)
print('PUSH:', ((r.stderr or '') + (r.stdout or '')).strip().splitlines()[-1])
subprocess.run(['git', 'remote', 'set-url', 'origin', 'https://github.com/teenyoun/eyewear-guide.git'], cwd=base, check=True, capture_output=True)
print('remote:', subprocess.run(['git', 'remote', 'get-url', 'origin'], cwd=base, capture_output=True, text=True).stdout.strip())
