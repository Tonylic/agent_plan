#!/usr/bin/env python3
"""Render the over-engineering and assumptions review (data/review/oe/summary.json) as a confirmation page.

usage: python3 render_confirm.py > ../home-agent-review-confirmation.html
"""
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E = html.escape
S = json.load(open(HERE + '/data/review/oe/summary.json'))
LIVE = set(json.load(open(HERE + '/data/final/catalog.json'))['features'])
CATALOG = 'home-agent-capability-catalog.html'
try:
    ANSWERS = json.load(open(HERE + '/data/review/oe/answers.json'))
except OSError:
    ANSWERS = {}
RELIES = {}
try:
    for _w in json.load(open(HERE + '/data/review/waves/final.json'))['waves']:
        for _r in _w.get('relies_on_simplifications') or []:
            _m = re.match(r'S\d+', _r)
            if _m:
                RELIES.setdefault(_m.group(0), []).append(_w['wave'])
except OSError:
    pass


def answered(code):
    if code not in ANSWERS:
        return ''
    return f'<p class="backed"><span class="chip ok">Answered</span> {t(ANSWERS[code])}</p>'


def t(text):
    x = re.sub(r'`([^`]+)`', r'<code>\1</code>', E(str(text or '')))
    return re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', x)


def ids(lst):
    out = []
    for i in lst or []:
        out.append(f'<a href="{CATALOG}#{E(i)}">{E(i)}</a>' if i in LIVE else E(i))
    return ' '.join(out)


INTRO = [
    'You asked for one more review, of over-engineered design and of anything I assumed without backing, to be '
    'confirmed with you before anything changes. Two reviewers read every card, one for each question; a third '
    'looked at the plan as a whole and at my own summary; a challenger then tried to refute each finding against '
    'your roadmap, the sources and what you have actually said. {up} of {tot} findings survived. **Nothing in the '
    'catalog has been changed.**',
]
VERDICT = [
    '**The catalog is over-built for two adults.** By the reviewers\' count the 42 cards together ask for about 18 '
    'in-house plugins, hook sets and wrappers. Your roadmap describes one small rule plugin, and the config repo '
    'holds one plugin today.',
    '**About fifteen cards rest on family facts nobody gave.** The config repo records two adults and a home town. '
    'Children aged 8 and 10, a soccer team, a sitter, grandparents, replies in Chinese, a shared Google calendar and '
    'a shared grocery list all came from agents\' example texts.',
    '**The order is wrong for what you keep asking about.** Nineteen wave A items sit in front of mail. The review '
    'proposes mail first, for your inbox, then one item at a time, each live only after its own test.',
    '**Your roadmap\'s safety gates dropped out of the build order.** The outbound firewall and proxy rules it calls '
    'not optional are in no card and not in the config repo, and nothing on record waives them.',
]
MINE = [
    'I marked mail on the cloud model as decided. You agreed to apply for Zero Data Retention and chose the '
    'connector and the wave; whether real mail is read before OpenAI answers is still yours to decide.',
    'I read "no need" as "Jordan needs another way to stop Happy" and kept a stop plugin with a lock-out phrase '
    'under Decided. You only said not to add her to the command list.',
    'I recommended the shared Reminders list as her route for reminders. It has never been tested and nobody has '
    'said the family shares a list.',
    'The photo and PDF privacy gate is described as "the condition Tony set". It was my proposal inside a question.',
    'Value scores, effort sizes and waves are shown as facts. They are estimates by agents.',
    '"Every cited source was re-opened by script" should read: 481 of 496 citations on the surviving cards were '
    'opened and contain the cited term; 15 could not be confirmed that way, and no script judged whether a page '
    'supports the claim.',
    '23 of the 42 "Backed by" lines point at OpenClaw\'s own docs or bundled skills. That shows an item can be '
    'built, not that it is worth having, which is why that test removed nothing.',
]
HOW = ('Every simplification and every question on this page was answered on 12 Oct; the answers are shown on '
       'each one. The page is now the record of what was proposed and what you decided. The catalog page has the '
       'result: the rewritten cards and the ten waves.')


