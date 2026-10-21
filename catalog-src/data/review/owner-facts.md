# What Tony has actually said or decided

Compiled 11 Oct 2026 by Claude Code from this project's records and conversations. A claim about the family,
its preferences or its priorities counts as BACKED only if it appears here, in the roadmap text as a decision
marked "By: You", or in the config repo (~/src/happy-config). Everything else in the catalog is an assumption
made by an agent, however reasonable it sounds.

## Said in the catalog conversations (10 and 11 Oct 2026)
- M0 and M1 are finished. He chose to skip M2 (local models) for now and expand Happy's capabilities in a batch.
- He wants three levels: general capabilities (his examples: web fetch, reading emails), special capabilities
  (his example: monitoring school emails and notifying), advanced abilities (his examples: controlling a
  computer, and a connected idle iPhone).
- "Be realistic and reasonable. All should be coming from real and authentic and verifiable sources."
- Review instruction: "Remove vague and low-value items (no credible source mentioned it, or people mentioned
  it but advised against it). Remove duplicate and combine similar items if they serve same purpose or could
  be complete rather in the same batch."
- He agreed to apply to OpenAI for Zero Data Retention.
- "No need" to add Jordan to the command allowlist.
- "All school related emails are going into our personal Gmail, which eventually you would need to read."
  School mail arrives in both parents' Gmail.
- Use an existing Gmail connector with a token, not a new mailbox and not a password. He agreed to gog.
- Move the whole-inbox mail features to wave B: "once having the whole email inbox read, school digest would
  be very trivial".
- He now asks for a review "focusing on over-engineering design or anything you assumed with no backup
  reasons", to be confirmed with him before anything changes.

## Said on 12 Oct 2026, about the build order
- The assistant proposed replacing the waves with "mail first, then one item at a time, the rest a pick list".
  Tony's reply, quoted: "Then you must change the wave definition. For each wave, I expect we could execute in
  one plan. If you say we should do mail read now, then just change wave A to include it." Earlier the same day:
  "I thought we do wave A to C?"
- So: the waves stay. Each wave must be executable as ONE plan. Mail reading goes into wave A. He thinks of the
  waves as A to C.
- What "one plan" has meant in this project so far: one runbook like M0 (50 steps) and M1 (49 steps in nine
  phases whose own time estimates add up to about 20 hours), written for 8 to 10 hours of work a week, with one
  exit gate at the end. The roadmap's milestones are two weeks each (one is five).
- Later on 12 Oct, after seeing the redefined waves, Tony's words: "Approve all simplifications. Yes mail could
  go to the cloud model. What other outstanding questions do you need? The goal is to make sure all planned
  features are going into concrete wave plan."
- So: ALL 15 simplifications (S1 to S15 in data/review/oe/summary.json) are APPROVED. S13 is approved in the
  form that fits his wave rule: the waves stay, and the items it names are parked with one line each unless
  the wave definition already holds them (F028 in its small form, F049 as a fill-in).
- Q8 part 1 is answered YES: real mail may go to the cloud model before OpenAI answers on Zero Data Retention.
  He said this about mail only. Photos and PDFs (Q8 part 2) and children's health details (Q8 part 3) are
  NOT answered.
- With S1 approved, the roadmap's coded check on who may call the mail connector waits until the house-rules
  plugin is first created; until then that separation rests on tool permissions, an explicit deny and two tests.
- His goal: every feature that stays planned is in a concrete wave plan. A parked item is not a planned feature
  until he says he wants it.
