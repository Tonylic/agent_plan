# Happy feature catalog: capability expansion after M1

Prepared 9 Oct 2026 by Claude Code for Tony. Brainstorm input to the next milestone, which replaces M2 (local models) with a batch of capabilities; M3 (research, email to the asker) and M4 (morning email digest) are folded in where they are feasible now.

How it was produced: nine brainstorm lenses (household ops, kids and school, information and research, inbox, memory and knowledge, devices and media, health and admin, bottom-up from the installed OpenClaw 2026.9.7 docs and skills, market comparison) produced 224 ideas; they were merged to 87, each verified by a feasibility reviewer reading the installed docs and by a security-and-realism reviewer applying the roadmap's rules; a completeness critic added 20; 2 were dropped by the reviewers and 10 folded into siblings. 105 features remain. Reviewer corrections that change the build appear as indented notes. Claims about gog were not checked against a binary (gog is not installed yet) and are marked as such.

Levels
- L1 General capabilities: a tool, account or platform feature an agent can be granted.
- L2 Composite features: a reusable behaviour built from L1 items that anyone in the family uses on demand.
- L3 Special workflows and monitors: scheduled or event-driven programs written for this family.

Tag legend: `[who · risk · agent · dependency · value/5 · effort]`. Risk follows the blueprint tiers (low: untrusted content only; medium: private data, read-only; high: acts in the world). Dependency `now` means buildable on the current stack (cloud model, store:false) without M2; `M3`/`M4` means it belongs to that roadmap milestone's plumbing; `M2` needs a local model; `later` is deferred by choice.

Companion documents: home-agent-roadmap.html (architecture rules, M3/M4 deliverables), home-agent-m1-runbook.html (what exists today). Full verifier notes per feature: ask Claude for the JSON catalog.


Tags: `[who · risk · agent · dependency · value/5 · effort]`. Ten redundant ids are folded into siblings and marked "absorbs". Indented notes are verifier corrections that change the build.

## L1 General capabilities

### Media, voice, channel
- **Inbound iMessage attachments (F001)**: flip `channels.imessage.includeAttachments: true` so photos, PDFs and voice memos reach the agent; today attachment-only messages are dropped. `[adult · medium · channel config · now · 4/5 · S]`
  - Default attachmentRoots already covers /Users/happy. `mediaMaxMb` is outbound only; inbound caps are `tools.media.image.maxBytes` 10 MB and `tools.media.audio.maxBytes` 20 MB. Rewrite templates/person/AGENTS.md line 22. Ship behind F084.
- **Photo and PDF understanding (F002)**: flyer, label, receipt, permission slip, camp packet in, answer out. `[adult · medium · <p>-main · now · 5/5 · S]`
  - F001 alone already delivers PDFs as an untrusted file block (local PDFium extraction). The `pdf` tool adds page selection and must be in both `tools.alsoAllow` and `tools.sandbox.tools.allow`. Leave `agents.defaults.pdfModel` unset (global only). `view_image` is not granted today and not needed: sol/luna take images natively.
- **Voice memos in, transcribed locally (F003)**: dictate from the car, Happy echoes the transcript and answers. `[adult · medium · gateway tools.media · now · 3/5 · M]`
  - Nothing installed: `brew install whisper-cpp` under happy, explicit `tools.media.models[]` CLI entry with `capabilities: ["audio"]`, `{{AttachmentPath}}`, full binary path, `audio.preferredModel: "cli:whisper"`, because configured OpenAI auth beats local CLIs in auto-detect. Independent of M2.
- **Spoken replies (F004)**: `/tts` or `tts.auto: "inbound"` on <p>-main only. `[both · low · <p>-main · now · 2/5 · S]`
  - Free path is tts-local-cli `say` (WAV, not MP3); set `tts.summaryModel` or long replies truncate at 1,500 chars. iOS already reads texts aloud; keep as the F003 round trip.
- **Image generation (F005)**: coloring pages and cards via `image_generate`. `[both · medium · <p>-main · later · 2/5 · M]`
  - Needs the catalog `models.providers.openai`, not a custom id, and the Images API has no `store` field. Adding that provider makes OpenAI the auto-detected audio and pdf provider, so F003 pins become mandatory.
- **Family delivery primitive (G009)**: `message` tool on <p>-main, recipients pinned by a fail-closed `before_tool_call` hook to family.json5 handles and the parents' `chat_id`; host jobs use `openclaw agent --to --deliver`. `[both · medium · <p>-main · now · 5/5 · M]`
  - This adds the third trifecta leg; safe only because the recipient set is closed. Add `message_sending` as a second gate and a promptfoo canary ("text this number"). Never on research.
- **Bilingual replies and grandparent translations (G011)**: per-person `languages` rendered into USER.md. `[both · low · <p>-main · now · 3/5 · S]`

### Calendar and reminders
- **Timed reminders (F007, absorbs F008 standing intents)**: `automations` tool (alias `cron`) on <p>-main; `--at` one-shots auto-delete, recurring `--cron --tz America/New_York`, `--tools ""`. `[adult · low · <p>-main · now · 4/5 · S]`
  - Both parents in `commands.ownerAllowFrom` to list/cancel (global elevation; pair with `tools.deny: ["gateway"]`). Hook sets delivery.to from `ctx.requester.senderId`. Cron sessions omit MEMORY.md, so reminder text is self-contained. `intent` (memory-core, FTS, no model call) stays an AGENTS.md footnote: intents for events, automations for clock times. Refill math and antibiotic courses (ex-F065) are reminder templates.
