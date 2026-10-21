#!/usr/bin/env python3
"""Apply the owner's decisions as one more round on top of the review loop.

usage: python3 apply_owner.py K        (reads data/review/r{K-1}.json and data/review/r{K}.owner.json)
The owner file: { "label": "...", "edits": [ { "id", "note", "set": {field: value},
  "replace": [{"field", "old", "new"}], "prepend": {list_field: [..]}, "drop_sources": ["substring of ref"],
  "add_sources": [source objects] } ] }
"""
import json
import sys

from review_lib import REV, dump, load, write_chunks, write_index

K = int(sys.argv[1])
items = load(f'{REV}/r{K - 1}.json')
spec = load(f'{REV}/r{K}.owner.json')
by_id = {it['id']: it for it in items}
problems, edited = [], 0

for e in spec['edits']:
    it = by_id.get(e['id'])
    if it is None:
        problems.append(f'unknown id {e["id"]}')
        continue
    for k, v in (e.get('set') or {}).items():
        it[k] = v
    for r in e.get('replace') or []:
        cur = it.get(r['field'])
        if isinstance(cur, str) and r['old'] in cur:
            it[r['field']] = cur.replace(r['old'], r['new'])
        elif isinstance(cur, list) and any(r['old'] in str(x) for x in cur):
            it[r['field']] = [str(x).replace(r['old'], r['new']) for x in cur]
        else:
            problems.append(f'{e["id"]}: text to replace not found in {r["field"]}: {r["old"][:60]}')
    for k, v in (e.get('prepend') or {}).items():
        it[k] = list(v) + list(it.get(k) or [])
    drops = e.get('drop_sources') or []
    if drops:
        it['sources'] = [s for s in it.get('sources', []) if not any(d in str(s.get('ref')) for d in drops)]
    have = {(s.get('kind'), s.get('ref')) for s in it.get('sources', [])}
    for s in e.get('add_sources') or []:
        if (s.get('kind'), s.get('ref')) not in have:
            it.setdefault('sources', []).append(dict(s, check='unchecked', added_round=K))
    it.setdefault('history', []).append(f'r{K} ({spec["label"]}): {e["note"]}')
    edited += 1

dump(items, f'{REV}/r{K}.json')
write_index(items, K)
stats = {'round': K, 'label': spec['label'], 'in': len(items), 'out': len(items), 'removed': 0, 'edited': edited,
         'merged_groups': 0, 'merged_away': 0, 'overturned': 0, 'kept': len(items) - edited, 'sources_added': 0,
         'chunks': write_chunks(items, K), 'changes': edited, 'problems': problems}
dump(stats, f'{REV}/r{K}.stats.json')
print(json.dumps(stats))
