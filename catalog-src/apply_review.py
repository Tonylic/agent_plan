#!/usr/bin/env python3
"""Apply one review round mechanically.

usage: python3 apply_review.py K
reads   data/review/r{K-1}.json
        data/review/r{K}/chunk-*.final.json   (falls back to chunk-*.review.json if the challenger left none)
        data/review/r{K}/merges.json
writes  data/review/r{K}.json, r{K}.index.md, r{K}.chunk-*.json, r{K}.stats.json; appends removed.json, merged-map.json
prints  the stats as one JSON object
"""
import glob
import json
import os
import re
import sys

from review_lib import REV, dump, load, write_chunks, write_index

READY_ORDER = ['now', 'build', 'experimental', 'blocked', 'not-recommended']
RISK_ORDER = ['low', 'medium', 'high']
EFFORT_ORDER = ['S', 'M', 'L']
EDITABLE = {'name', 'description', 'example', 'how', 'depends_on', 'caveats', 'safety', 'unverified',
            'readiness', 'risk', 'value', 'effort', 'who'}
MERGE_FIELDS = EDITABLE | {'tier', 'wave', 'section'}
CATEGORIES = {'advised-against', 'no-credible-source', 'vague', 'duplicate', 'simplified'}


def worst(order, vals):
    vals = [v for v in vals if v in order]
    return max(vals, key=order.index) if vals else None


def src_key(s):
    return (s.get('kind'), re.sub(r':\d+(-\d+)?$', '', str(s.get('ref', '')).strip()))


def add_sources(item, new):
    seen = {src_key(s) for s in item.get('sources', [])}
    added = 0
    for s in new or []:
        if not isinstance(s, dict) or not s.get('ref') or not s.get('kind'):
            continue
        if src_key(s) in seen:
            continue
        seen.add(src_key(s))
        item.setdefault('sources', []).append(dict(s, check='unchecked', added_round=K))
        added += 1
    return added


def uniq(seq):
    out, seen = [], set()
    for x in seq:
        k = re.sub(r'\W+', ' ', str(x).lower()).strip()
        if k and k not in seen:
            seen.add(k)
            out.append(x)
    return out


K = int(sys.argv[1])
prev = load(f'{REV}/r{K - 1}.json')
if prev is None:
    print(json.dumps({'round': K, 'error': f'missing r{K - 1}.json'}))
    sys.exit(1)
items = {it['id']: it for it in prev}
order = [it['id'] for it in prev]
removed_log = load(f'{REV}/removed.json', [])
merged_map = load(f'{REV}/merged-map.json', {})
problems = []
stats = {'round': K, 'in': len(items), 'removed': 0, 'edited': 0, 'sources_added': 0,
         'merged_groups': 0, 'merged_away': 0, 'overturned': 0, 'kept': 0}

# --- per-item verdicts ---
verdicts = {}
rdir = f'{REV}/r{K}'
chunk_ids = sorted({re.search(r'chunk-(\d+)\.', os.path.basename(p)).group(1)
                    for p in glob.glob(f'{rdir}/chunk-*.json')}, key=int)
for cid in chunk_ids:
    final = load(f'{rdir}/chunk-{cid}.final.json')
    first = load(f'{rdir}/chunk-{cid}.review.json')
    rows = final if isinstance(final, list) else first
    if not isinstance(rows, list):
        problems.append(f'chunk {cid}: no readable verdict file')
        continue
    if not isinstance(final, list):
        problems.append(f'chunk {cid}: challenger file missing, first review used')
    for row in rows:
        if isinstance(row, dict) and row.get('id') in items:
            verdicts[row['id']] = row
        elif isinstance(row, dict):
            problems.append(f'chunk {cid}: unknown id {row.get("id")}')
missing = [i for i in order if i not in verdicts]
if missing:
    problems.append(f'{len(missing)} items got no verdict and are kept: {" ".join(missing[:30])}')

folds = []
for fid in order:
    v = verdicts.get(fid)
    it = items[fid]
    if not v:
        continue
    if v.get('overturned'):
        stats['overturned'] += 1
    d = v.get('demand_source')
    if isinstance(d, dict) and d.get('ref'):
        stats['sources_added'] += add_sources(it, [d])
        it['demand'] = {'ref': d.get('ref'), 'title': d.get('title', ''), 'supports': d.get('supports', '')}
    verdict = v.get('verdict')
    if verdict == 'remove':
        cat = v.get('category') if v.get('category') in CATEGORIES else 'vague'
        removed_log.append({'id': fid, 'name': it['name'], 'tier': it['tier'], 'round': K, 'category': cat,
                            'reason': v.get('reason', ''), 'fold_into': v.get('fold_into') or '',
                            'sources': [s for s in (v.get('evidence') or []) if isinstance(s, dict) and s.get('ref')][:4]
                            or it.get('sources', [])[:4]})
        if v.get('fold_into'):
            folds.append((fid, v['fold_into'], v.get('fold_note') or v.get('reason', ''), it['name']))
        del items[fid]
        stats['removed'] += 1
        continue
    if verdict == 'park':
        it['wave'] = 'parked'
        it['park_note'] = v.get('park_note') or v.get('reason', '')
        it.pop('wave_condition', None)
        it['history'].append(f'r{K}: parked. {v.get("reason", "")}'.strip())
        stats['parked'] = stats.get('parked', 0) + 1
        continue
    if verdict == 'edit':
        changed = []
        for k, val in (v.get('edits') or {}).items():
            if k in EDITABLE and val not in (None, '', []):
                it[k] = val
                changed.append(k)
        if changed:
            stats['edited'] += 1
            it['history'].append(f'r{K}: edited {", ".join(changed)}. {v.get("reason", "")}'.strip())
        else:
            stats['kept'] += 1
    else:
        stats['kept'] += 1
    if it.get('demand') and not any(h.startswith(f'r{K}: kept') for h in it['history']):
        it['history'].append(f'r{K}: kept; credible mention: {it["demand"].get("title") or it["demand"].get("ref")}')

