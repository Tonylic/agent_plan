#!/usr/bin/env python3
"""Render data/final/catalog.json plus the hand-written frame (frame.json) into the catalog page.

Pipeline: assemble.py (research -> catalog-pre-review.json), review_init.py, apply_review.py K per review round,
finalize_review.py (-> catalog.json), frame.py, then
usage: python3 render.py local > ../home-agent-capability-catalog.html
"""
import html
import json
import os
import re
import sys
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
WF = HERE + '/data'
HEAD = HERE + '/../m1-runbook-src/shell-head.html'

E = html.escape
cat = json.load(open(WF + '/final/catalog.json'))
frame = json.load(open(HERE + '/frame.json'))
F = cat['features']
REMOVED = cat.get('removed', [])
REMOVED_IDS = {r['id'] for r in REMOVED}
ALIASES = cat.get('aliases', {})
ANCHORS = set(F) | REMOVED_IDS | {a for a, t in ALIASES.items() if t in F}
CATS = [('advised-against', 'Advised against', 'A credible source advises against it, or the phone, a vendor app or a free service already does the job better.'),
        ('no-credible-source', 'No credible source', 'No vendor documentation, shipping product, authority or established publication was found that describes it as worth having.'),
        ('vague', 'Vague, or not a feature', 'A note, a decision record or a rule restated, not something that can be built and used. Where the content mattered it was folded into the item named.'),
        ('duplicate', 'Duplicate', 'Fully covered by the item it was folded into.'),
        ('simplified', 'Dropped by an approved simplification', 'Nothing of it was left to build once you approved the simplifications on 12 Oct. Where one line survives, the row says which card carries it.')]


def link(i):
    return f'<a href="#{E(i)}">{E(i)}</a>' if i in ANCHORS else E(i)

READY = {'now': ('Ready now', 'ok'), 'build': ('Needs a build', 'acc'), 'experimental': ('Experimental', 'you'),
         'blocked': ('Blocked today', 'sec'), 'not-recommended': ('Not recommended', 'sec')}
WAVE = {'later': 'Later', 'never': 'Never', 'unplaced': 'Not placed', 'no': 'Not recommended',
        'none': 'Not in a wave yet', 'parked': 'Parked'}
REVIEW_PAGE = 'home-agent-review-confirmation.html'
TIER = {1: 'General capabilities', 2: 'Special capabilities', 3: 'Advanced abilities'}


def code_spans(text):
    """Escape, then turn `x` into <code>x</code>."""
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', E(str(text or '')))
    return re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)


def refs(text):
    """code_spans, plus links from S6 / Q8 / T1 to the review page and from item ids to their cards."""
    t = code_spans(text)
    t = re.sub(r'\b([SQT])(\d{1,2})\b', lambda m: f'<a href="{REVIEW_PAGE}#{m.group(1)}{m.group(2)}">{m.group(0)}</a>', t)
    return re.sub(r'\b((?:F|G)\d{3}|(?:MAC|IPH|WEB|VOX|HOM|AUT|MKT|OCL|SRC|CRT)-\d{2})\b',
                  lambda m: f'<a href="#{m.group(1)}">{m.group(1)}</a>' if m.group(1) in F else m.group(1), t)


def doc_url(path):
    m = re.match(r'^docs/(.+)\.mdx?$', path)
    if not m:
        return None
    p = m.group(1)
    p = re.sub(r'/index$', '', p)
    return 'https://docs.openclaw.ai/' + p


def source_html(s):
    tip = E(s.get('supports', '') or '')
    if s.get('kind') == 'web':
        url = s['ref'].strip()
        host = urlparse(url).netloc.replace('www.', '')
        label = E((s.get('title') or host).strip())
        mark = ' <span class="blk">(site blocks automated re-check)</span>' if s.get('check') == 'bot-blocked' else ''
        return f'<a href="{E(url)}" title="{tip}" rel="noopener">{label}</a> <span class="host">{E(host)}</span>{mark}'
    ref = s['ref'].strip().replace('/opt/homebrew/lib/node_modules/openclaw/', '')
    path = re.sub(r':\d+(-\d+)?$', '', ref)
    url = doc_url(path)
    if url:
        return f'<a href="{E(url)}" title="{tip}" rel="noopener"><code>{E(ref)}</code></a>'
    return f'<code title="{tip}">{E(ref)}</code>'


