import pathlib, subprocess, shutil, os

base = pathlib.Path(__file__).parent
tmp = pathlib.Path(os.environ.get('TEMP', str(base)))

# scratch files -> recycle to TEMP (no hard delete of anything potentially useful)
for name in ('check_state.py', 'pin_candidates.py', 'record_pins.py',
             'quora-answer.txt', 'progress-rolling.md'):
    f = base / name
    if f.exists():
        shutil.move(str(f), str(tmp / ('archive-' + name)))
        print('archived:', name)

subprocess.run(['git', 'add', '-A'], cwd=base, check=True, capture_output=True)
r = subprocess.run(['git', 'status', '--short'], cwd=base, capture_output=True, text=True)
print('staged:\n' + (r.stdout or '(nothing)'))

subprocess.run(['git', 'commit', '-m',
                'matrix 9/15: under-50 + face-shape pins (board 92), quora answer; sync picks last_checked'],
               cwd=base, check=True, capture_output=True)

tok = pathlib.Path(r'C:\Users\Administrator\.accio\accounts\1758995702\agents\DID-F456DA-14F456DAU1777026-5875-B06335\agent-core\secrets\github-token.txt').read_text().strip()
subprocess.run(['git', 'remote', 'set-url', 'origin',
                'https://{0}@github.com/teenyoun/eyewear-guide.git'.format(tok)], cwd=base, check=True, capture_output=True)
p = subprocess.run(['git', 'push', 'origin', 'main'], cwd=base, capture_output=True, text=True)
lines = ((p.stderr or '') + (p.stdout or '')).strip().splitlines()
print('PUSH:', lines[-1] if lines else '?')
subprocess.run(['git', 'remote', 'set-url', 'origin', 'https://github.com/teenyoun/eyewear-guide.git'], cwd=base, check=True, capture_output=True)
print('status after:', repr(subprocess.run(['git', 'status', '--short'], cwd=base, capture_output=True, text=True).stdout))
print('remote:', subprocess.run(['git', 'remote', 'get-url', 'origin'], cwd=base, capture_output=True, text=True).stdout.strip())
(base / 'finish.py').unlink(missing_ok=True)