for fid, target, note, name in folds:
    if target in items:
        items[target].setdefault('adds', []).append(f'From {fid} ({name}): {note}')
        merged_map[fid] = target
    else:
        problems.append(f'fold target {target} for {fid} does not survive; note dropped')

# --- merges ---
merges = load(f'{rdir}/merges.json', [])
if not isinstance(merges, list):
    merges = []
used = set()
for g in merges:
    if not isinstance(g, dict):
        continue
    into = g.get('into')
    members = [m for m in dict.fromkeys(g.get('members') or []) if m in items]
    gone = [m for m in (g.get('members') or []) if m not in items]
    if into not in items:
        problems.append(f'merge into {into}: surviving id was removed or is unknown; skipped')
        continue
    if into not in members:
        members.insert(0, into)
    if any(m in used for m in members):
        problems.append(f'merge into {into}: overlaps an earlier merge; skipped')
        continue
    others = [m for m in members if m != into]
    if not others:
        problems.append(f'merge into {into}: fewer than two surviving members ({" ".join(gone)} gone); skipped')
        continue
    used.update(members)
    base = items[into]
    recs = [items[m] for m in members]
    rec = g.get('record') or {}
    # conservative defaults; the editor's record may restate them but cannot lower risk or readiness
    base['readiness'] = worst(READY_ORDER, [r.get('readiness') for r in recs] + [rec.get('readiness')]) or base.get('readiness')
    base['risk'] = worst(RISK_ORDER, [str(r.get('risk')).lower() for r in recs] + [str(rec.get('risk')).lower()]) or base.get('risk')
    base['effort'] = worst(EFFORT_ORDER, [r.get('effort') for r in recs] + [rec.get('effort')]) or base.get('effort')
    base['value'] = max([int(r.get('value') or 0) for r in recs] + [int(rec.get('value') or 0)])
    for k, val in rec.items():
        if k in MERGE_FIELDS and k not in ('readiness', 'risk', 'effort', 'value') and val not in (None, '', []):
            base[k] = val
    if not rec.get('caveats'):
        base['caveats'] = uniq(sum([r.get('caveats') or [] for r in recs], []))[:8]
    base['unverified'] = uniq(sum([r.get('unverified') or [] for r in recs], []) + list(rec.get('unverified') or []))
    base['corrections'] = uniq(sum([r.get('corrections') or [] for r in recs], []))
    base['review_notes'] = []
    for m in others:
        o = items[m]
        have = {src_key(s) for s in base.get('sources', [])}
        for s in o.get('sources') or []:
            if src_key(s) not in have:
                have.add(src_key(s))
                base.setdefault('sources', []).append(s)
        base['includes'] = base.get('includes', []) + [{'id': m, 'name': o['name']}] + list(o.get('includes') or [])
        base['absorbs'] = list(dict.fromkeys((base.get('absorbs') or []) + [m] + list(o.get('absorbs') or [])))
        base['adds'] = (base.get('adds') or []) + list(o.get('adds') or [])
        merged_map[m] = into
        for old, tgt in list(merged_map.items()):
            if tgt == m:
                merged_map[old] = into
        del items[m]
        stats['merged_away'] += 1
    base['origin'] = 'new' if all(r.get('origin') == 'new' for r in recs) else base.get('origin')
    base['history'].append(f'r{K}: merged with {", ".join(others)} ({g.get("why", "")}). {g.get("note", "")}'.strip())
    stats['merged_groups'] += 1

out = [items[i] for i in order if i in items]
# keep sections contiguous after merges moved items
sec_order = []
for it in prev:
    key = (it['tier'], it['section'])
    if key not in sec_order:
        sec_order.append(key)
for it in out:
    key = (it['tier'], it['section'])
    if key not in sec_order:
        sec_order.append(key)
pos = {i: n for n, i in enumerate(order)}
out.sort(key=lambda it: (it['tier'], sec_order.index((it['tier'], it['section'])), pos[it['id']]))

dump(out, f'{REV}/r{K}.json')
dump(removed_log, f'{REV}/removed.json')
dump(merged_map, f'{REV}/merged-map.json')
write_index(out, K)
stats['out'] = len(out)
stats['chunks'] = write_chunks(out, K)
stats['changes'] = stats['removed'] + stats['edited'] + stats['merged_groups']
stats['problems'] = problems
dump(stats, f'{REV}/r{K}.stats.json')
print(json.dumps(stats))