## Tony's answers of 12 Oct 2026 (later the same day), in his words where quoted
He was shown seven questions and a table of 18 parked features. His replies:
1. Which parked features to plan: "All features." So ALL 18 are now planned features and each needs a wave:
   F003 voice memos in and spoken replies out; F006 Happy in a group chat with both parents (he was told this
   re-opens group chats, off since M1); F030 Happy adds to a shared Apple Reminders list; F043 a shared family
   handbook both agents can search; CRT-13 emergency card, sitter sheet and school-form kit; CRT-10 the
   sick-day "what was given" log (he was told it puts children's health details on the cloud model);
   CRT-11 childcare coverage planner; MKT-06 calendar conflict watch; F033 dinner plan to grocery list;
   F076 lights and speakers by text; F080 printing; OCL-01 the OpenClaw app on his iPhone (a first paired
   device); AUT-01 multi-day project check-ins; F020 a reader for pages that need JavaScript, and video and
   podcast summaries; F018 watching a page or feed he names; G006 a weekly "what Happy did" text;
   F049 "email me this"; MAC-02 a screen-control pilot on a clean virtual machine.
   Each is planned in the SIMPLIFIED form the review described (the approved simplifications still hold: for
   example the weekly text is the smallest no-model form, watchers start with one named feed, the house-device
   card loses its Home Assistant, TV and announcement branch, the iPhone app loses realtime cloud voice).
2. Timed reminders from Happy: "Yes." (They work for him only; Jordan is not a command owner.)
3. Calendar: "Google calendar. Evening text at 9pm EST." The family shares a Google calendar; one evening text
   at 21:00 Eastern time (the config uses the America/New_York zone).
4. Family facts: two children, one in 3rd grade and one in kindergarten, in one school district. Tony gave their
   first names and the district's name to the assistant; they are entered into the family file at execution.
   DO NOT write the children's names or the district's name into any catalog page, card or output: say "the
   two children", "the third-grader", "the kindergartner", "the school district". "I can give you the email
   address once we are on the execution" (the school senders).
   Not stated: a second language (so English only), team or activity apps, camps, a sitter, grandparents.
5. Jordan: "Yes. She's agreed." She connects her own Gmail and gets the 07:00 text.
6. Photos and PDFs to the cloud model before OpenAI answers on data retention: "Yes."
7. Roadmap safety gates: (a) "accept": mail is read with one firewall rule before the full firewall and proxy
   exist; (b) "yes outbound proxy": the outbound proxy is built before web reading; (c) "Yes wait for local
   models": the prompt-injection tripwire is waived until local models exist.
His general rule, quoted: "any concrete information you are missing could be deferred to the execution stage
where I would provide. Do not block current stuff". So a missing concrete detail (a sender address, which
printer, which page to watch, a sending account, a chore for the screen-control pilot, which Reminders list)
NEVER parks an item or makes a wave conditional: the plan carries a step "Tony provides X" at execution.

Defaults he was told would apply and did not change: one mail text at 07:00; Jordan has no stop phrase of her
own and is not a command owner; the recovery card is a half page with no envelope; web searches may include
the town and the children's ages but never names or school; kids stay off cloud models as a house rule;
no chat excerpts kept overnight. "Children's health details not stored" was also on that list, but he picked
the dose log (CRT-10) knowing it puts those details on the cloud model, so for CRT-10 that default is
overridden and the plan carries a confirm step at execution.
The assistant's reading, which he did not contradict: with S1 approved the coded check on the mail connector
waits for the house-rules plugin, so "did I get an email about X?" is built in wave A.

Not planned (still parked): the kids agent F072, which waits for a local model (his answer 7c and the house
rule), and AUT-06, where nothing is built until a parent names a first routine (S12). Dropped by approved
simplifications: the notification-policy plugin (S4), texts into the other parent's chat and the relay (S5),
the renewals table (S11), the outage notice (S14).

## Said on 13 Oct 2026, about how helpers get their tools

Context: the wave A runbook had found that on OpenClaw 2026.9.7 an agent started by another keeps only the
tools its asker is allowed, so the mail lookup as first designed could not work. Tony asked what the concern
with mail privacy was, why not simply a Gmail MCP, and what a redesign would look like. Claude described two
versions: (1) the parent's own agent is allowed the helper's tools and helpers do the reading; (2) the
parent's agent holds nothing and helpers hold the tools, which OpenClaw's own hand-off cannot do.

- "I think the ideal architecture is that everything going through main agent Happy, and then happy dispatch
  subagent to do their things like you dispatch sub-agent here?"
