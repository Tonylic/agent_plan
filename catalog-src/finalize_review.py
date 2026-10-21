#!/usr/bin/env python3
"""Turn the last review round into data/final/catalog.json, the shape render.py reads.

Also re-opens, by script, every source the review rounds added (the earlier ones were checked on 11 Oct).
usage: python3 finalize_review.py
"""
import concurrent.futures as cf
import glob
import json
import re
import time

from check_sources import check_installed, check_web
from review_lib import HERE, REV, dump, load

BAD = {'file-missing', 'anchor-missing', 'http-error', 'fetch-error', 'bad-url', 'no-anchor'}

rounds = sorted(int(re.search(r'r(\d+)\.json$', p).group(1)) for p in glob.glob(f'{REV}/r*.json')
                if re.search(r'/r\d+\.json$', p))
K = rounds[-1]
items = load(f'{REV}/r{K}.json')
removed = load(f'{REV}/removed.json', [])
merged_map = load(f'{REV}/merged-map.json', {})
stats = [load(f'{REV}/r{k}.stats.json') for k in rounds if k > 0]

# --- script re-check of sources added during review ---
# A result that once passed is kept, so a flaky host cannot drop a good source on a later rebuild;
# anything not yet passed is tried up to three times.
CACHE = HERE + '/data/final/review-source-checks.json'
cache = load(CACHE, {})
PASS = {'ok', 'near', 'reachable', 'bot-blocked'}
todo = {}
for holder in items + removed:
    for s in holder.get('sources', []) or []:
        if s.get('check', 'unchecked') == 'unchecked':
            todo.setdefault((s.get('kind'), s.get('ref'), s.get('anchor')), []).append(s)


def ck(k):
    return '|'.join(str(x) for x in k)


def run(k):
    src = todo[k][0]
    return (check_web(src) if k[0] == 'web' else check_installed(src))['status']


results = {k: cache[ck(k)] for k in todo if cache.get(ck(k)) in PASS}
for attempt in range(3):
    pending = [k for k in todo if results.get(k) not in PASS]
    if not pending:
        break
    if attempt:
        time.sleep(4)
    with cf.ThreadPoolExecutor(max_workers=6 if attempt else 12) as ex:
        futs = {ex.submit(run, k): k for k in pending}
        for fut in cf.as_completed(futs):
            results[futs[fut]] = fut.result()
for k, st in results.items():
    cache[ck(k)] = st
dump(cache, CACHE)
for k, lst in todo.items():
    for s in lst:
        s['check'] = results[k]
tally = {}
for k, st in results.items():
    tally[(k[0], st)] = tally.get((k[0], st), 0) + 1

problems = []
for holder in items + removed:
    kept = []
    for s in holder.get('sources', []) or []:
        if s.get('check') in BAD:
            problems.append((holder['id'], s.get('check'), s.get('ref'), s.get('anchor')))
        else:
            kept.append(s)
    holder['sources'] = kept
# the credible mention each item was kept on: find the full source object in the verdict files and re-open it
verdict_src = {}
for k in rounds:
    for pth in sorted(glob.glob(f'{REV}/r{k}/chunk-*.final.json')):
        for row in load(pth, []) or []:
            d = row.get('demand_source') if isinstance(row, dict) else None
            if isinstance(d, dict) and d.get('ref'):
                verdict_src[(row.get('id'), d['ref'])] = d
for it in items:
    d = it.get('demand')
    if d:
        full = next((s for s in it['sources'] if s.get('ref') == d.get('ref')), None)
        if full is None:
            full = verdict_src.get((it['id'], d.get('ref'))) or next(
                (v for (i, r), v in verdict_src.items() if r == d.get('ref')), None)
            if full is not None:
                full = dict(full)
                full['check'] = (check_web(full) if full.get('kind') == 'web' else check_installed(full))['status']
        if full is None or full.get('check') in BAD:
            problems.append((it['id'], 'credible-mention source not confirmed by script', d.get('ref'), (full or {}).get('check', 'not found')))
            d['check'] = 'unconfirmed'
        else:
            d.update({'kind': full.get('kind'), 'anchor': full.get('anchor', ''), 'check': full.get('check')})
    else:
        problems.append((it['id'], 'no credible mention recorded', '', ''))
    if not it['sources']:
        problems.append((it['id'], 'no source left', '', ''))

# where each folded item ended up after later merges; recover a fold note the apply step had to drop
live = {it['id']: it for it in items}


def resolve(i):
    seen = set()
    while i not in live and i in merged_map and i not in seen:
        seen.add(i)
        i = merged_map[i]
    return i if i in live else ''


for r in removed:
    r['fold_final'] = resolve(r['fold_into']) if r.get('fold_into') else ''
    tgt = live.get(r['fold_final'])
    if tgt is not None and not any(str(a).startswith(f'From {r["id"]} ') for a in tgt.get('adds') or []):
        tgt.setdefault('adds', []).append(f'From {r["id"]} ({r["name"]}): {r.get("reason", "")}')
aliases = {a: resolve(a) for a in merged_map if resolve(a)}

sections = {'1': [], '2': [], '3': []}
for it in items:
    secs = sections[str(it['tier'])]
    if not secs or secs[-1]['title'] != it['section']:
        hit = next((s for s in secs if s['title'] == it['section']), None)
        if hit is None:
            hit = {'title': it['section'], 'ids': []}
            secs.append(hit)
        hit['ids'].append(it['id'])
    else:
        secs[-1]['ids'].append(it['id'])

waves_def = load(f'{REV}/waves/final.json')
if waves_def:
    for w in waves_def['waves']:
        for c in w.get('conditional_items') or []:
            if c.get('id') in live:
                live[c['id']]['wave_condition'] = c.get('condition', '')
    for x in waves_def.get('not_in_a_wave') or []:
        if x.get('id') in live:
            live[x['id']]['wave_condition'] = x.get('reason', '')

out = {'features': {it['id']: it for it in items}, 'sections': sections, 'removed': removed, 'waves_def': waves_def,
       'aliases': aliases, 'review': {'rounds': stats, 'last': K, 'source_recheck': {f'{a} {b}': n for (a, b), n in tally.items()}}}
dump(out, HERE + '/data/final/catalog.json')

print('final round', K, 'items', len(items), 'removed log', len(removed), 'aliases', len(merged_map))
print('sources added in review, re-checked:', dict(sorted((f'{a} {b}', n) for (a, b), n in tally.items())))
print('problems:', len(problems))
for p in problems:
    print('  ', p)
