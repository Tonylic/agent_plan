#!/usr/bin/env python3
"""Mechanical re-check of every source cited in the workflow outputs.

installed: the file must exist under the OpenClaw package and the anchor must appear in it
           (status ok = within 60 lines of the cited line, near = elsewhere in the file).
web:       the URL must answer; the anchor is searched in the body as a soft signal.
Writes wf/final/source-checks.json keyed by "kind|ref|anchor".
"""
import concurrent.futures as cf
import glob
import html
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WF = HERE + '/data'
PKG = '/opt/homebrew/lib/node_modules/openclaw'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15'


def norm(s):
    return re.sub(r'\s+', ' ', re.sub(r'[`*_"“”‘’\']', '', s or '')).strip().lower()


def collect():
    out = []
    for f in sorted(glob.glob(WF + '/brainstorm/*.json') + glob.glob(WF + '/sourcing/*.json')):
        for feat in json.load(open(f)):
            for s in feat.get('sources', []) or []:
                out.append((feat.get('id'), s))
    for f in sorted(glob.glob(WF + '/verify/*.json')):
        for v in json.load(open(f)):
            for s in v.get('added_sources', []) or []:
                out.append((v.get('id'), s))
    return out


def split_ref(ref):
    ref = ref.strip()
    if ref.startswith(PKG + '/'):
        ref = ref[len(PKG) + 1:]
    m = re.match(r'^(.*?)(?::(\d+)(?:-\d+)?)?$', ref)
    return m.group(1), int(m.group(2)) if m.group(2) else None


def check_installed(s):
    path, line = split_ref(s.get('ref', ''))
    full = os.path.join(PKG, path)
    if not os.path.isfile(full):
        return {'status': 'file-missing', 'path': path}
    lines = open(full, errors='replace').read().split('\n')
    anchor = norm(s.get('anchor', ''))
    if not anchor:
        return {'status': 'no-anchor', 'path': path, 'line': line}
    hits = [i + 1 for i, l in enumerate(lines) if anchor in norm(l)]
    if not hits:
        # anchors sometimes span a line break
        if anchor in norm(' '.join(lines)):
            return {'status': 'near', 'path': path, 'line': line}
        return {'status': 'anchor-missing', 'path': path, 'line': line}
    if line is None:
        return {'status': 'near', 'path': path, 'line': hits[0]}
    best = min(hits, key=lambda h: abs(h - line))
    return {'status': 'ok' if abs(best - line) <= 60 else 'near', 'path': path, 'line': line, 'found_at': best}


def check_web(s):
    url = s.get('ref', '').strip()
    if not re.match(r'^https?://', url):
        return {'status': 'bad-url'}
    try:
        p = subprocess.run(
            ['curl', '-sL', '--max-time', '25', '-A', UA, '-H', 'Accept-Language: en-US,en;q=0.9',
             '-w', '\n%{http_code}', url],
            capture_output=True, timeout=40)
        raw = p.stdout.decode('utf-8', errors='replace')
        body, _, code = raw.rpartition('\n')
        code = int(code) if code.strip().isdigit() else 0
    except Exception as e:  # noqa: BLE001
        return {'status': 'fetch-error', 'error': str(e)[:80]}
    text = norm(html.unescape(re.sub(r'<[^>]+>', ' ', body)))
    anchor = norm(s.get('anchor', ''))
    found = bool(anchor) and anchor in text
    if 200 <= code < 300:
        return {'status': 'ok' if found else 'reachable', 'http': code}
    if code in (401, 403, 405, 429, 999):
        return {'status': 'bot-blocked', 'http': code}
    return {'status': 'http-error', 'http': code}


def main():
    items = collect()
    uniq = {}
    for fid, s in items:
        k = '|'.join([s.get('kind', ''), s.get('ref', ''), s.get('anchor', '')])
        uniq.setdefault(k, {'source': s, 'ids': []})['ids'].append(fid)
    results = {}
    web = [(k, v) for k, v in uniq.items() if v['source'].get('kind') == 'web']
    inst = [(k, v) for k, v in uniq.items() if v['source'].get('kind') != 'web']
    for k, v in inst:
        results[k] = dict(check_installed(v['source']), ids=v['ids'])
    with cf.ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(check_web, v['source']): (k, v) for k, v in web}
        for fut in cf.as_completed(futs):
            k, v = futs[fut]
            results[k] = dict(fut.result(), ids=v['ids'])
    os.makedirs(WF + '/final', exist_ok=True)
    json.dump(results, open(WF + '/final/source-checks.json', 'w'), indent=1)
    tally = {}
    for k, r in results.items():
        key = (k.split('|')[0], r['status'])
        tally[key] = tally.get(key, 0) + 1
    for key in sorted(tally):
        print(key, tally[key])
    bad = [(k, r) for k, r in results.items() if r['status'] in ('file-missing', 'anchor-missing', 'http-error', 'fetch-error', 'bad-url', 'no-anchor')]
    print('--- needs a look:', len(bad))
    for k, r in sorted(bad, key=lambda x: x[1]['status']):
        print(r['status'], r.get('http', ''), '|', k[:150], '|', ','.join(sorted(set(r['ids'])))[:60])


if __name__ == '__main__':
    sys.exit(main())