- On binding a second iMessage thread to the mail reader: "This is not the way, say in future we have another
  agent, I don't have that many iMessage handle to bound."
- "yes, go with the first version and update the runbook. Also update the catalog HTML to reflect this. Not
  just email reader, we expect to adopt this pattern (Happy main agent hold tools, then dispatch sub-agent to
  narrow tool selection to do their specific work)"
- "Then do a review loop on both wave A runbook and catalog HTML (up to 5) to make sure no contradictory
  information."
- Asked whether to build the coded check before wave B's web helper (from wave B each parent's agent holds
  the fetch tool for its helper): "That's ok, keep as is, as long as we clearly mark the plan to build check in C."

Not stated by Tony (Claude's reading or proposal): that the house-rules plugin's who-may-call rule gets a
second half blocking a parent's own agent from the tools it holds for helpers; that the home agent's tools
get such a rule in wave H; the planted mail that asks the parent's agent to search the mailbox itself. He has
not ruled on the wave A runbook's other findings (the gate with a local proxy, the firewall rule's screen
limit, tokens in the Keychain, the gog wrapper, the records kept); those wait for his yes at its step A4.

## Decided earlier (recorded in the roadmap, the runbooks and the project notes)
- One OpenClaw gateway on the Mac mini M5 Pro (64 GB), run by a non-admin macOS user "happy"; Tony's admin
  account holds the config repo and deploys. FileVault on, manual unlock. Tailscale Serve only.
- iMessage in Basic mode (System Integrity Protection on) is the only channel.
- One control plane (Tony's) and one data domain per person; one agent per person and permission set; shared
  agents keep no memory. No strict isolation from the operator: Tony can read everyone's data.
- OpenAI only for now: gpt-6-sol through per-person provider ids with store:false. No Anthropic key. Brave for
  web search. A weather tool on the National Weather Service API.
- Evals run on demand and after a critical-path change, never on a schedule. One Grafana screen; alerts by
  ntfy; healthchecks.io for silence.
- Free security stack (Keychain and SOPS, LuLu, Smokescreen). Colima sandbox for every agent. Dreaming off.
  Code Mode off. Session reset daily at 04:00.
- The roadmap's "never" list: payments, purchases, bookings, bank writes; CAPTCHA solving; WhatsApp; LinkedIn
  scraping; and its rule that prompt injection is treated as unsolved (the "lethal trifecta" per agent).
- In the roadmap's section 9 each decision is marked "By: You" (Tony chose it) or "Default" (an agent chose it
  and Tony did not object). Treat "Default" rows as adopted assumptions, not as Tony's stated wishes.

## What the config repo records about the family (checked 11 Oct)
- family.json5 lists exactly two people, both adults: Tony (owner) and Jordan. It records a home town and a
  town-centre coordinate for weather. Nothing else.
- It records NO children (no number, ages, names, school or grade), no pets, no languages, no cars, no
  devices, no routines, no activities, no calendar account, no school platforms.

## Known from a scan, not from Tony
- A LAN scan on 9 Oct saw a Hue bridge, two Sonos speakers, an LG TV (the only HomeKit accessory) and a Canon
  PRO-100 printer, and no RTSP camera. Tony has not said he wants any of them controlled.

## Never stated by Tony (so any card that relies on these is assuming)
- How many children there are, their ages, names, schools, grades, activities, or whether they have devices.
  ("Kids 8 and 10" and the name "Leo" appear only in example texts written by agents.)
- Which school platforms the district uses, and whether the school uses Google Classroom.
- Which calendar the family shares (Google or iCloud), and whether both parents use it.
- Whether the family uses Apple Reminders lists, a shared grocery list, or any notes app.
- Any second language, grandparents, a sitter, pets, cars, passports, insurance, medications or allergies.
- Preferred times of day for any text from Happy, quiet hours, or a daily cap on texts.
- Whether Jordan wants any of this, and which features she would use.
- Whether a spare iPhone, an Apple TV or HomePod, a second Mac, or a Home Assistant install exists.
- Value scores, wave placement and effort estimates: all assigned by agents.
