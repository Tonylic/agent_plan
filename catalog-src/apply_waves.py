#!/usr/bin/env python3
"""Turn the verified wave definition (data/review/waves/final.json) into an owner round that re-waves the items.

usage: python3 apply_waves.py K [definition.json]     (writes data/review/r{K}.owner.json; then run: python3 apply_owner.py K)
Every item gets the wave the definition gives it; items on its "not in a wave yet" list get wave "none".
"""
import json
import sys

from review_lib import REV, dump, load

K = int(sys.argv[1])
SRC_FILE = sys.argv[2] if len(sys.argv) > 2 else f'{REV}/waves/final.json'
d = load(SRC_FILE)
items = load(f'{REV}/r{K - 1}.json')
ids = [it['id'] for it in items]

where, why = {}, {}
for w in d['waves']:
    for ph in w.get('phases', []):
        for i in ph.get('ids', []):
            where.setdefault(i, []).append(w['wave'])
for x in d.get('not_in_a_wave', []):
    where.setdefault(x['id'], []).append('none')
    why[x['id']] = x.get('reason', '')
for c in d.get('changes_from_today', []):
    why.setdefault(c['id'], c.get('why', ''))

problems = [f'{i}: placed {len(where.get(i, []))} times ({where.get(i)})' for i in ids if len(where.get(i, [])) != 1]
problems += [f'{i}: not a catalog item' for i in where if i not in ids]
if problems:
    print(json.dumps({'error': 'the wave definition does not place every item exactly once', 'problems': problems}, indent=1))
    sys.exit(1)

edits = []
for it in items:
    new = where[it['id']][0]
    if new == 'none' and it.get('wave') == 'parked':
        continue
    if new != it.get('wave'):
        old = it.get('wave')
        label = 'not in a wave yet' if new == 'none' else f'wave {new}'
        edits.append({'id': it['id'], 'set': {'wave': new},
                      'note': f'moved from wave {old} to {label}. {why.get(it["id"], "")}'.strip()})
dump({'label': 'Wave definition, 12 Oct', 'edits': edits}, f'{REV}/r{K}.owner.json')
print(json.dumps({'round': K, 'moved': len(edits), 'unchanged': len(items) - len(edits)}))