def is_wave(w):
    return isinstance(w, str) and len(w) == 1 and w.isalpha() and w.isupper()


def wave_label(w):
    return f'Wave {w}' if is_wave(w) else WAVE.get(w, str(w))


def chips(f):
    out = []
    lab, cls = READY.get(f.get('readiness'), (str(f.get('readiness') or 'Unrated'), 'mut'))
    out.append(f'<span class="chip {cls}">{E(lab)}</span>')
    if f.get('risk'):
        rc = {'low': 'mut', 'medium': 'you-o', 'high': 'sec-o'}.get(str(f['risk']).lower(), 'mut')
        out.append(f'<span class="chip {rc}">{E(str(f["risk"]).capitalize())} risk</span>')
    if f.get('who'):
        who = {'adult': 'Adults', 'kid': 'Kids', 'both': 'Adults and kids', 'operator': 'Operator'}.get(str(f['who']).lower(), str(f['who']))
        out.append(f'<span class="chip mut">{E(who)}</span>')
    if f.get('value'):
        out.append(f'<span class="chip mut">Value {E(str(f["value"]))}/5</span>')
    if f.get('effort'):
        out.append(f'<span class="chip mut">Effort {E(str(f["effort"]))}</span>')
    w = f.get('wave')
    if w and w not in ('no',):
        out.append(f'<a class="chip {"acc-o" if is_wave(w) else "mut"}" href="#wave-{E(w)}">{E(wave_label(w))}</a>' if is_wave(w)
                   else f'<span class="chip mut">{E(wave_label(w))}</span>')
    if f.get('origin') == 'new':
        out.append('<span class="chip obs">New</span>')
    return ''.join(out)


def alias_spans(f):
    """Anchors for the old ids this item absorbed, so old links still land here."""
    olds = [m['id'] for m in f.get('includes') or []] + list(f.get('absorbs') or []) + [a for a, t in ALIASES.items() if t == f['id']]
    return ''.join(f'<span class="alias" id="{E(a)}"></span>' for a in dict.fromkeys(olds) if a not in F and a not in REMOVED_IDS)