def main():
    head = open(HERE + '/../m1-runbook-src/shell-head.html').read()
    head = re.sub(r'<title>.*?</title>\n?', '', head, flags=re.S)
    css = open(HERE + '/extra.css').read() + '''
.q{border-left:3px solid var(--you)}
.s{border-left:3px solid var(--accent)}
.kv2{display:grid;grid-template-columns:110px minmax(0,1fr);gap:6px 14px;font-size:15px;margin:8px 0 4px}
.kv2 dt{font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);padding-top:3px}
.kv2 dd{margin:0}
@media (max-width:600px){.kv2{grid-template-columns:1fr}}
ol.slice li{margin-bottom:10px;max-width:84ch}
'''
    c = S.get('counts', {})
    up, ov = c.get('findings_upheld', 0), c.get('findings_overturned', 0)
    b = ['<div class="wrap">']
    b.append('<header class="masthead"><div class="eyebrow">Home agent · catalog review · to confirm</div>'
             '<h1>What to simplify, and what only you can answer</h1>'
             f'<p class="lede">{t(INTRO[0].format(up=up, tot=up + ov))}</p>'
             f'<div class="meta"><span>11 Oct 2026</span><span>{len(S["simplifications"])} simplifications</span>'
             f'<span>{len(S["questions"])} questions</span><span>{len(S["tests_first"])} tests first</span>'
             f'<span>{len(S["wording_fixes"])} wording fixes</span></div></header>')
    toc = [('short', 'The short version'), ('slice', 'Proposed first slice'), ('simp', 'Simplifications'),
           ('ques', 'Questions for you'), ('tests', 'Tests first'), ('words', 'Wording fixes'), ('limits', 'Limits')]
    b.append('<div class="layout"><nav class="toc" aria-label="Contents"><ol>' +
             ''.join(f'<li><a href="#{i}">{E(x)}</a></li>' for i, x in toc) + '</ol></nav><main>')

    b.append('<section class="sec" id="short"><div class="eyebrow">Summary</div><h2>The short version</h2><ul class="finds">' +
             ''.join(f'<li>{t(v)}</li>' for v in VERDICT) + '</ul>')
    b.append('<h3>What I got wrong</h3><ul class="finds">' + ''.join(f'<li>{t(v)}</li>' for v in MINE) + '</ul>')
    b.append(f'<div class="callout note"><div class="t">Status</div><p>{t(HOW)}</p></div></section>')

    fs = S.get('first_slice') or {}
    b.append('<section class="sec" id="slice"><div class="eyebrow">Build order</div><h2>Proposed first slice</h2>')
    b.append(f'<div class="callout note"><div class="t">Superseded on 12 Oct</div><p>You kept the waves and asked that each wave be one plan, '
             f'with mail reading in wave A. The waves were redefined on that rule: see <a href="{CATALOG}#batch">The waves</a> on the '
             'catalog page. The reviewers\' original proposal is kept below for the record.</p></div>')
    b.append(f'<p>{t(fs.get("why", ""))}</p>')
    needs = fs.get('needs', '')
    parts = re.split(r'\s*\((\d)\)\s+', needs)
    if len(parts) > 2:
        b.append(f'<p>{t(parts[0])}</p><ol class="slice">')
        for k in range(1, len(parts) - 1, 2):
            b.append(f'<li>{t(parts[k + 1])}</li>')
        b.append('</ol>')
    else:
        b.append(f'<p>{t(needs)}</p>')
    b.append(f'<p class="src"><strong>Items</strong>{ids(fs.get("ids"))}</p></section>')

    b.append(f'<section class="sec" id="simp"><div class="eyebrow">{len(S["simplifications"])} proposals</div><h2>Simplifications</h2>'
             '<p>Each removes machinery. "Saves" is a rough size, not hours. Every one was checked once more against '
             'your roadmap\'s hard rules.</p>')
    for n, x in enumerate(S['simplifications'], 1):
        conf = 'ok' if x.get('confidence') == 'high' else 'you'
        b.append(f'<article class="step feat s" id="S{n}"><div class="st-top"><span class="st-id">S{n}</span>'
                 f'<h4 class="st-title">{E(x["title"])}</h4></div>'
                 f'<div class="st-chips"><span class="chip acc">Saves {E(str(x.get("saves")))}</span>'
                 f'<span class="chip {conf}">{E(str(x.get("confidence", "")).capitalize())} confidence</span>' +
                 ''.join(f'<a class="chip acc-o" href="{CATALOG}#wave-{w}">Wave {w} relies on this</a>' for w in RELIES.get(f'S{n}', [])) + '</div>' +
                 answered(f'S{n}') +
                 ''
                 f'<dl class="kv2"><dt>Today</dt><dd>{t(x["today"])}</dd><dt>Instead</dt><dd>{t(x["instead"])}</dd>'
                 f'<dt>You give up</dt><dd>{t(x["gives_up"])}</dd></dl>' +
                 (f'<details class="more"><summary>Technical note</summary><p>{t(x["detail"])}</p></details>' if x.get('detail') else '') +
                 f'<p class="src"><strong>Cards</strong>{ids(x.get("ids"))}</p></article>')
    b.append('</section>')

    b.append(f'<section class="sec" id="ques"><div class="eyebrow">{len(S["questions"])} questions</div><h2>Questions for you</h2>'
             '<p>Things only you know or can decide, most consequential first. Each has the default the catalog '
             'will use if you leave it unanswered.</p>')
    for n, x in enumerate(S['questions'], 1):
        b.append(f'<article class="step feat q" id="Q{n}"><div class="st-top"><span class="st-id">Q{n}</span>'
                 f'<h4 class="st-title">{t(x["question"])}</h4></div>' + answered(f'Q{n}') +
                 f'<dl class="kv2"><dt>Why it matters</dt><dd>{t(x["why"])}</dd><dt>Default</dt><dd>{t(x["default"])}</dd></dl>'
                 f'<p class="src"><strong>Cards</strong>{ids(x.get("ids"))}</p></article>')
    b.append('</section>')

    b.append(f'<section class="sec" id="tests"><div class="eyebrow">{len(S["tests_first"])} tests</div><h2>Tests to run before relying on it</h2>'
             '<p>Software behaviour the design leans on that nobody has tried. These become the first step of the '
             'card they belong to; they need no answer from you now.</p>'
             '<div class="tablewrap"><table><tr><th>#</th><th>What is unproven</th><th>The test</th><th>Cards</th></tr>')
    for n, x in enumerate(S['tests_first'], 1):
        b.append(f'<tr id="T{n}"><td>T{n}</td><td>{t(x["what"])}</td><td>{t(x["test"])}</td><td class="used">{ids(x.get("ids"))}</td></tr>')
    b.append('</table></div></section>')

    b.append(f'<section class="sec" id="words"><div class="eyebrow">{len(S["wording_fixes"])} fixes</div><h2>Wording fixes</h2>'
             '<p>Places where a card or my summary states an assumption as a fact, or a recommendation as a '
             'decision. Fixable by rewording, with no decision from you.</p>'
             '<div class="tablewrap"><table><tr><th>Where</th><th>What it says now</th><th>Fix</th></tr>')
    for x in S['wording_fixes']:
        who = f'<a href="{CATALOG}#{E(x["id"])}">{E(x["id"])}</a>' if x['id'] in LIVE else E(x['id'])
        b.append(f'<tr><td><span class="st-id">{who}</span><br><span class="n">{t(x.get("where", ""))}</span></td>'
                 f'<td>{t(x["now"])}</td><td>{t(x["fix"])}</td></tr>')
    b.append('</table></div></section>')

    b.append('<section class="sec" id="limits"><div class="eyebrow">Method</div><h2>Limits of this review</h2><ul class="finds">' +
             ''.join(f'<li>{t(n)}</li>' for n in S.get('notes', [])) + '</ul></section>')
    b.append('</main></div></div>')
    js = '''(function(){var links=[].slice.call(document.querySelectorAll('nav.toc a[href^="#"]'));
var secs=links.map(function(a){return document.getElementById(a.getAttribute('href').slice(1));}).filter(Boolean);
if('IntersectionObserver' in window&&secs.length){var io=new IntersectionObserver(function(es){es.forEach(function(en){
if(en.isIntersecting){links.forEach(function(a){a.classList.toggle('active',a.getAttribute('href')==='#'+en.target.id);});}});},
{rootMargin:'-20% 0px -70% 0px'});secs.forEach(function(s){io.observe(s);});}})();'''
    style = head.replace('</style>', css + '\n</style>')
    sys.stdout.write('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                     '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                     '<title>Catalog Review: To Confirm</title>\n' + style + '</head>\n<body>\n' + '\n'.join(b) +
                     f'\n<script>\n{js}\n</script>\n</body>\n</html>\n')


if __name__ == '__main__':
    main()
