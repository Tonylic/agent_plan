#!/usr/bin/env python3
"""Hand-written framing for the catalog page. Numbers in braces are filled in by render.py."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

frame = {
    'html_title': 'Happy Capability Catalog',
    'eyebrow': 'Home agent · capability catalog · reviewed edition',
    'title': 'What Happy could do next',
    'lede': ('Everything Happy is planned to gain after M1, in the three tiers you asked for: general capabilities, '
             'special capabilities and advanced abilities. {inwaves} planned features sit in {nwaves} waves, A to J, '
             'each sized as one plan. {parked} are parked and {rejected} were removed along the way, each with its '
             'reason. Every card is in the simplified form you approved on 12 Oct, with your answers applied. On '
             '13 Oct the cards and waves that use a helper were changed to the pattern you said that day you '
             'expect to adopt.'),
    'meta': ['Final waves cut 12 Oct 2026 · helper pattern 13 Oct', 'OpenClaw 2026.9.7 · macOS 27', '{inwaves} planned in {nwaves} waves · {parked} parked',
             'Companion to the roadmap and the 9 Oct catalog'],

    'glance_intro': [
        'Tier 1 is a single ability an agent can be granted, such as fetching a web page or reading a mailbox. '
        'Tier 2 is a family workflow built from those, such as a morning text of what in your mail needs '
        'attention. Tier 3 is acting on a device or on the world beyond chat: a computer, a phone, a browser, '
        'voice, the house.',
        'The table counts the planned features. The wave chip on each card links to the plan it is built in. '
        'Examples on the cards are made up to show the feature; none is a fact about your family. Value and effort '
        'are my estimates.',
    ],
    'answers': [
        {
            'label': 'Can Happy control a computer?', 'kind': 'warn',
            'paras': [
                '**On paper yes; not safely on this Mac\'s own desktop.** OpenClaw has a built-in `computer` tool '
                'that takes screenshots and sends clicks and keystrokes. On macOS it works only through the '
                'separate OpenClaw Mac app, which is not installed here.',
                'Once that app is paired and has its macOS permissions, the grant has no per-action confirmation, '
                'no expiry and no limit to one app, and it works only on an unlocked desktop. On the Mac mini the '
                'only unlocked desktop is Happy\'s own, with Messages signed in, and pairing the app also brings '
                'shell execution and desktop sharing with it.',
                'What is planned: a list of commands no paired device may ever run, built first in wave I '
                '(MAC-04), and, as the last wave, a pilot on a clean, throwaway virtual Mac with one chore you '
                'name (MAC-02, wave J). Its first step tests whether it can work at all, and Happy\'s own desktop '
                'is never used. OpenAI and Anthropic both tell developers to run this kind of tool in an isolated '
                'machine. Printing needs no screen control (F080, wave H).',
            ],
            'ids': ['MAC-04', 'MAC-02', 'F080', 'MAC-12', 'MAC-07'],
        },
        {
            'label': 'Can Happy control a connected idle iPhone?', 'kind': 'warn',
            'paras': [
                '**No.** The OpenClaw iPhone app makes a phone a sensor and a chat client. It has no command to '
                'tap or read other apps, its camera works only while the app is open on screen, and its own '
                'documentation says it is not a computer-control backend.',
                'The only way to tap inside iPhone apps is Apple\'s iPhone Mirroring driven by the Mac `computer` '
                'tool. Apple requires the phone to be signed in to the same Apple Account as the Mac user '
                '(Happy\'s), locked and nearby, and the route inherits every problem in the box above. It was '
                'turned down (IPH-08), with developer automation over a cable (IPH-12) and Apple\'s accessibility '
                'features (IPH-13). Every spare-phone idea was removed in review.',
                'What is planned: the OpenClaw app on your own iPhone, for chat with files and, if it passes its '
                'check, voice (OCL-01, wave I). A phone running the app is a control console for the whole '
                'gateway, not a per-person window, so it is your phone only and Jordan stays on iMessage.',
            ],
            'ids': ['OCL-01', 'MAC-04', 'IPH-08', 'IPH-12', 'IPH-13', 'IPH-02', 'IPH-14'],
        },
    ],
    'findings_title': 'Where things stand',
    'findings': [
        {'text': '**Every planned feature is in a wave.** Ten waves, A to J, about {wave_hours} hours in all by my '
                 'estimate; at 8 to 10 hours a week that is {wave_weeks}. The detail is '
                 'under "The waves".',
         'ids': []},
        {'text': '**A to C are the waves you have seen.** A is mail for your inbox: the 07:00 text with the school '
                 'lines first, "did I get an email about X?", and a daily check that the Google sign-in still '
                 'works. B is Jordan\'s inbox, then public web pages, photos and PDFs. C is typed family facts, '
                 'saved notes, calendar questions, the 21:00 text, reminders and dates from a flyer.',
         'ids': ['G015', 'F051', 'F019', 'F002', 'F041', 'F009', 'F014', 'F007']},
        {'text': '**How helpers get their tools (13 Oct).** You chose it for the mail lookup ("go with the first '
                 'version") and said of later helpers: "Not just email reader, we expect to adopt this pattern (Happy '
                 'main agent hold tools, then dispatch sub-agent to narrow tool selection to do their specific '
                 'work)". On this OpenClaw version a helper '
                 'keeps only the tools its asker is allowed, so each parent\'s own agent is allowed the tools of the '
                 'helpers it starts: the Gmail read tools for its mail reader, the fetch tool for the web helper, '
                 'later the browser, the video reader and the lights and speakers tools. It is told to hand the work '
                 'over and never to use those tools itself, and the helper\'s own shorter list narrows each hand-off. '
                 'What this gives up: for those tools an instruction, checked by tool-call records and planted tests, '
                 'stands where a tool limit stood, until the house-rules plugin in wave C can block the parent\'s '
                 'agent in code, which test T5 has to show is possible. That check is planned for wave C; you chose '
                 'to keep the wave order rather than build it before wave B\'s web helper. Between the two parents '
                 'nothing changes.',
         'ids': ['G015', 'F019', 'F020', 'F076', 'F007']},
        {'text': '**D to J add one new kind of risk each, lowest first.** D keeps an eye on things (hourly weather, '
                 'a day out, a page watch, the conflict watch, a weekly count). E is shared pages and logs. F reads '
                 'harder pages and hears voice memos. G sends beyond the chat (the shared list, email to yourself, '
                 'the group chat). H acts in the house (lights, speakers, printing). I is the app on your iPhone. '
                 'J is the screen-control pilot, alone and last.',
         'ids': ['F018', 'F043', 'F020', 'F030', 'F076', 'OCL-01', 'MAC-02']},
        {'text': '**Missing details block nothing.** On your rule, anything I do not have yet (the school senders, '
                 'which page to watch, which printer, a sending address, a chore for the pilot) is listed under '
                 '"What you provide at execution" for the wave that uses it.',
         'ids': []},
        {'text': '**What can still change a plan is a test result.** Each wave runs the checks that could end or '
                 'shrink a card before it builds on them: whether the Google sign-in lasts past day 8 (wave A), '
                 'whether a hand-off returns its answer and its helper keeps its tools (A, B, F, H), whether a coded '
                 'rule can see what it must check, the calling agent included (C, F, G, H), whether a reminder can '
                 'be created from iMessage at all (C). Each card names its '
                 'fallback. Nothing in the waves has been tried on the Mac yet.',
         'ids': ['G015', 'F007', 'F041']},
        {'text': '**What Jordan gets.** Her own 07:00 mail text and the lookup from wave B, then web answers, '
                 'photos and PDFs, notes, calendar questions, the handbook, the coverage grid, the dose log, voice '
                 'memos, the shared list, email to herself, the group chat, lights and printing. She is not a '
                 'command owner, so timed reminders, flyer reminders and project check-ins are yours only.',
         'ids': ['F007', 'F010', 'AUT-01']},
        {'text': '**Where the plan departs from your roadmap, each on your own answer.** Mail is read on the cloud '
                 'model, with the Zero Data Retention application filed. Mail starts with a gate on the connector '
                 'alone: you accepted one firewall rule, and the wave A runbook found that it has to be a blocking '
                 'rule plus a small local proxy, for which it asks your yes at its step A4. The full outbound '
                 'firewall and proxy arrive in wave B before web reading. The prompt-injection tripwire waits for '
                 'local models. The coded check on who may call an account connector arrives with the house-rules '
                 'plugin in wave C, if test T5 shows it can be written; until then the separation between the two parents rests on tool permissions, an '
                 'explicit deny and two tests, and a parent\'s own agent is kept from the tools it holds for its '
                 'helpers by an instruction, until a coded check takes over in wave C if test T5 allows it.',
         'ids': ['G015', 'F019', 'F007']},
        {'text': '**Children\'s data.** From wave C the two children\'s first names, school years and school '
                 'district go to the cloud model with every chat of a parent\'s own agent. From wave E the dose '
                 'log keeps what was given for 14 days and sends it to the cloud model when read back, behind a '
                 'confirm step at execution. Web searches may carry the town and ages, never names or school.',
         'ids': ['F042', 'CRT-10', 'F019']},
        {'text': '**Parked and dropped.** Two cards are parked: the kids agent, which waits for a local model, and '
                 'the routines card, where nothing is built until one of you names a first routine. Four were '
                 'dropped by simplifications you approved: the notification-policy plugin, texts into the other '
                 'parent\'s chat, the renewals table and the outage notice.',
         'ids': ['F072', 'AUT-06', 'G001', 'G009', 'F063', 'CRT-04']},
    ],
    'legend': [
        ['Ready now', 'ok', 'config or prompt changes only, on what is installed'],
        ['Needs a build', 'acc', 'a plugin, script, account or binary; well trodden'],
        ['Experimental', 'you', 'works in principle; documented as experimental or known to be brittle'],
        ['Blocked today', 'sec', 'the platform or a house rule stops it'],
        ['Wave B', 'acc-o', 'the plan it is built in; the chip links to it'],
        ['New', 'obs', 'first proposed on 11 Oct, not in the 9 Oct catalog'],
    ],
    'codes': [
        ['F', '9 Oct', 'Feature from the first brainstorm (F001 to F087)'],
        ['G', '9 Oct', 'Gap: added by that round\'s completeness critic (G001 to G020)'],
        ['MAC', '11 Oct', 'Controlling a Mac or another computer'],
        ['IPH', '11 Oct', 'iPhone, and phones generally (the Android entries were here too)'],
        ['WEB', '11 Oct', 'Browser and logged-in web actions'],
        ['VOX', '11 Oct', 'Voice, calls and meetings'],
        ['HOM', '11 Oct', 'Smart home and the physical world'],
        ['AUT', '11 Oct', 'Longer-running autonomy and platform features'],
        ['MKT', '11 Oct', 'Market: gaps against real family-assistant products'],
        ['OCL', '11 Oct', 'OpenClaw: capabilities the installed release ships that the catalog did not use'],
        ['SRC', '11 Oct', 'Sources: monitors fed by real public data feeds'],
        ['CRT', '11 Oct', 'Critic: added by the 11 Oct completeness critic'],
    ],
    'codes_note': 'The letters say which line of research proposed an item, not which tier it ended up in. The number '
                  'is the order within that line of research. A combined item keeps the code of its most foundational '
                  'member and lists the others under "Combines".',
    'tier_intro': {
        '1': ['One tool, account or platform ability that an agent can be granted. Your examples were web fetch and '
              'reading email. {t1} are planned.'],
        '2': ['Family workflows, digests and monitors built from tier 1. Your example was watching school email and '
              'notifying you. {t2} are planned.'],
        '3': ['Acting on a device or on the world beyond chat tools. Your examples were a computer and an idle '
              'iPhone. {t3} are planned, each behind the gate its kind of risk needs.'],
    },
    'rejected_intro': [
        '{rejected} items are no longer in the catalog: {removed0} were turned down in the first edition and '
        '{removed_review} in the review rounds and under the simplifications you approved. Each keeps one line '
        'with the reason and a source. Where an item\'s content moved into a surviving card, the row says which.',
    ],
    'batch_intro': [
        'On your rule each wave is one plan: one runbook like M0 and M1, about 15 to 25 hours and at most about 50 '
        'steps, built in phases, with one exit test at the end. Every planned feature is in exactly one wave. Three '
        'designs were drafted from different starting points, judged, merged and audited twice; all three judges '
        'chose the design that orders the waves by kind of risk.',
        'All hours and step counts are my estimates, counted at the M1 runbook\'s rate (49 steps for about 20 '
        'hours). Nothing in the waves has been tried on the Mac. T numbers link to the tests on the review page.',
    ],
    'batch_outro': [
        'Waves A to C have little or no room, so each names the one piece that moves to the next wave if the plan '
        'runs over. Waves I and J are short on purpose: each adds one new kind of risk (a paired device, then '
        'screen control) and they are not merged.',
    ],
    'decisions_intro': [
        'What you have decided, in your words where I have them. Nothing in this catalog is waiting on a decision '
        'from you. The wave A runbook asks your yes or no at its step A4 on what it found while it was written (the '
        'gate with a local proxy, the firewall rule\'s limit to happy\'s own desktop, tokens in the Keychain, the '
        'gog wrapper, OpenClaw\'s own review jobs switched off, and what is kept of the reader\'s records), and '
        'what each wave needs at execution is listed under that wave.',
    ],
    'decided': [
        {'when': '9 Oct', 'what': 'Skip local models for now and expand Happy\'s capabilities in a batch.',
         'detail': 'The kids agent (F072) waits for a local model.'},
        {'when': '11 Oct', 'what': 'Apply to OpenAI for Zero Data Retention.',
         'detail': 'OpenAI\'s data-controls page names no form: the route is its sales contact, approval is '
                   'required and not guaranteed, and once approved it is set per project. Filing it is a step in '
                   'wave A.'},
        {'when': '11 Oct', 'what': 'Jordan is not added to the command list ("no need").',
         'detail': 'The built-in stop words and /status stay yours only, and she is not a command owner, so '
                   'reminders and project check-ins are yours only.'},
        {'when': '11 Oct', 'what': 'Happy reads both parents\' personal Gmail, where school mail already lands, '
                                   'through gog\'s MCP server with a read-only token. No separate school mailbox.',
         'detail': 'The whole-inbox features go with the school lines.'},
        {'when': '12 Oct', 'what': '"For each wave, I expect we could execute in one plan." Mail reading is in wave A.',
         'detail': 'Applied: ten waves, each sized as one plan.'},
        {'when': '12 Oct', 'what': '"Approve all simplifications."',
         'detail': 'All 15 from the review are applied to the cards. Four cards had nothing left to build and '
                   'were dropped.'},
        {'when': '12 Oct', 'what': '"All features." Every feature that had been parked is planned.',
         'detail': 'Eighteen features, each in its simplified form, now sit in waves D to J.'},
        {'when': '12 Oct', 'what': 'Mail, and photos and PDFs you send, may go to the cloud model before OpenAI answers.',
         'detail': 'You also picked the dose log knowing it puts the children\'s health details on the cloud '
                   'model; that card carries a confirm step at execution.'},
        {'when': '12 Oct', 'what': 'Timed reminders: yes. A shared Google calendar. An evening text at 9 pm Eastern.',
         'detail': 'Reminders work for you only. The evening text is one job at 21:00 in the America/New_York zone.'},
        {'when': '12 Oct', 'what': 'Two children, a third-grader and a kindergartner, in one school district. Jordan has agreed to connect her Gmail.',
         'detail': 'Names and the district are kept out of these pages and typed into the family file at execution.'},
        {'when': '12 Oct', 'what': 'Roadmap gates: mail with one firewall rule first is accepted; the outbound proxy is built before web reading; the prompt-injection tripwire waits for local models.',
         'detail': 'Recorded as departures from the roadmap on the sign-off pages of waves A and B.'},
        {'when': '12 Oct', 'what': '"Any concrete information you are missing could be deferred to the execution stage where I would provide. Do not block current stuff."',
         'detail': 'Each missing detail is a "you provide" line in the wave that uses it.'},
        {'when': '13 Oct', 'what': '"Go with the first version", and "we expect to adopt this pattern (Happy main agent hold tools, then dispatch sub-agent to narrow tool selection to do their specific work)".',
         'detail': 'Said after the wave A runbook found that a helper keeps only the tools its asker is allowed. The '
                   'first version: a parent\'s own agent is allowed its helper\'s tools, hands the work over and is '
                   'told never to use them itself. Applied to the mail lookup, the web helper and its extra readers, '
                   'and the home agent; "Not just email reader" were your words. The hard limit comes back only if '
                   'wave C\'s coded check can tell a parent\'s agent from its helper (test T5).'},
        {'when': '13 Oct', 'what': '"That\'s ok, keep as is, as long as we clearly mark the plan to build check in C."',
         'detail': 'Said when asked whether the coded check should be built before wave B\'s web helper, since from '
                   'wave B each parent\'s agent holds the fetch tool for its helper. The wave order stays; the check is '
                   'marked as planned in wave C\'s house-rules phase, and in wave B as not yet there.'},
    ],
    'stats': {'cites': '1,178', 'web_total': 413, 'web_ok': 392, 'web_soft': 11, 'web_blocked': 10,
              'corrections': 77, 'proposed': 154, 'agents': 32, 'review_agents': 88},
    'method': [
        'The first edition (11 Oct) started from the 9 Oct catalog of 105 features. Nine researchers each took one '
        'lens, fourteen reviewers tried to refute their proposals, six more attached sources to the existing '
        'features, a completeness critic added 15, and an editor merged the result: {agents} agents, {start} live '
        'items and {removed0} turned down. Every feature had to cite a source opened in the run: a line in the '
        'installed OpenClaw files, or a first-party or government web page.',
        'On your instruction a review loop then ran over all {start} items for five rounds, with {review_agents} '
        'agents. In each round one reviewer applied three tests to every item: does a credible source advise '
        'against it; does a credible source describe it as worth having (vendor documentation of the capability, a '
        'shipping product, an authority, or an established publication, not just proof that a setting exists); and '
        'is it concrete enough to build. A second reviewer tried to overturn each verdict in both directions. Two '
        'more proposed merges, one looking for the same purpose and one for the same build batch, and an editor '
        'settled them. A script applied the result.',
        'The loop stopped at the five-round limit. Round 5 removed nothing more under those three tests and '
        'combined one pair, though it still reworded 34 cards. Your answers of 11 Oct were then applied, which '
        'reworked the two mail cards and the stop-command card.',
        'On 11 Oct a further review looked for over-engineered design and unbacked assumptions (21 agents; 208 of '
        '221 findings survived a challenge). Its simplifications and questions are on the review page and '
        'were approved by you on 12 Oct. That day every card was rewritten to its simplified form with your '
        'answers (six editors, six checkers, a consistency pass), and the waves were cut twice: first three waves '
        'with 23 items left out, then, after you asked for every feature, ten waves that place all of them '
        '(three designs, three judges, a merge, two audits and a repair pass each time). After each stage a '
        'script, not a model, re-opened the citations.',
        'On 13 Oct, after the wave A runbook was written, twelve cards, eight wave plans (A to H) and the notes '
        'were changed by hand to the helper pattern you said that day you expect to adopt, and the runbook\'s findings on wave A were '
        'noted where they differ from a card. The two pages were then reviewed against each other for '
        'contradictions. Only the five sources added that day were opened by script, and hours and steps were '
        'not re-counted.',
    ],
    'method_table': [
        ['Source per surviving item', '{live} of {live} name one, and the script confirmed each: the file or page opens and contains the cited term (one is a PDF the script could open but not search). 23 of the {live} point at OpenClaw\'s own docs or bundled skills, which shows an item can be built, not that it is worth having'],
        ['Citations on the surviving cards', '{src_ok} of {src_total} were opened by script and contain the cited term; {src_soft} could not be confirmed that way. No script judged whether a page supports the claim'],
        ['Removed for lacking a credible source', '0. Items failed on "advised against", "vague" or "duplicate" first'],
        ['Sources added during the review', '{added} re-opened by script: {added_ok} contained the cited term, {added_soft} opened but could not be searched, {added_blocked} refuse automated requests, {added_bad} failed and were dropped'],
        ['First-edition citations', '{cites} citations of installed files all found the term near the cited line; of {web_total} web pages, {web_ok} matched, {web_soft} opened without a match, {web_blocked} refuse automated requests'],
        ['What was not done', 'No OpenClaw command was run and no device was contacted. gog, the Mac app and the '
                              'iPhone app are not installed, so their behaviour comes from documentation. Some '
                              'findings were read from the installed code or the config repo and need one live '
                              'test; those cards say so.'],
        ['What could not be sourced', 'OpenAI\'s help and terms pages refused every fetch, so the "13+" reason '
                                      'behind the kids rule and any benchmark figure for gpt-6-sol are unverified.'],
        ['What I read myself', 'The summary sections, every removal reason, and the key cards. The long "how it '
                               'works" text on each card is the reviewers\' output, checked by the loop and by '
                               'script, not line by line by me.'],
        ['The 11 Oct section in the Markdown catalog', 'A separate session added "Computer use and device nodes" to '
                                                       '`home-agent-feature-catalog.md`. Its verdict matches. Three '
                                                       'details are corrected here: limited and voice-node pairing '
                                                       'do not confine a phone to one person; a setup code approves '
                                                       'a node\'s first command surface in one step, so the deny '
                                                       'list is the dependable gate; and screen control on the '
                                                       'released Android app is unconfirmed.'],
    ],
    'sources_intro': [
        'Every source cited on a surviving card, grouped by where it lives. Installed files are under '
        '`/opt/homebrew/lib/node_modules/openclaw` on the Mac mini; their links go to the public mirror at '
        'docs.openclaw.ai, which tracks the latest release, so where the two differ the installed file is the '
        'authority. The codes after each source are the items that cite it.',
    ],
}

json.dump(frame, open(HERE + '/frame.json', 'w'), indent=1)
print('frame written')