def card(f, rejected=False):
    fid = f['id']
    parts = [f'<article class="step feat" id="{E(fid)}" data-ready="{E(str(f.get("readiness") or ""))}" '
             f'data-origin="{E(f.get("origin", ""))}" data-wave="{E(str(f.get("wave") or ""))}">']
    parts.append(alias_spans(f))
    parts.append(f'<div class="st-top"><span class="st-id">{E(fid)}</span><h4 class="st-title">{E(f["name"])}</h4></div>')
    parts.append(f'<div class="st-chips">{chips(f)}</div>')
    parts.append('<div class="st-body">')
    if rejected and f.get('reject_reason'):
        parts.append(f'<p><strong>Why not:</strong> {code_spans(f["reject_reason"])}</p>')
    parts.append(f'<p>{code_spans(f.get("description", ""))}</p>')
    if f.get('example'):
        parts.append(f'<p class="why"><em>Example:</em> {code_spans(f["example"])}</p>')
    if f.get('wave_condition'):
        lab = 'Why not yet' if f.get('wave') == 'none' else f'In wave {f.get("wave")}'
        parts.append(f'<p class="inc"><span class="lab-i">{E(lab)}</span> {refs(f["wave_condition"])}</p>')
    if f.get('includes'):
        parts.append('<p class="inc"><span class="lab-i">Combines</span> ' +
                     '; '.join(f'<span class="st-id">{E(m["id"])}</span> {E(m["name"])}' for m in f['includes']) + '</p>')
    d = f.get('demand')
    if d and d.get('ref'):
        src = next((x for x in f.get('sources', []) if x.get('ref') == d['ref']), None) or (d if d.get('kind') else None)
        shown = source_html(src) if src else E(d.get('title') or d['ref'])
        lab = 'Can be built because' if d.get('kind') == 'installed' else 'Backed by'
        parts.append(f'<p class="backed"><span class="lab-i">{lab}</span> {shown}' +
                     (f': {code_spans(d["supports"])}' if d.get('supports') else '') + '</p>')
    more = []
    if f.get('how'):
        more.append(f'<p><span class="lab-i">How</span> {code_spans(f["how"])}</p>')
    if f.get('depends_on'):
        deps = f['depends_on'] if isinstance(f['depends_on'], list) else [f['depends_on']]
        deps = [d for d in deps if str(d).strip()]
        if deps:
            more.append('<p><span class="lab-i">Depends on</span> ' + '; '.join(code_spans(d) for d in deps) + '</p>')
    if f.get('caveats'):
        more.append('<p><span class="lab-i">Limits</span></p><ul>' + ''.join(f'<li>{code_spans(c)}</li>' for c in f['caveats']) + '</ul>')
    if f.get('safety'):
        more.append(f'<p><span class="lab-i">Safety</span> {code_spans(f["safety"])}</p>')
    if f.get('corrections'):
        more.append('<p><span class="lab-i">Corrected since 9 Oct</span></p><ul>' + ''.join(f'<li>{code_spans(c)}</li>' for c in f['corrections']) + '</ul>')
    if f.get('review_notes'):
        more.append('<p><span class="lab-i">Reviewers</span></p><ul>' + ''.join(f'<li>{code_spans(c)}</li>' for c in f['review_notes']) + '</ul>')
    if f.get('adds'):
        more.append('<p><span class="lab-i">Folded in</span></p><ul>' + ''.join(f'<li>{code_spans(a)}</li>' for a in f['adds']) + '</ul>')
    if f.get('unverified'):
        more.append('<p><span class="lab-i">Not verified</span></p><ul>' + ''.join(f'<li>{code_spans(c)}</li>' for c in f['unverified']) + '</ul>')
    named = {m['id'] for m in f.get('includes') or []}
    rest_ids = [a for a in f.get('absorbs') or [] if a not in named]
    if rest_ids:
        more.append('<p><span class="lab-i">Also absorbs</span> ' + ', '.join(E(a) for a in rest_ids) + '</p>')
    if f.get('history'):
        more.append('<p><span class="lab-i">Review</span></p><ul>' + ''.join(f'<li>{code_spans(h)}</li>' for h in f['history']) + '</ul>')
    if f.get('origin') == '9 Oct':
        more.append(f'<p class="why">Build notes from 9 Oct: see {E(fid)} in <code>home-agent-feature-catalog.md</code>.</p>')
    if more:
        parts.append('<details class="more"><summary>How it works and its limits</summary>' + ''.join(more) + '</details>')
    if f.get('sources'):
        srcs = f['sources']
        first, rest = srcs[:6], srcs[6:]
        parts.append('<p class="src"><strong>Sources</strong>' + ' · '.join(source_html(s) for s in first) + '</p>')
        if rest:
            parts.append(f'<details class="more srcmore"><summary>{len(rest)} more sources</summary><p class="src">' +
                         ' · '.join(source_html(s) for s in rest) + '</p></details>')
    else:
        parts.append('<p class="src"><strong>Sources</strong>none survived the re-check; treat as unverified</p>')
    parts.append('</div></article>')
    return '\n'.join(parts)


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def tier_section(t):
    secs = cat['sections'].get(str(t), [])
    n = sum(1 for s in secs for i in s['ids'] if F[i].get('wave') != 'parked')
    out = [f'<section class="sec" id="tier{t}">',
           f'<div class="eyebrow">Tier {t} · {n} items</div>',
           f'<h2>{E(TIER[t])}</h2>']
    out += [f'<p>{code_spans(p.format(t1=n, t2=n, t3=n))}</p>' for p in frame['tier_intro'][str(t)]]
    for s in secs:
        act = [i for i in s['ids'] if F[i].get('wave') != 'parked']
        if not act:
            continue
        out.append(f'<div class="grp"><h3 id="t{t}-{slug(s["title"])}">{E(s["title"])} <span class="n">{len(act)}</span></h3>')
        out += [card(F[i]) for i in act]
        out.append('</div>')
    out.append('</section>')
    return '\n'.join(out)