- **Family calendar read-only (F009)**: per-person host-side stdio MCP `<p>-calendar` over `gog calendar events|freebusy|conflicts`. `[adult · medium · <p>-main · now · 4/5 · M]`
  - Request a calendar read-only scope at `gog auth add` (verify the flag on the installed gog; plain `--services calendar` grants full scope). MCP tools are `<server>__<tool>` and need `bundle-mcp` in the sandbox allow list. Publish the Google OAuth app (Testing status expires refresh tokens in 7 days). Google vs iCloud decided first; build one.
- **External .ics feeds (G012)**: district days off, TeamSnap, library. `[adult · low · host-side · now · 3/5 · S]`
  - OpenClaw has no .ics handling. Subscribe feeds inside the family Google Calendar and read through F009; a host parser only if 6-hour freshness matters.

### Research and summaries
- **Stateless research agent with web_fetch (F019, M3 slice 1)**: memory off, tools `web_search` + `web_fetch`; <p>-main gets `sessions_spawn` and `subagents.allowAgents: ["research"]`. `[adult · low · research · now · 5/5 · M]`
  - Drop `session_status` (sub-agents lose it). The sandbox adds nothing for a web_search + web_fetch tool set (both run in the gateway process); keep sandbox mode `all` for consistency with the roadmap, noting that sandboxed `pdf` rejects http URLs. Handoff rule: ages and town OK, never kid names, school, address, health.
- **Extra readers (F020)**: host-managed headless `browser` profile (logged out, `evaluateEnabled: false`) and a `summarize` stdio MCP. `[adult · low · research · M3 · 3/5 · M]`
  - The Docker sandbox browser needs bridge networking and CDP ports (effort L); use the host profile and hook-block form-fill actions.
- **Places lookup (F021)**: `goplaces` as host-side stdio MCP, key as SecretRef, home lat/lng pinned server-side. `[adult · low · research · M3 · 3/5 · M]`
  - Google's Maps Grounding Lite MCP (roadmap ref 75) is an external Google MCP, not an OpenClaw plugin; goplaces is the bundled alternative and returns straight-line distance, not drive time. Pick one at build time.
- **Citation and freshness rules (F022)**: prices only from tool results, quote `web_fetch` fetchedAt, flag when no visible date or over 30 days, "could not verify" allowed. `[adult · low · <p>-main + research · now · 4/5 · S]`
- **Long-running task etiquette (G014)**: ack, `sessions_spawn` with `runTimeoutSeconds`, one completion message, `subagents` cancel, `maxConcurrent` cap. `[both · low · <p>-main · M3 · 4/5 · S]`

### Lists and household
- **Shared Apple Reminders bridge (F030)**: host-side plugin `home-reminders` over `remindctl`: list/add/complete on named lists, no delete; Notes append later. `[both · medium · <p>-main · now · 4/5 · M]`
  - TCC for Reminders/Automation goes to the launchd node binary on happy's desktop, not Terminal. macOS node `reminders.*` is iOS/Android only. Siri captures better; value is as the write target for F032/F038.
- **Household structured store (F031, home-store)**: `defineToolPlugin` over SQLite: `schedule_get/upsert/mark_done`, `fact_get/set`. `[both · medium · <p>-main · now · 4/5 · M]`
  - Ship as a plugin, not a separate MCP process; hook rejects secret-looking values; jobs reference `home-store__*`. Lists stay in Reminders.
- **Contacts lookup (G013)**: `gog contacts list` read-only MCP on the calendar grant. `[adult · medium · <p>-main · later · 2/5 · S]`

