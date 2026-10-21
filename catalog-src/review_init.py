#!/usr/bin/env python3
"""Start the review loop: round 0 is the 11 Oct catalog's live items; the 60 already turned down go to the removal log."""
import json

from review_lib import HERE, REV, dump, write_chunks, write_index

cat = json.load(open(HERE + '/data/final/catalog-pre-review.json'))
F = cat['features']

items = []
for tier in ('1', '2', '3'):
    for sec in cat['sections'][tier]:
        for fid in sec['ids']:
            f = dict(F[fid])
            f['tier'] = int(tier)
            f['section'] = sec['title']
            f['includes'] = []
            f['history'] = []
            f.pop('rejected', None)
            items.append(f)

removed = []
for fid in cat['rejected']:
    f = F[fid]
    removed.append({'id': fid, 'name': f['name'], 'tier': f['tier'], 'round': 0, 'category': 'advised-against',
                    'reason': f.get('reject_reason', ''), 'sources': f.get('sources', [])[:6]})

dump(items, f'{REV}/r0.json')
dump(removed, f'{REV}/removed.json')
dump({}, f'{REV}/merged-map.json')
write_index(items, 0)
n = write_chunks(items, 0)
print(json.dumps({'round': 0, 'items': len(items), 'removed_before_review': len(removed), 'chunks': n}))