def counts_table():
    live = [f for f in F.values() if f.get('wave') != 'parked']
    cols = [c for c in ['now', 'build', 'experimental', 'blocked', 'not-recommended'] if any(f.get('readiness') == c for f in live)]
    rows = []
    for t in (1, 2, 3):
        fs = [f for f in live if f['tier'] == t]
        cells = ''.join(f'<td>{sum(1 for f in fs if f.get("readiness") == c) or "–"}</td>' for c in cols)
        new = sum(1 for f in fs if f.get('origin') == 'new')
        rows.append(f'<tr><td><a href="#tier{t}">Tier {t} · {E(TIER[t])}</a></td><td>{len(fs)}</td><td>{new}</td>{cells}</tr>')
    head = '<tr><th>Tier</th><th>Items</th><th>Added 11 Oct</th>' + ''.join(f'<th>{E(READY[c][0])}</th>' for c in cols) + '</tr>'
    return f'<div class="tablewrap"><table>{head}{"".join(rows)}</table></div>'


def waves_section():
    wd = cat.get('waves_def') or {}
    out = []
    for w in wd.get('waves', []):
        est = w.get('estimate') or {}
        ids_ = [i for ph in w.get('phases', []) for i in ph.get('ids', [])]
        out.append(f'<div class="wave" id="wave-{E(w["wave"])}"><h3>Wave {E(w["wave"])} · {E(w["name"])} <span class="n">{len(ids_)} items</span></h3>')
        hrs = est.get('hours', est.get('hours_if_simplified'))
        out.append('<div class="st-chips">'
                   f'<span class="chip acc">About {E(str(hrs))} hours · {E(str(est.get("steps")))} steps</span>'
                   '<span class="chip mut">My estimate</span>' +
                   (f'<span class="chip you-o">{E(str(est.get("hours_as_designed")))} hours as the cards were first written</span>' if est.get('hours_as_designed') else '') + '</div>')
        out.append(f'<p>{refs(w.get("goal", ""))}</p>')
        rel = w.get('relies_on_simplifications') or []
        if rel:
            out.append('<p class="src"><strong>One plan only if</strong>' + ', '.join(refs(x) for x in rel) + ' are taken</p>')
        out.append('<div class="tablewrap"><table><tr><th style="width:24%">Phase</th><th style="width:20%">Items and tests</th><th>Goes live when</th></tr>')
        for ph in w.get('phases', []):
            items_ = ' '.join(link(i) for i in ph.get('ids', [])) or '–'
            tests = ' '.join(refs(x) for x in ph.get('tests', []))
            out.append(f'<tr><td>{E(ph["name"])}</td><td class="used">{items_}{"<br>" + tests if tests else ""}</td><td>{refs(ph.get("goes_live_when", ""))}</td></tr>')
        out.append('</table></div>')
        out.append(f'<p><span class="lab-i">Exit test</span> {refs(w.get("exit_test", ""))}</p>')
        needs = w.get('tony_provides') or w.get('needs_from_tony') or []
        if needs:
            out.append(f'<details class="more"><summary>What you provide at execution ({len(needs)})</summary><ul>' +
                       ''.join(f'<li>{refs(x)}</li>' for x in needs) + '</ul></details>')
        if w.get('gives_way_first'):
            out.append(f'<p><span class="lab-i">Gives way first</span> {refs(w["gives_way_first"])}</p>')
        risks = w.get('new_risks') or []
        if risks:
            out.append(f'<details class="more"><summary>New kinds of risk ({len(risks)})</summary><ul>' +
                       ''.join(f'<li>{refs(x)}</li>' for x in risks) + '</ul></details>')
        out.append('<details class="more"><summary>What each phase builds</summary>' + ''.join(
            f'<p><span class="lab-i">{E(ph["name"])}</span></p><ul>' + ''.join(f'<li>{refs(x)}</li>' for x in ph.get('also_built_here', [])) + '</ul>'
            for ph in w.get('phases', []) if ph.get('also_built_here')) + '</details>')
        if est.get('basis'):
            out.append(f'<details class="more"><summary>How the size was estimated</summary><p>{refs(est["basis"])}</p></details>')
        out.append('</div>')
    parked = [f for f in F.values() if f.get('wave') == 'parked']
    niw = [x for x in (wd.get('not_in_a_wave') or []) if x.get('id') in F and F[x['id']].get('wave') != 'parked']
    if parked:
        out.append(f'<div class="wave" id="wave-parked"><h3>Parked <span class="n">{len(parked)} items</span></h3>'
                   '<p>Not planned. Each comes back when the thing named happens.</p>'
                   '<div class="tablewrap"><table class="rm"><tr><th>Item</th><th>What it is, and what brings it back</th></tr>')
        for f in parked:
            out.append(f'<tr id="{E(f["id"])}"><td>{alias_spans(f)}<span class="st-id">{E(f["id"])}</span> <strong>{E(f["name"])}</strong></td><td>{refs(f.get("park_note", ""))}</td></tr>')
        out.append('</table></div></div>')
    if niw:
        out.append(f'<div class="wave" id="wave-none"><h3>Not in a wave yet <span class="n">{len(niw)} items</span></h3>'
                   '<div class="tablewrap"><table class="rm"><tr><th>Item</th><th>Why</th></tr>')
        for x in niw:
            nm = F[x['id']]['name'] if x['id'] in F else ''
            out.append(f'<tr><td>{link(x["id"])} <strong>{E(nm)}</strong></td><td>{refs(x.get("reason", ""))}</td></tr>')
        out.append('</table></div></div>')
    ops = wd.get('open_points') or []
    if ops:
        out.append(f'<div class="wave" id="open-points"><h3>Open points the waves rest on <span class="n">{len(ops)}</span></h3>'
                   '<p>Each has the default the definition assumes until you answer.</p>'
                   '<div class="tablewrap"><table><tr><th style="width:46%">Point</th><th>Default meanwhile</th><th style="width:12%">Affects</th></tr>')
        for x in ops:
            aff = ' '.join(link(i) if i in ANCHORS else (f'<a href="#wave-{E(i)}">Wave {E(i)}</a>' if i in ('A', 'B', 'C') else E(i)) for i in x.get('affects', []))
            out.append(f'<tr><td>{refs(x["point"])}</td><td>{refs(x.get("default", ""))}</td><td class="used">{aff}</td></tr>')
        out.append('</table></div></div>')
    notes = wd.get('notes') or []
    if notes:
        out.append(f'<details class="more"><summary>Notes on how the definition was reached ({len(notes)})</summary><ul>' +
                   ''.join(f'<li>{refs(x)}</li>' for x in notes) + '</ul></details>')
    return '\n'.join(out)