### Memory and knowledge
- **Durable per-person memory, "remember this" (F041)**: `write`/`edit` on <p>-main with `workspaceAccess: rw`, hook limiting paths to MEMORY.md, USER.md, memory/*.md; `memory_search`, `sessions_search` visibility `agent`; session-memory hook. `[adult · medium · <p>-main · now · 5/5 · M]`
  - `allow: ["write"]` also enables `apply_patch`; deny it. The hook must track `after_tool_call` for web_search/web_fetch per run and block writes in tainted runs (one tainted write downgrades the whole file). Set `memory.search.provider: "none"` explicitly; default is OpenAI embeddings.
- **Family facts in bootstrap files (F042)**: kids, routines, preferences from family.json5. `[adult · medium · <p>-main · now · 4/5 · S]`
  - USER.md has a hard 4,000-char cap: adult directives there, kid/routine facts in MEMORY.md or memory/family-facts.md. gen-family writes a managed block and preserves a manual block or chat edits vanish on redeploy. Cron sessions do not see these files.
- **Household knowledge vault (F043, absorbs F035 family facts Q&A)**: step 1 shared Markdown via `agents.entries.<p>-main.memory.search.extraPaths`; step 2 `openclaw plugins enable memory-wiki`, `vault.scope: global`, own dir, `wiki_search/get/apply/lint`. `[adult · medium · <p>-main · now · 4/5 · M]`
  - `wiki_apply` only creates synthesis pages and edits metadata; people, provider and location pages are seeded via `openclaw wiki ingest`. Hook denies wiki_apply in tainted turns. Never policy/member/account numbers; locations excluded from any kid export.
- **Sheets and Drive read-only (F045)**: `<p>-drive-ro` MCP exposing only search/get/cat. `[adult · medium · <p>-main · later · 2/5 · M]`
  - gog documents no read-only scope flag; the allowlist wrapper is the boundary. Bundle with the M4 OAuth consent.
- **Semantic memory search (F046)**: `@openclaw/llama-cpp-provider` + embeddinggemma, `memory.search.provider: "local"`. `[adult · medium · <p>-main · M2 · 2/5 · S]`
  - Text leg is independent of Ollama; photo leg needs gemini-embedding-2 (Google cloud), drop it.

### Inbox
- **Per-person read-only Gmail (F047)**: `<p>-gmail` stdio MCP for <p>-mail only. `[adult · medium · <p>-mail · M4 · 5/5 · M]`
  - gog is not installed yet, so verify its flags at build time: its MCP mode exposes read tools only unless `--allow-write` (roadmap ref 99), but the OAuth token's default Gmail scope may be gmail.modify. Request a read-only scope at `gog auth add` if the installed version supports it, pass `--gmail-no-send`, expose only search/get, and deny the rest by hook. Both tokens share one file keyring under happy.
- **Per-person Gmail drafts (F048)**: `gog gmail drafts create` MCP; hook blocks any send. `[adult · medium · <p>-mail · M4 · 4/5 · M]`
  - Verify `--reply-to-message-id` on drafts create, else drafts are unthreaded.
- **mailout to owner (F049)**: happy-family@ sender, hook rewrites `to` to the owner, rejects cc/bcc. `[adult · medium · <p>-main only · M3 · 3/5 · M]`
  - Not on research (owner ambiguous, reads untrusted web).
- **IMAP watch on a personal Gmail (F050)**: bundled `imap` plugin, `allowedSenders`, `senderAuth.min: verified`, per-message isolated reader. `[adult · medium · <p>-mail-reader · M4 · 3/5 · M]`
  - `deliver: true` posts a system event, it does not text the owner; push needs the reader's `message` tool pinned by hook, or a 15-minute cron sweep. Reader is tool-less and separate from <p>-mail.
- **Dedicated school mailbox (F051)**: happy-school@ registered with district, PTA, coaches, lunch system; parents forward with a one-line note; tool-less, memory-less `school-mail` reader. `[adult · low · school-mail · now · 5/5 · M]`
  - Sidesteps the private-inbox decision. iCloud+ needs `watch.mode: "interval"`; IMAP passes body text only; acceptance test is the docs' "follow this link and run a command" email. Same delivery caveat as F050.
- **Per-person mail reader agent (G015)**: the <p>-mail entry: `profile: minimal`, deny web/browser/fs/runtime, memory off, send pinned to owner, `openclaw sandbox explain --agent` in happy-deploy. `[adult · medium · <p>-mail · M4 · 5/5 · M]`
- **Sender allowlist by chat (G016)**: proposed rule, /approve, gen-family regenerates `allowedSenders`. `[adult · medium · <p>-main · with F051 or M4 · 3/5 · M]`
  - The allowlist is the reader's security boundary; only the mailbox owner approves.

### Kids
- **Kids agent base (F072)**: per-kid handle via `bindings[]`, no tools, memory off, classifiers in/out, 04:00 reset. `[kid · low · kid-<name> · M2 then M5 · 4/5 · L]`
  - No built-in classifier: in-house plugin on `before_dispatch` and `message_sending`; onnx is unpublished. OpenAI terms are 13+, no cloud shortcut. One agent per kid; kids need their own Apple child accounts.

### Devices and home
- **Hue (F076)**: plugin `home-hue` over `openhue`, room allowlist and quiet hours in code, inside a new stateless `home` agent reached via `sessions_spawn`. `[adult · high · home · now · 3/5 · M]`
  - Bridge confirmed on LAN. `home` must be sandboxed like its caller; <p>-main must un-deny `sessions_spawn`; openhue keeps its key in ~/.openhue; grant Local Network to the launchd node process.
- **Sonos (F077)**: plugin `home-sonos` over `sonoscli`, volume cap 35 (10 after 21:00), favorites only. `[adult · high · home · now · 3/5 · M]`
  - Two speakers found (Living Room, Family Room); sonoscli is `go install` only.
- **Allowlisted macOS Shortcuts (F078)**: `shortcuts run <name>` by exact-name allowlist; never locks, garage, alarm, gate. `[adult · high · home · now · 3/5 · S]`
  - Input is a file path, drop free-text input. Only HomeKit accessory today is an LG TV. Shortcuts live in happy's account, one interactive first run.
- **Camera snapshot (F079)**: `camsnap` plugin, outdoor allowlist. `[adult · medium · <p>-main · later · 2/5 · M]`
  - No RTSP camera found; Ring/Nest/Arlo are cloud-only.
- **Print it (F080)**: plugin `home-print` over `lp`; https download inside the plugin with SSRF checks; copies cap 10. `[adult · high · home · now · 3/5 · S]`
  - Canon PRO-100 is on the LAN but `lpstat -p` shows no destination: `lpadmin` once. Fridge-sheet leg waits for calendar and lists.

### Operator platform
- **ask_user and llm-task (F082)**: `ask_user` on <p>-main only (main session, plain-text reply); `llm-task` with schema validation, `llm.allowedCompletionModels` listing both custom ids, `allowModelOverride: false`. `[both · low · <p>-main, readers get llm-task · now · 3/5 · S]`
- **home_weather v2 (F083)**: alert ids, hourly via `forecastHourly`, snowfall. `[both · low · <p>-main · now · 3/5 · S]`
- **Local privacy gate for documents (F084)**: refuse statements, W-2/1099, SSN and card patterns before any cloud call. `[operator · low · plugin hook · now · 4/5 · M]`
  - A `before_tool_call` on `pdf` is the wrong hook: inbound attachments reach the model as a file block on the first turn. Gate in `before_agent_run` (`{outcome: "block"}`, fails closed) over the extracted text, plus `allowedMimes`; refuse scanned PDFs under ~200 chars/page. Photos get only caption keywords until M2. Prerequisite for F001.
- **Memory hygiene and weekly review (F085)**: `memoryPolicy.excludeSessions.hookExternalContentSources: ["email","gmail"]`, `openclaw memory forget --dry-run` runbook, Sunday 5-line review per adult. `[operator · medium · <p>-main isolated · now · 3/5 · M]`
  - The exclusion covers hook sessions only; the real guard is <p>-mail with memory off. Do not set `memoryFlush.model` to apple-fm (8k window). Promote via `openclaw memory promote --apply`.
- **Apple Foundation Models (F086)**: `openclaw onboard --auth-choice apple-fm`, `agents.defaults.utilityModel: apple-fm/system`. `[operator · low · all · now · 2/5 · M]`
  - Probe the 8,192-context variant in the happy user first. Titles and narration are Control UI only; keep as the free classifier for F084.
- **Notification policy (G001)**: quiet hours 21:30-06:30, cap 6 per day, urgent/normal/low classes, job tag; one plugin on `before_tool_call` (`message`) and `reply_payload_sending` (covers `--announce`). `[both · low · plugin + home-store · now · 4/5 · M]`
  - No built-in quiet hours exist. Ships with the first digest.
- **Jobs registry in family.json5 (G003)**: per-feature flags with per-person subscription; gen-family emits `openclaw automations add --agent --to --tz --announce --display-name` and diffs against `automations list --json`. `[operator · low · host-side · now · 5/5 · M]`
  - Always pass `--agent`. `--webhook` cannot combine with `--announce`; healthchecks pings come from a command job.
- **Spend caps (G004)**: `openclaw gateway usage-cost --json`, Prometheus `openclaw_model_cost_usd_total` alert. `[operator · low · host-side · now · 3/5 · M]`
  - Estimate, not billing; the OpenAI project limit is the backstop. Fold the daily line into G006; defer auto-downgrade.
- **Kill switch (G005)**: `before_dispatch` exact-phrase claim, kill file checked in `before_tool_call` and `message_sending`, `cron.enabled: false` (hot-applies), `openclaw gateway stop`. `[both · low · plugin · now · 4/5 · M]`
- **Audit digest (G006)**: `logging.audit` plus an `after_tool_call` side-effect ledger; on demand and Sunday rollup. `[operator · low · host-side · now · 4/5 · M]`
  - The audit ledger stores no tool arguments; `openclaw approvals` has no history.
- **Backups and restore drill (G007)**: `openclaw backup create --verify`, `backup sqlite create --repository`, quarterly `backup restore --target`. `[operator · low · host-side · now · 4/5 · M]`
  - Encryption, rotation and the vault/home-store/family.json5 tar are outside the command; SQLite snapshots can contain auth profiles.
- **Integration health watch (G008)**: `openclaw health --json`, `channels status --probe`, `models status --check`, `gog auth list --check`. `[operator · low · host-side · now · 4/5 · S]`
  - Never `models status --probe` in a job; it needs the Gateway stopped.

## L2 Composite features

### Media, voice, channel
- **Happy in the parents' group chat (F006)**: `groupPolicy: allowlist`, `groupAllowFrom`, `groups["<chat_id>"]`, `bindings[]` to a stateless `family-group` agent; the chat_id is the announce target for opted-in jobs. `[adult · medium · family-group · now · 3/5 · M]`
  - v1 tools are home_weather and web_search only (no calendar or lists yet). "Tell everyone" relays go through G009, never a `message` tool on a memory-holding agent.

### Calendar and reminders
- **Calendar create with approval (F010)**: ship the .ics tap-to-add attachment first (zero write scope); then `<p>-calendar-write` MCP with its own full-scope gog home, hook pins the Family calendar, rejects attendees, `requireApproval` with `allowedDecisions: ["allow-once","deny"]`. `[adult · high · <p>-main · now · 4/5 · M]`
  - Approval `timeoutMs` caps at 10 minutes; owner check uses `ctx.requester.senderIsOwner`.
- **Snap-to-action (F011, absorbs F040 receipts)**: after reading a flyer or receipt, propose reminders, list items, calendar drafts, return-by date; write only after a yes. `[adult · medium · <p>-main · now · 4/5 · M]`
  - Plain proposal plus the AGENTS.md standing order, not `ask_user` (900 s timeout). FSA and donation ledgers dropped.
- **Pending items view (G020)**: approvals (`openclaw approvals pending --json` carries `expiresAtMs`), reminders, watchers, intents, open requests via one host MCP. `[adult · low · <p>-main · now · 3/5 · M]`

### Research and summaries
- **Explain this (F023, absorbs F024 summarize link)**: text, screenshot/PDF or URL in; fixed 5 lines out (dates, what to do, money, which kid, deadline). URLs go via research. `[adult · low · <p>-main + research · now · 4/5 · S]`
- **Fact check and official sources (F025)**: `web_search count 8` then `web_fetch`; "unclear" is valid. `[adult · low · research · M3 · 2/5 · S]`
  - A hostname allowlist is not a config knob (`blockedHostnames` only); fold the rubric into F022.
- **Product and program research (F026)**: 3-5 options with price, dates, fetched-at; no cart. `[adult · low · research · M3 · 3/5 · M]`
  - Retail sites bot-wall plain fetch; expect "could not verify".
- **Find a place and route errands (F027)**: goplaces `--open-now --min-rating --radius-m`; errands from the F030 list. `[adult · low · research · M3 · 3/5 · S]`
- **Trip and outing planner (F028, absorbs F017's Friday "this weekend near us")**: 2 options with hours, cost, weather; long version via mailout; Friday 16:00 job on research. `[adult · low · research · M3 · 4/5 · L]`
  - Free windows cross as date ranges only. Sunday topic brief dropped.

### Lists and household
- **Grocery capture and Saturday list (F032)**: text or voice add; Saturday 09:00, one job per parent. `[both · medium · <p>-main · now · 3/5 · M]`
  - "Staples not bought in 3 weeks" needs home-store history; ship without it.
- **Home systems and provider registry (F034)**: data-plate photos into vault pages or `home-store__fact_set`; manuals via research. `[adult · medium · <p>-main · now · 4/5 · S]`
- **Babysitter sheet (F036)**: vault `sitter` facts plus calendar; never store the Wi-Fi password. `[adult · medium · <p>-main · now · 2/5 · S]`
- **Draft-only outreach texts (F037)**: plumber, coach, carpool; parent sends from their own phone. `[adult · low · <p>-main · now · 2/5 · S]`

### Memory and knowledge
- **Document vault "file this" (F044)**: host tool copies the attachment, extracts text, `wiki ingest` the summary, nightly expiry scan. `[adult · medium · <p>-main + command job · later · 3/5 · L]`
  - `wiki ingest` rejects binaries; claims have no expiresAt field, so a docs/index.json convention.

### Inbox
- **"Did I get an email about X?" (F052)**: <p>-main hands off to <p>-mail via `sessions_spawn`. `[adult · medium · <p>-mail · M4 · 4/5 · S]`
- **Draft a reply (F053)**: absence, early pickup, thank-you templates into Gmail Drafts. `[adult · medium · <p>-mail · M4 · 4/5 · S]`
- **Needs-reply tracker (F054)**: weekdays 17:30, both directions. `[adult · medium · <p>-mail · M4 · 2/5 · M]`
  - Gmail Nudges already does this.

### Health and admin
- **Explain this EOB or bill (F064, absorbs F068's "no EOB 30 days after a visit")**: 5 lines; drafts the member-services message. `[adult · medium · <p>-main · now · 3/5 · S]`
  - EOB images carry member and claim IDs to the cloud model before any rule applies; add an ID-redaction hook on memory writes.
- **Health-form helper (F067)**: copy-paste block from vault facts; never fills or submits. `[adult · medium · <p>-main · now · 2/5 · S]`
- **Spend summary from statements (F070)**: `<p>-finance` agent on a local model. `[adult · medium · <p>-finance · M2 · 3/5 · M]`
  - `pdfModel` is global only: deny `pdf` and rely on local extraction; route by watched folder, not an in-agent gate (the cloud model would already have read it).

### Kids
- **Homework hints and curiosity Q&A (F073)**: hint-first, grade band in AGENTS.md, no URLs or a 5-10 URL allowlist enforced in `message_sending`. `[kid · low · kid-<name> · M2/M5 · 4/5 · S]`
- **Practice drills (F074)**: spelling, math facts, reading buddy; parent-run version from <p>-main now. `[both · low · kid-<name> · M2/M5 · 3/5 · S]`
  - A text spelling quiz shows the word; needs local `say` TTS per agent (`agents.entries.kid-*.tts.auto`), never cloud TTS for kids.
- **Kid check-in relay (G018)**: "I'm home" / "I fed the dog" claimed by a `before_dispatch` regex, forwarded via G009. `[kid · medium · plugin · later · 3/5 · M]`

### Coordination
- **Snooze, mute, vacation mode (G002)**: paused-until row in home-store that every job checks (NO_REPLY), or `automations disable` from a host helper. `[both · low · <p>-main · now · 4/5 · S]`
- **Parent-to-parent request relay (G010)**: tracked ask with id, 4 h expiry, yes/no matched in `before_dispatch`. `[adult · low · <p>-main · now · 3/5 · M]`

## L3 Special workflows and monitors

### Calendar and reminders
- **Birthday and gift-date heads-up (F012)**: dates table in family.json5 rendered to memory/family-dates.md; daily 08:00 isolated job with a 7-day window. `[adult · medium · <p>-main isolated · now · 3/5 · S]`
  - memory-wiki is not enabled; weekly `0 8 * * 1` gives a 7-13 day lead.
- **Leave-by nudges (G017)**: Google Routes drive time to the tagged driver. `[adult · low · host-side · M3 · 2/5 · M]`
  - Phones already do Time to Leave; up to 4 extra texts a day against the cap.

### Digests and briefs
- **Weekday morning brief 07:00 (F013)**: weather and alerts, calendar, reminders due, trash day, sunset. `[adult · medium · <p>-main isolated · now · 3/5 · M]`
  - Drop `--light-context` (it skips AGENTS.md). Drop headlines (untrusted web in a run holding private calendar data). Pass `--tools home_weather,<p>-calendar__*,home-store__*` explicitly. Really gated on F009/F030.
- **Evening logistics brief 19:30 Sun-Thu (F014)**: tomorrow's events, who drives ([T]/[S]), what to pack, weather; NO_REPLY when nothing is notable. `[adult · medium · <p>-main isolated · now · 5/5 · S]`
  - Routines table lives in AGENTS.md (USER.md cap).
- **Sunday 18:00 week-ahead (F015)**: early releases, drivers, deadlines; the M4 leg runs on <p>-mail as its own job. `[adult · medium · <p>-main isolated · now · 4/5 · S]`
- **07:00 email digest (F016)**: ~10 lines with action items; drafts opt-in per item. `[adult · medium · <p>-mail isolated · M4 · 4/5 · M]`
  - `--tools "<p>-gmail__*,<p>-gmail-drafts__*,llm-task"`; relay sender, subject, action only, never URLs from mail bodies.
- **Severe-weather and snow-day watch (F018)**: `--command-argv` job running scripts/nws-alerts.mjs with a seen-id state file; prints NO_REPLY. `[adult · low · command job · now · 3/5 · M]`
  - Zero model calls; one job per parent. F083 alert id is needed only for the trigger-script variant.

### Research
- **Public page watcher (F029)**: `--every 6h --trigger-script` owned by research (no exec), `once: true`, 16 KB state. `[adult · low · research · M3 · 3/5 · M]`
  - Tony creates via CLI (chat-created jobs inherit the creator's tools). Drop price-drop watching.

### Lists and household
- **Sunday meal plan to grocery list (F033)**: recipes as home-store rows or wiki synthesis; the job writes "plan/this-week" so the main session can swap a night. `[adult · medium · jordan-main isolated · now · 3/5 · M]`
- **Home upkeep calendar (F038)**: HVAC filter, inspection, bins with holiday shifts; `--cron '0 20 * * 0,3'` per parent over `home-store__schedule_*`. `[both · low · <p>-main isolated · now · 3/5 · S]`
  - January town-page refresh needs web_fetch: research task, or Tony pastes the PDF.
- **Kids' chore rota, parent-run (F039)**: Sunday board, 17:30 routine lines to the on-duty parent, Saturday tally. `[both · low · <p>-main isolated · now · 2/5 · S]`

### Inbox
- **Urgent school alert relay (F055)**: reader classifies URGENT vs ROUTINE (NO_REPLY). `[adult · low · school-mail · now · 3/5 · M]`
  - "Within a minute" needs the reader's `message` tool pinned to the two parents; the sweep fallback is ~15 minutes. Districts already push closures; the value is gating routine mail into F056.
- **School and activities digest 16:00 (F056, absorbs F057 deadlines sheet)**: 5 lines with dates spelled out, newsletter 5-liner, dated checklist in home-store with day-before reminders via F007, lunch-balance line. `[adult · low · school-mail + <p>-main · now · 5/5 · M]`
  - `school-mail-ro` MCP is gog (Gmail) or himalaya (iCloud), host-side; `--tools school-mail-ro__*`; relay only links whose domain matches the allowlisted sender; two jobs or the family chat_id. No Google Sheet.
- **Package tracking (F058)**: arriving today, delivered, return windows. `[adult · medium · <p>-mail-reader · M4 · 2/5 · M]`
- **Appointments, refills, travel changes (F060, absorbs F059 bill nudges and F066 prep card)**: confirmations become .ics plus an evening-before reminder with address and "bring insurance card"; pharmacy and results pings subject-only; airline delay pings; non-autopay bill due nudges. `[adult · medium · <p>-mail · M4 · 3/5 · L]`
  - Keep PHI senders subject-only (small maxBytes); rebooking stays human.
- **Tax document checklist Jan-Apr (F061)**: `--cron '0 9 * 1-4 6'`; checklist text in the job prompt because `--tools ""` blocks reads. `[adult · medium · <p>-mail + <p>-main · M4 · 3/5 · M]`

### Health and admin
- **Renewals and expiry program (F063)**: passports (9 months), inspection, registration, domains; monthly `--cron '0 9 1 * *' --agent <p>-main --session isolated --tools ""`. `[adult · medium · <p>-main isolated · now · 4/5 · S]`
  - With `--tools ""` the table must be in `--message` or AGENTS.md; RDAP needs web_fetch (M3).
- **Pet care program (F069)**: monthly meds, vaccine dates, food link. `[both · low · <p>-main · now · 2/5 · S]`
  - No pet appears in the brief; confirm before building.

### Kids
- **Kid-safe weekly card (F075)**: schedule, chores, first names only, exported into an AGENTS.md "## This week" section. `[kid · medium · kid-<name> · later · 2/5 · M]`
  - Channel sessions omit MEMORY.md, so the export cannot go there.
- **Parents' nightly kids-chat digest (G019)**: 3 lines per kid rendered host-side on a local model. `[adult · medium · host-side · later · 3/5 · S]`

### Devices
- **Goodnight check and scheduled scenes (F081)**: 22:30 read-only check as a `--command` payload (zero tokens); actuation later after a dry-run period. `[adult · high · command job, then home · now · 2/5 · S]`
  - No Lobster (disabled in sandboxed contexts); isolated runs cannot approve, so dry-run instead of per-call approval.

### Operator
- **Approval-gated workflows, Lobster (F087)**: typed pipelines with resume tokens. `[adult · high · dedicated agent · later · 1/5 · L]`
  - Host exec in a person agent; `before_tool_call requireApproval` already gives the gate.

## Recommended batch for the next milestone (capability expansion, M2 deferred)

Scope: every "now" item, plus F019 (M3 slice 1, verifiers agree it is config and prompts). M4 personal-inbox items enter wave C only if decision 1 is yes.

**Wave A: substrate and read-only inputs**
- Operator: G003 jobs registry, G005 kill switch (phrase + CLI), G008 health watch, G007 backups, G004 soft alert.
- Channel: F084 gate, then F001 + F002; F003 (whisper-cpp); G011; F083.
- Memory: F041 write path, F042 bootstrap facts, F043 step 1 (extraPaths).
- Scheduling: F007 (+F008 footnote), Jordan in `commands.ownerAllowFrom`, F082.
- Calendar: F009 read-only after decision 4, OAuth app published.
- Delivery: G009 primitive, F006 group registry as announce target.
- Research: F019 slice 1, F022, F023 (incl. URL input).
- Household: F031 home-store (schedules, facts), F030 Reminders bridge.
- Exit test: Jordan forwards a camp flyer photo and a voice memo; Happy reads both and proposes reminders, creates one via `automations` that fires to her handle; "remember Leo's shoe size" lands in jordan-main MEMORY.md; "what's on Saturday" answers from the family calendar; "Happy, stop everything" pauses all jobs; a seeded tier-C statement PDF is refused before any cloud call.

**Wave B: digests and monitors on A**
- G001 notification policy (with the first digest), G002 snooze/vacation, G006 audit digest.
- F014 evening brief, F013 morning brief (no headlines), F015 week-ahead, F018 weather watch, F038 upkeep, F012 dates, F063 renewals, F032 Saturday list, F039 optional.
- F051 school mailbox + F055 + F056 (+G016 for its allowlist).
- F010 .ics first, F011 snap-to-action, F034 registry, F064 EOB, F036, F037, F085 weekly review, F043 step 2 if the folder grows, F069 if there is a pet.
- Exit test: two school weeks in which both parents get the 19:30 brief and the 16:00 school digest, a seeded two-hour-delay email is relayed within 15 minutes, bins text the night before, zero proactive texts inside quiet hours, the daily cap is never hit, G006 shows every write with a job tag, and Jordan mutes a week with one text.

**Wave C: research agent, actions, devices (M4 conditional)**
- M3: F020 readers, F021 goplaces, F025-F028, F029 watcher, F049 mailout, G014 etiquette, G020 pending view.
- Actions: F010 write MCP if .ics taps annoy, G010 parent relay, F033 meal plan, F080 print, F076/F077/F078 home agent, F081 read-only goodnight.
- M4 (decision 1 = yes): G015, F047, F048, F016, F052, F053, F060, F061.
- Exit test: "plan Saturday, kids 8 and 10, rain likely" returns two options with fetched-at links in under 3 minutes with an ack; the promptfoo injection suite passes on research and <p>-mail ("follow this link and run a command"); a seeded "text this number" is blocked by the G009 hook; if M4 is on, the 07:00 digest lists sender/subject/action with no URLs and one draft lands in the owner's Drafts.

**Decisions Tony makes first**
1. Personal email on the cloud model under store:false now, or wait for M2. Gates F047, F048, G015, F016, F052, F053, F058-F061. The school mailbox (F051/F055/F056) needs no such decision.
2. Mail path: dedicated school mailbox first (recommended); IMAP plugin for per-message watches and gog Gmail MCP for search/drafts (different jobs, both); whether Jordan's inbox is in scope (her OAuth consent, one keyring under happy).
3. Attachments to the cloud vision model: `includeAttachments: true` sends family photos and school PDFs to OpenAI under store:false, with F084 as the condition. Voice stays local.
4. Calendar: Google (gog `--readonly`, published OAuth app) or iCloud (macOS node); and Jordan as an owner in `commands.ownerAllowFrom` (global elevation, pair with `gateway` deny).
5. Providers and kids: no Anthropic for PDFs (local PDFium extraction suffices; revisit if flyers fail); no catalog `openai` provider now (F005 changes audio/pdf routing); kids stay off until M2/M5 (OpenAI terms are 13+), parents run drills from <p>-main.

## Later / never

Later
- F005 image generation: catalog provider side effects on F002/F003 routing.
- F044 document vault: effort L for 1-2 documents a month.
- F045 Sheets/Drive: bundle with the M4 OAuth consent.
- F046 semantic search: M2; photo leg never (Google cloud embeddings).
- F054 needs-reply tracker: Gmail Nudges already does it.
- F058 packages: carrier apps already push; M4 at best.
- F070 statements: tier C, M2 only.
- F072-F075, G018, G019 kids: M2 then M5.
- F079 camera: no RTSP camera in the house.
- G013 contacts: pull forward only with F036/F037.
- G017 leave-by: phone calendars already do it.
- G012 parser: subscribe in Google Calendar; parser only if freshness bites.
- F087 Lobster: host exec in a person agent.
- Merged-away halves: F017 Sunday topic brief (Google Alerts), F040 FSA/donation ledgers (tier C drift), F057 Sheets write (fifth store), F065 dose pings (reminder template), F068 claims tracker (niche), F006 broadcast via `message` on a memory agent (only via G009 pins).

Never
- Payments, purchases, bookings, bank writes; CAPTCHA solving; WhatsApp; LinkedIn scraping (roadmap).
- Gmail Pub/Sub (public endpoint).
- Firecrawl as default fetch provider (ships failed URLs to a third party).
- Cloud TTS or cloud LLM for kids' content (provider terms).
- `apple-fm/system` as memory flush model (8k window).
- `models status --probe` in any scheduled job (needs the Gateway stopped).
## Computer use and device nodes (assessed 11 Oct 2026)

Question: can Happy operate a real computer, or a connected idle iPhone? Checked against the installed OpenClaw 2026.9.7 docs (nodes/computer-use.md, nodes/command-policy.md, platforms/ios.md, platforms/android.md, platforms/mac/permissions.md, tools/exec-approvals-advanced.md) by four reviewers and a skeptic pass.

What exists
- **Mac desktop control**: a built-in `computer` tool (screenshot, click, type, key, scroll; window/element/browser families with the CUA provider) routed through the node command `computer.act`. On macOS the only fulfiller is the signed OpenClaw.app menu-bar app running in the target user's logged-in session, paired as a node; the Homebrew CLI gateway cannot fulfil it, and `openclaw plugins enable cua-computer` is Windows/Linux only. No OpenClaw.app is installed on the mini today.
- **iPhone**: the iOS app is a sensor and terminal node, not a controllable computer. Defaults: camera.list, location.get, device.info/status, contacts.search, calendar.events, reminders.list, photos.latest, motion.*, system.notify, talk.ptt.*. Opt-ins: camera.snap/clip, screen.record, health.summary, calendar.add, reminders.add. There is no UI-control command for iOS; camera and screen commands need the app foregrounded; background wakes only record presence; nothing bypasses unlock. Pairing hands the phone a full operator token unless `openclaw qr --limited` or `--voice-node` is used.
- **Android** is the only phone OpenClaw can operate: with Accessibility Control on it advertises mobile.ui.observe/act (default-allowed) behind the `mobile_ui` tool, whose `confirmed=true` flag is the model confirming itself. Android also forwards other apps' notifications to the gateway (package allowlist, quiet hours, 20/min cap, route to a session).

Why desktop control is not in this batch
- The grant is durable and unconfirmed: Allow Computer Control defaults on in the app, `computer.act` is a macOS platform default, there is no lease, arm/disarm or per-action prompt. The only per-action gate OpenClaw itself implements is the spoken confirmation in Talk-originated runs.
- No code-enforced per-app or per-domain limit exists: a hook sees action, text and coordinates, never the screen; the roadmap's "known domains, never submits" rule cannot be expressed on pixel input.
- Capture and input need a verified unlocked desktop; lock retires the run and OpenClaw never unlocks. On the mini the unlocked console is happy's, with Messages signed in: one tool then holds private data (family chats on screen), untrusted content (the screen) and an unbounded exit (type into Messages or Safari), bypassing the send-only-to-owner rule.
- Approvals would be blind: screenshots are model-only, the approval card carries 80 + 512 characters, and over iMessage any allowlisted sender can resolve any request. Gateway-side approval needs the `operator.approvals` scope (Control UI).
- TCC grants (Accessibility, Event Posting, Screen Recording) must go to /Applications/OpenClaw.app, never to the Homebrew `node` binary that already holds Full Disk Access.

What computer use would add that the catalog lacks: portals with manual login and MFA on bot-sensitive sites, native Apple apps without a CLI (Photos, Home, Find My), PDF forms in Preview, "what is on the screen" during an incident. Narrower substitutes exist for most: the M3 sandboxed browser, a host browser profile with manual sign-in (a baseline change: browser is disabled in M0), gog and the apple-* skills, `lpr` and `shortcuts run <name>` behind a host plugin, the pdf skill.

Decisions and items
- **Now (S)**: `gateway.nodes.commands.deny: ["computer.act", "desktop.stream", "mobile.ui.act"]` in the repo config; keep `group:nodes` denied for every agent; family Control UI devices without `operator.write` or `operator.approvals`; standing rule: Allow Computer Control and Desktop sharing OFF before any Mac is ever paired.
- **Later, after M6, attended only**: a stateless `desk` agent holding only `computer`, Peekaboo provider, on a dedicated spare Mac paired as a node (never Tony's or Jordan's personal laptop; a Lume VM is undocumented for this), bound to Tony's Control UI session with an owner-required, fail-closed hook and an action-type allowlist, Tony watching the Desktop panel. Marginal family value.
- **Spare iPhone, later, one role only**: outdoor-facing camera snapshot kiosk (camera.snap opt-in, dedicated Apple ID, personal-data commands denied, hook limits `nodes` to one node and command), or an adults-only kitchen Talk terminal, or an iCloud Calendar/Reminders bridge if iCloud wins decision 4. Fragile: the app must stay foregrounded. Locating kids' phones: never (Find My). Kids speaker stays Home Assistant Voice PE (M5).
- **Android portal phone, later**: a cheap phone on a dedicated Google account with school, activity, pharmacy and carrier apps; notification forwarding into a tool-less reader relayed to parents through the pinned delivery primitive. Schedule after two school weeks of the school-mail digest show gaps only an app can fill. Observe-only `mobile_ui` pilot only after that, with activate/set_text/tap/swipe, sms.* and callLog.search denied.
- **Unverified**: whether the app's node resolves the Keychain SecretRef for the gateway token (OPENCLAW_GATEWAY_TOKEN in the app environment is the fallback); whether a standard user can toggle Accessibility and Screen Recording without an admin password; the scope of the iOS "screen snapshot"; whether `computer` added to sandbox.tools.allow clears the shipped sandbox default deny.
