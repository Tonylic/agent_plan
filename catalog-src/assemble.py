#!/usr/bin/env python3
"""Assemble the workflow outputs into one catalog JSON (wf/final/catalog.json).

Inputs: the 9 Oct verified catalog, wf/sourcing/*.json, wf/brainstorm/*.json,
wf/verify/*.json, wf/final/decisions.json, wf/final/source-checks.json.
Every rule applied here is mechanical; judgment lives in the inputs.
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WF = HERE + '/data'
PKG = '/opt/homebrew/lib/node_modules/openclaw'
OLD = HERE + '/../.claude/feature-catalog-verified.json'

# ids the 9 Oct catalog folded into a sibling
ABSORBED = {'F008': 'F007', 'F017': 'F028', 'F024': 'F023', 'F035': 'F043', 'F040': 'F011',
            'F057': 'F056', 'F059': 'F060', 'F066': 'F060', 'F065': 'F007', 'F068': 'F064'}
# placement of the 105 in the 9 Oct batch (from the catalog's "Recommended batch" section)
WAVE_OLD = {
    'A': 'G003 G005 G008 G007 G004 F084 F001 F002 F003 G011 F083 F041 F042 F043 F007 F082 F009 G009 F006 F019 F022 F023 F031 F030',
    'B': 'G001 G002 G006 F014 F013 F015 F018 F038 F012 F063 F032 F039 F051 F055 F056 G016 F010 F011 F034 F064 F036 F037 F085 F069',
    'C': 'F020 F021 F025 F026 F027 F028 F029 F049 G014 G020 G010 F033 F080 F076 F077 F078 F081 G015 F047 F048 F016 F052 F053 F060 F061',
    'later': 'F005 F044 F045 F046 F054 F058 F070 F072 F073 F074 F075 G018 G019 F079 G013 G017 G012 F087',
}
BAD = {'file-missing', 'anchor-missing', 'http-error', 'fetch-error', 'bad-url'}


def load(path, default=None):
    try:
        return json.load(open(path))
    except Exception as e:  # noqa: BLE001
        print('WARN cannot load', path, e, file=sys.stderr)
        return default


def skey(s):
    return '|'.join([s.get('kind', ''), s.get('ref', ''), s.get('anchor', '')])


def as_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x) for x in v if str(x).strip()]
    return [str(v)] if str(v).strip() else []


READY_ORDER = ['now', 'build', 'experimental', 'blocked', 'not-recommended']
RISK_ORDER = ['low', 'medium', 'high']
EFFORT_ORDER = ['S', 'M', 'L']
STOP = set('the a an of to and or in on for is are be it its that this with as by at from not no only can cannot'.split())


def toks(s):
    return {w for w in re.findall(r'[a-z0-9_.]+', s.lower()) if w not in STOP and len(w) > 2}


def merge_list(base, extra):
    """Union; a later item that restates an earlier one replaces it."""
    out = list(base)
    for item in extra:
        t = toks(item)
        hit = None
        for i, old in enumerate(out):
            o = toks(old)
            if not t or not o:
                continue
            j = len(t & o) / len(t | o)
            if j >= 0.5 or old[:40].lower() == item[:40].lower():
                hit = i
                break
        if hit is None:
            out.append(item)
        elif len(item) >= len(out[hit]):
            out[hit] = item
    return out


def worst(order, a, b):
    a, b = str(a), str(b)
    if a not in order:
        return b
    if b not in order:
        return a
    return a if order.index(a) >= order.index(b) else b


def main():
    checks = load(WF + '/final/source-checks.json', {})
    # curl gets 404 from ftc.gov; the page was re-fetched by hand on 11 Oct and holds the anchor
    for k, c in checks.items():
        if 'ftc.gov/business-guidance/resources/complying-coppa-frequently-asked-questions' in k and c.get('status') == 'http-error':
            c['status'] = 'bot-blocked'
    decisions = load(WF + '/final/decisions.json', {}) or {}
    feats = {}
    problems = []

    def clean_sources(fid, sources):
        out, seen = [], set()
        for s in sources or []:
            if not isinstance(s, dict) or not s.get('ref'):
                continue
            k = skey(s)
            base = (s.get('kind'), re.sub(r':\d+(-\d+)?$', '', s['ref']))
            c = checks.get(k, {})
            st = c.get('status', 'unchecked')
            if st in BAD:
                problems.append((fid, st, s.get('ref'), s.get('anchor')))
                continue
            if base in seen:
                continue
            seen.add(base)
            out.append(dict(s, check=st))
        return out

    # --- existing 105 ---
    old = {f['id']: f for f in load(OLD, [])}
    sourcing = {}
    for f in sorted(glob.glob(WF + '/sourcing/*.json')):
        for row in load(f, []) or []:
            sourcing[row['id']] = row
    for fid, f in old.items():
        s = sourcing.get(fid, {})
        feats[fid] = {
            'id': fid, 'origin': '9 Oct', 'name': f['name'],
            'tier': s.get('tier') or {'L1': 1, 'L2': 2, 'L3': 2}[f['level']],
            'cluster': f['cluster'],
            'description': s.get('one_line') or f['description'],
            'example': '', 'how': s.get('how_short') or f.get('needs', ''),
            'who': f.get('users', ''), 'risk': f.get('risk', ''),
            'readiness': s.get('readiness') or ('now' if f.get('dependency') == 'now' else 'build'),
            'dependency_old': f.get('dependency', ''),
            'value': f.get('value'), 'effort': f.get('effort'),
            'caveats': [], 'corrections': as_list(s.get('corrections')), 'unverified': as_list(s.get('unverified')),
            'safety': '', 'sources': list(s.get('sources') or []), 'absorbs': [], 'adds': [],
        }
    for wave, ids in WAVE_OLD.items():
        for fid in ids.split():
            if fid in feats:
                feats[fid]['wave'] = wave
    for child, parent in ABSORBED.items():
        if child in feats and parent in feats:
            feats[parent]['absorbs'].append(child)
            feats[parent]['sources'] += feats[child]['sources']
            del feats[child]

    # --- new features with reviewer verdicts ---
    verdicts = {}
    for f in sorted(glob.glob(WF + '/verify/*.json')):
        lens = os.path.basename(f).split('.')[1]
        for v in load(f, []) or []:
            verdicts.setdefault(v.get('id'), []).append(dict(v, lens=lens))
    rejected = {}
    for f in sorted(glob.glob(WF + '/brainstorm/*.json')):
        for feat in load(f, []) or []:
            fid = feat['id']
            feat = dict(feat, origin='new', absorbs=[], adds=[])
            feat['caveats'] = as_list(feat.get('caveats'))
            feat['unverified'] = as_list(feat.get('unverified'))
            feat['sources'] = list(feat.get('sources') or [])
            reasons, notes = [], []
            # security lens first; the fact-check lens then wins on mechanism text
            order = {'security-and-realism': 0, 'combined': 1, 'sources-and-feasibility': 2}
            for v in sorted(verdicts.get(fid, []), key=lambda v: order.get(v['lens'], 1)):
                corr = v.get('corrections') or {}
                for k, val in corr.items():
                    if k in ('caveats', 'unverified', 'depends_on'):
                        feat[k] = merge_list(as_list(feat.get(k)), as_list(val))
                    elif k == 'sources':
                        continue
                    elif k == 'readiness':
                        feat[k] = worst(READY_ORDER, feat.get(k), val) if v['lens'] != 'combined' and feat.get('_r') else val
                        feat['_r'] = True
                    elif k == 'risk':
                        feat[k] = worst(RISK_ORDER, str(feat.get(k)).lower(), str(val).lower())
                    elif k == 'effort':
                        feat[k] = worst(EFFORT_ORDER, feat.get(k), val)
                    elif k == 'value':
                        try:
                            feat[k] = min(int(feat.get(k) or 5), int(val)) if feat.get('_v') else int(val)
                        except (TypeError, ValueError):
                            pass
                        feat['_v'] = True
                    elif k == 'safety' and v['lens'] == 'sources-and-feasibility' and feat.get('_s'):
                        continue  # keep the security reviewer's wording
                    else:
                        feat[k] = val
                        if k == 'safety':
                            feat['_s'] = True
                removed = set(as_list(v.get('removed_sources')))
                feat['sources'] = [s for s in feat['sources'] if s.get('ref') not in removed]
                feat['sources'] += list(v.get('added_sources') or [])
                if v.get('reason') and v.get('verdict') in ('revise', 'reject'):
                    notes.append(v['reason'])
                if v.get('verdict') == 'reject':
                    reasons.append(v.get('reason', ''))
            for k in ('_r', '_v', '_s'):
                feat.pop(k, None)
            feat['review_notes'] = notes
            feat['reviewed_by'] = len(verdicts.get(fid, []))
            if reasons:
                rejected[fid] = ' '.join(r for r in reasons if r)
            feats[fid] = feat

    # --- editor decisions ---
    for d in decisions.get('duplicates', []) or []:
        drop, into = d.get('drop'), d.get('into')
        if drop in feats and into in feats and drop != into:
            feats[into]['sources'] += feats[drop]['sources']
            if d.get('adds'):
                feats[into]['adds'].append(d['adds'])
            feats[into]['absorbs'].append(drop)
            rejected.pop(drop, None)
            del feats[drop]
    for fid, t in (decisions.get('tier_overrides') or {}).items():
        if fid in feats:
            feats[fid]['tier'] = int(t)
    for fid, w in (decisions.get('placement') or {}).items():
        if fid in feats and feats[fid]['origin'] == 'new':
            feats[fid]['wave'] = w
    for r in decisions.get('rejected', []) or []:
        if r.get('id') in feats:
            rejected.setdefault(r['id'], r.get('reason', ''))
            if r.get('reason'):
                feats[r['id']]['reject_reason'] = r['reason']
    for fid, reason in rejected.items():
        if fid in feats:
            feats[fid]['rejected'] = True
            feats[fid].setdefault('reject_reason', reason)
            feats[fid]['wave'] = 'never' if feats[fid].get('wave') == 'never' else 'no'
            if feats[fid].get('readiness') not in ('blocked', 'not-recommended'):
                feats[fid]['readiness'] = 'not-recommended'

    for fid, f in feats.items():
        f['sources'] = clean_sources(fid, f['sources'])
        try:
            f['tier'] = int(f.get('tier') or 2)
        except (TypeError, ValueError):
            f['tier'] = 2
        f.setdefault('wave', 'unplaced' if f['origin'] == '9 Oct' else 'later')

    # --- sections ---
    placed, sections = set(), {}
    for tier in ('1', '2', '3'):
        sections[tier] = []
        for sec in (decisions.get('sections') or {}).get(tier, []) or []:
            ids = [i for i in sec.get('ids', []) if i in feats and i not in placed and not feats[i].get('rejected')]
            for i in ids:
                feats[i]['tier'] = int(tier)
            placed.update(ids)
            if ids:
                sections[tier].append({'title': sec.get('title', 'Other'), 'ids': ids})
    left = [i for i, f in feats.items() if i not in placed and not f.get('rejected')]
    for i in left:
        t = str(feats[i]['tier'])
        sec = next((s for s in sections[t] if s['title'] == 'Other'), None)
        if not sec:
            sec = {'title': 'Other', 'ids': []}
            sections[t].append(sec)
        sec['ids'].append(i)

    out = {
        'features': feats, 'sections': sections,
        'rejected': sorted(i for i, f in feats.items() if f.get('rejected')),
        'findings': decisions.get('findings', []), 'new_decisions': decisions.get('new_decisions', []),
        'contradictions': decisions.get('contradictions', []),
    }
    json.dump(out, open(WF + '/final/catalog-pre-review.json', 'w'), indent=1)

    live = [f for f in feats.values() if not f.get('rejected')]
    print('features total', len(feats), 'live', len(live), 'rejected', len(out['rejected']), 'unplaced->Other', len(left))
    for t in (1, 2, 3):
        print(' tier', t, sum(1 for f in live if f['tier'] == t))
    nosrc = [f['id'] for f in feats.values() if not f['sources']]
    print('features with NO surviving source:', len(nosrc), ' '.join(nosrc))
    print('sources dropped by the mechanical check:', len(problems))
    for p in problems:
        print('  ', p)


if __name__ == '__main__':
    main()