def all_sources():
    seen = {}
    for f in F.values():
        for s in f.get('sources', []):
            if s.get('kind') == 'web':
                key = s['ref'].strip()
                grp = urlparse(key).netloc.replace('www.', '')
            else:
                key = re.sub(r':\d+(-\d+)?$', '', s['ref'].strip().replace('/opt/homebrew/lib/node_modules/openclaw/', ''))
                grp = 'OpenClaw 2026.9.7, installed files'
            d = seen.setdefault(grp, {})
            d.setdefault(key, {'s': s, 'ids': []})['ids'].append(f['id'])
    groups = sorted(seen.items(), key=lambda kv: (kv[0] != 'OpenClaw 2026.9.7, installed files', -len(kv[1]), kv[0]))
    out, nweb, ninst = [], 0, 0
    for grp, d in groups:
        out.append(f'<h4>{E(grp)} · {len(d)}</h4><ul>')
        for key, v in sorted(d.items()):
            s = dict(v['s'])
            if s.get('kind') != 'web':
                s['ref'] = key
                ninst += 1
            else:
                nweb += 1
            ids = sorted(set(v['ids']))
            used = ' '.join(f'<a href="#{E(i)}">{E(i)}</a>' for i in ids[:8]) + (' …' if len(ids) > 8 else '')
            out.append(f'<li>{source_html(s)} <span class="used">{used}</span></li>')
        out.append('</ul>')
    return '\n'.join(out), ninst, nweb


