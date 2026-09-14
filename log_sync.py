import pathlib, subprocess

base = pathlib.Path(__file__).parent
subprocess.run(['git', 'add', '-A'], cwd=base, check=True, capture_output=True)
r0 = subprocess.run(['git', 'status', '--short'], cwd=base, capture_output=True, text=True)
if not r0.stdout.strip():
    print('nothing to commit')
else:
    subprocess.run(['git', 'commit', '-m', 'sync daily-log.txt after 9/14 publish'], cwd=base, check=True, capture_output=True)
    tok = pathlib.Path(r'C:\Users\Administrator\.accio\accounts\1758995702\agents\DID-F456DA-14F456DAU1777026-5875-B06335\agent-core\secrets\github-token.txt').read_text().strip()
    subprocess.run(['git', 'remote', 'set-url', 'origin',
                    'https://{0}@github.com/teenyoun/eyewear-guide.git'.format(tok)], cwd=base, check=True, capture_output=True)
    p = subprocess.run(['git', 'push', 'origin', 'main'], cwd=base, capture_output=True, text=True)
    lines = ((p.stderr or '') + (p.stdout or '')).strip().splitlines()
    print('PUSH:', lines[-1] if lines else '?')
    subprocess.run(['git', 'remote', 'set-url', 'origin', 'https://github.com/teenyoun/eyewear-guide.git'], cwd=base, check=True, capture_output=True)

print('status now:', repr(subprocess.run(['git', 'status', '--short'], cwd=base, capture_output=True, text=True).stdout))
print('remote:', subprocess.run(['git', 'remote', 'get-url', 'origin'], cwd=base, capture_output=True, text=True).stdout.strip())
(base / 'log_sync.py').unlink(missing_ok=True)