def main():
    head = open(HEAD).read()
    head = re.sub(r'<title>.*?</title>\n?', '', head, flags=re.S)
    extra_css = open(HERE + '/extra.css').read()
    js = open(HERE + '/catalog.js').read()
    live = [f for f in F.values() if f.get('wave') != 'parked']
    rej = REMOVED
    src_html, ninst, nweb = all_sources()
    stats = dict(frame.get('stats', {}), live=len(live), new=sum(1 for f in live if f.get('origin') == 'new'),
                 old=sum(1 for f in live if f.get('origin') != 'new'), rejected=len(rej), ninst=ninst, nweb=nweb)
    rv = cat.get('review', {})
    stats['merged'] = sum(1 for a, t in ALIASES.items() if a not in REMOVED_IDS)
    stats['removed0'] = sum(1 for r in rej if r.get('round') == 0)
    stats['removed_review'] = sum(1 for r in rej if r.get('round', 0) > 0)
    stats['rounds'] = sum(1 for st in rv.get('rounds', []) if not st.get('label'))
    rc = rv.get('source_recheck', {})
    stats['added'] = sum(rc.values())
    stats['added_ok'] = rc.get('installed ok', 0) + rc.get('web ok', 0)
    stats['added_soft'] = rc.get('web reachable', 0) + rc.get('installed near', 0)
    stats['added_blocked'] = rc.get('web bot-blocked', 0)
    stats['added_bad'] = stats['added'] - stats['added_ok'] - stats['added_soft'] - stats['added_blocked']
    stats['start'] = rv['rounds'][0]['in'] if rv.get('rounds') else len(live)
    for t in (1, 2, 3):
        stats[f't{t}'] = sum(1 for f in live if f['tier'] == t)
    for w in 'ABCDEFGHIJ':
        stats[f'w{w}'] = sum(1 for f in live if f.get('wave') == w)
    stats['wnone'] = sum(1 for f in live if f.get('wave') == 'none')
    stats['parked'] = sum(1 for f in F.values() if f.get('wave') == 'parked')
    stats['inwaves'] = sum(1 for f in live if is_wave(f.get('wave')))
    stats['nwaves'] = len((cat.get('waves_def') or {}).get('waves', []))
    tot = (cat.get('waves_def') or {}).get('totals') or {}
    stats['wave_hours'] = tot.get('hours', '')
    stats['wave_weeks'] = tot.get('weeks_at_8_to_10_hours', '')
    allsrc = [x for f in live for x in f.get('sources', [])]
    stats['src_total'] = len(allsrc)
    stats['src_ok'] = sum(1 for x in allsrc if x.get('check') == 'ok')
    stats['src_soft'] = stats['src_total'] - stats['src_ok']

    def fmt(p):
        return code_spans(p.format(**stats))

    toc = [('glance', 'At a glance', ''), ('tier1', 'Tier 1 · General', sum(1 for f in live if f['tier'] == 1)),
           ('tier2', 'Tier 2 · Special', sum(1 for f in live if f['tier'] == 2)),
           ('tier3', 'Tier 3 · Advanced', sum(1 for f in live if f['tier'] == 3)),
           ('removed', 'Removed in review', len(rej)), ('batch', 'The waves', stats['nwaves']),
           ('decisions', 'Decided so far', ''), ('method', 'How it was checked', ''), ('sources', 'Sources', ninst + nweb)]
    body = []
    body.append('<div class="wrap">')
    body.append(f'<header class="masthead"><div class="eyebrow">{E(frame["eyebrow"])}</div><h1>{E(frame["title"])}</h1>'
                f'<p class="lede">{fmt(frame["lede"])}</p><div class="meta">' + ''.join(f'<span>{E(m.format(**stats))}</span>' for m in frame['meta']) + '</div></header>')
    body.append('<div class="layout"><nav class="toc" aria-label="Contents"><ol>' +
                ''.join(f'<li><a href="#{i}">{E(t)}<span class="cnt">{c}</span></a></li>' for i, t, c in toc) + '</ol></nav><main>')

    # at a glance
    body.append('<section class="sec" id="glance"><div class="eyebrow">Summary</div><h2>At a glance</h2>')
    body += [f'<p>{fmt(p)}</p>' for p in frame['glance_intro']]
    body.append(counts_table())
    for box in frame['answers']:
        body.append(f'<div class="callout {E(box.get("kind", "note"))}"><div class="t">{E(box["label"])}</div>' +
                    ''.join(f'<p>{code_spans(p)}</p>' for p in box['paras']) +
                    (('<p class="src"><strong>See</strong>' + ' · '.join(link(i) for i in box['ids']) + '</p>') if box.get('ids') else '') + '</div>')
    body.append(f'<h3>{E(frame.get("findings_title", "What else the research found"))}</h3><ul class="finds">')
    for fd in frame['findings']:
        ids = ' '.join(link(i) for i in fd.get('ids', []) if i in ANCHORS)
        body.append(f'<li>{fmt(fd["text"])} <span class="used">{ids}</span></li>')
    body.append('</ul>')
    body.append('<h3>How to read a card</h3><div class="legend">' +
                ''.join(f'<span><span class="chip {c}">{E(l)}</span> {E(d)}</span>' for l, c, d in frame['legend']) + '</div>')
    body.append('<h3>What the feature codes mean</h3>')
    body.append(f'<p>{fmt(frame["codes_note"])}</p>')
    body.append('<div class="tablewrap"><table><tr><th>Code</th><th>Round</th><th>Stands for</th><th>Live</th><th>Combined into another</th><th>Removed</th></tr>')
    for code, rnd, text in frame['codes']:
        pat = re.compile(rf'^{code}[-0-9]')
        nlive = sum(1 for i in F if pat.match(i))
        nrem = sum(1 for i in REMOVED_IDS if pat.match(i))
        nmer = sum(1 for a in ALIASES if pat.match(a) and a not in REMOVED_IDS)
        body.append(f'<tr><td><code>{E(code)}</code></td><td>{E(rnd)}</td><td>{code_spans(text)}</td><td>{nlive}</td><td>{nmer or "–"}</td><td>{nrem or "–"}</td></tr>')
    body.append('</table></div>')
    body.append('</section>')

    # filter bar
    body.append('<div class="filter" id="filter" role="group" aria-label="Filter features">'
                '<input type="search" id="q" placeholder="Filter by word or id" aria-label="Filter by word or id">'
                '<span class="fgrp" data-k="ready"><button type="button" data-v="" class="on">All</button>'
                '<button type="button" data-v="now">Ready now</button><button type="button" data-v="build">Needs a build</button>'
                '<button type="button" data-v="experimental">Experimental</button><button type="button" data-v="blocked">Blocked</button></span>'
                '<span class="fgrp" data-k="origin"><button type="button" data-v="" class="on">All</button><button type="button" data-v="new">Added 11 Oct</button></span>'
                '<span class="fcount" id="fcount" aria-live="polite"></span></div>')

    for t in (1, 2, 3):
        body.append(tier_section(t))

    body.append(f'<section class="sec" id="removed" data-count="{len(rej)}"><div class="eyebrow">{len(rej)} items</div><h2>Removed in review</h2>')
    body += [f'<p>{fmt(p)}</p>' for p in frame['rejected_intro']]
    for key, title, blurb in CATS:
        rows = [r for r in rej if r.get('category') == key]
        if not rows:
            continue
        rows.sort(key=lambda r: (r.get('tier') != 3, r.get('tier') or 9, r['id']))
        body.append(f'<h3>{E(title)} <span class="n">{len(rows)}</span></h3><p>{E(blurb)}</p>')
        body.append('<div class="tablewrap"><table class="rm"><tr><th>Item</th><th>Why it was removed</th><th>Source</th></tr>')
        for r in rows:
            srcs = ' · '.join(source_html(x) for x in (r.get('sources') or [])[:2])
            fold = f' Its content now sits in {link(r["fold_final"])}.' if r.get('fold_final') else ''
            when = 'first edition' if r.get('round') == 0 else f'round {r.get("round")}'
            body.append(f'<tr id="{E(r["id"])}"><td><span class="st-id">{E(r["id"])}</span> <strong>{E(r["name"])}</strong>'
                        f'<br><span class="n">tier {E(str(r.get("tier")))} · {when}</span></td>'
                        f'<td>{code_spans(r.get("reason", ""))}{fold}</td><td class="src">{srcs}</td></tr>')
        body.append('</table></div>')
    body.append('</section>')

    body.append('<section class="sec" id="batch"><div class="eyebrow">Build order</div><h2>The waves</h2>')
    body += [f'<p>{fmt(p)}</p>' for p in frame['batch_intro']]
    body.append(waves_section())
    body += [f'<p>{fmt(p)}</p>' for p in frame.get('batch_outro', [])]
    body.append('</section>')

    body.append('<section class="sec" id="decisions"><div class="eyebrow">On record</div><h2>Decided so far</h2>')
    body += [f'<p>{fmt(p)}</p>' for p in frame['decisions_intro']]
    body.append('<div class="tablewrap"><table><tr><th style="width:14%">When</th><th style="width:30%">Decision</th><th>What it means, and what stays open beside it</th></tr>')
    for d in frame['decided']:
        body.append(f'<tr><td>{E(d["when"])}</td><td>{refs(d["what"])}</td><td>{refs(d["detail"])}</td></tr>')
    body.append('</table></div></section>')

    body.append('<section class="sec" id="method"><div class="eyebrow">Method</div><h2>How this was produced and checked</h2>')
    body += [f'<p>{fmt(p)}</p>' for p in frame['method']]
    if frame.get('method_table'):
        body.append('<div class="tablewrap"><table><tr><th>Check</th><th>Result</th></tr>' +
                    ''.join(f'<tr><td>{code_spans(a)}</td><td>{code_spans(b.format(**stats))}</td></tr>' for a, b in frame['method_table']) + '</table></div>')
    if rv.get('rounds'):
        body.append('<h3>The review loop, round by round</h3><div class="tablewrap"><table><tr><th>Round</th><th>Items in</th><th>Removed</th>'
                    '<th>Combined away</th><th>Reworded</th><th>Removals overturned</th><th>Items out</th></tr>')
        for st in rv['rounds']:
            body.append(f'<tr><td>{E(st.get("label") or str(st["round"]))}</td><td>{st["in"]}</td><td>{st["removed"]}</td><td>{st["merged_away"]} in {st["merged_groups"]} groups</td>'
                        f'<td>{st["edited"]}</td><td>{st.get("overturned", 0)}</td><td>{st["out"]}</td></tr>')
        body.append('</table></div>')
    body.append('</section>')

    body.append(f'<section class="sec" id="sources"><div class="eyebrow">{ninst} installed files · {nweb} web pages</div><h2>Sources</h2>')
    body += [f'<p>{fmt(p)}</p>' for p in frame['sources_intro']]
    body.append(f'<div class="sources">{src_html}</div></section>')
    body.append('</main></div></div>')

    title = f'<title>{E(frame["html_title"])}</title>'
    style = head.replace('</style>', extra_css + '\n</style>')
    doc = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
           f'{title}\n{style}</head>\n<body>\n' + '\n'.join(body) + f'\n<script>\n{js}\n</script>\n</body>\n</html>\n')
    if len(sys.argv) > 1 and sys.argv[1] == 'artifact':
        doc = f'{title}\n{style}\n' + '\n'.join(body) + f'\n<script>\n{js}\n</script>\n'
    sys.stdout.write(doc)


if __name__ == '__main__':
    main()
