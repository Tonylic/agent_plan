# Happy: a self-hosted family assistant (plans and runbooks)

Happy is a personal assistant for one household. It runs on a Mac mini at home under its own
macOS account, and family members talk to it by iMessage. It is built on
[OpenClaw](https://github.com/openclaw/openclaw), an open-source agent gateway. Today it uses a
cloud model (OpenAI, with response storage off and a capped project per person). Local models are
planned for later.

This repository holds the **planning side** of the project: the architecture blueprint, the
roadmap, a step-by-step runbook for each milestone (with its execution log), and the catalog of
capabilities planned next, plus the scripts that build those pages. The live configuration repo
that the runbooks deploy (`happy-config`: the family registry, encrypted secrets, evidence) is
private and is not published here.

## How it is built

- **Safest useful thing first.** Each milestone adds one new kind of risk and ends with an exit
  gate. Three tracks run underneath: security (S0–S5), observability (O0–O4) and evaluation
  (E0–E4), and a feature cannot ship ahead of the controls it needs.
- **One agent per person.** The control plane is shared: one operator, one gateway, one config
  repo, logs and backups. The data plane is split: each person's agent has its own memory,
  workspace, sessions and connected accounts. Canary evals prove that one person's agent cannot
  read another's notes.
- **Contained tools.** Agent tools run in a Docker sandbox (Colima). Secrets live in the macOS
  Keychain and SOPS. FileVault is on. The firewall is LuLu, and a local allow-list proxy limits
  where the mail tool can connect. All deploys go through root-owned `happy-deploy` and
  `happy-inspect` scripts.
- **Helpers narrow tools.** A person's main agent holds the tools and hands each job to a helper
  sub-agent that gets only the tools for that job (for example, a read-only mail reader).
- **Watched.** VictoriaMetrics and Grafana provide metrics and alerts. healthchecks.io catches
  silence, and both send their alerts to the operator's phone through ntfy. promptfoo runs the
  evals on demand and after any change to the critical path.
- **Executable plans.** Every runbook step says who does it (the operator by hand, or Claude
  Code in the admin account) and gives the exact command, a "done when" check and an official
  source. Each runbook went through several independent review rounds before it was run.
  Decisions are recorded in the operator's own words.

## Progress (as of 20 Oct 2026)

| Stage | What it delivers | Status |
|---|---|---|
| **M0** Hardened foundation | Service account, FileVault, Keychain + SOPS, tool sandbox, Tailscale, backups with a restore drill, dead-man alerts, security audit | **Done**: 50/50 steps, approved 4 Oct |
| **M1** iMessage assistant | One agent per adult on a cloud model, iMessage, web search, a home-weather tool, metrics dashboard and alert rules, evals with separation canaries | **Done**: signed off 9 Oct |
| Capability catalog | Everything planned after M1: 36 capabilities in 10 waves (A–J), each wave one runbook; 2 parked, 148 removed in review | **Final** (12–13 Oct) |
| **Wave A**: Happy reads your mail | Read-only Gmail through gog's MCP server behind a firewall rule and proxy, a 07:00 text with school mail first, a "did I get an email about X?" lookup, a daily sign-in check | **In progress**: steps A1–E5 done (15–20 Oct), next is E6; earliest exit test 27 Oct |
| Waves B–J | The second adult's inbox, web reading, photos and PDFs; memory, calendar and reminders; monitors; shared pages; voice memos; sending; lights and printing; the iPhone app; a screen-control pilot | Planned |
| Roadmap M2–M6 | Local models, research and trips, morning digest, kids' Q&A, job-hunt copilot | M2 deferred on 9 Oct in favour of the capability waves; M3/M4 folded into waves where they fit |

## What's in this repo

| File | What it is |
|---|---|
| [`home-agent-blueprint.html`](home-agent-blueprint.html) | Hardware choice, machine topology, voice design and baseline security (23 Sep – 2 Oct) |
| [`home-agent-roadmap.html`](home-agent-roadmap.html) | Milestones M0–M6, the three tracks, family data domains, and the decisions table |
| [`home-agent-m0-runbook.html`](home-agent-m0-runbook.html) | M0 runbook and execution log (source: [`m0-runbook-src/`](m0-runbook-src)) |
| [`home-agent-m1-runbook.html`](home-agent-m1-runbook.html) | M1 runbook and execution log (source: [`m1-runbook-src/`](m1-runbook-src)) |
| [`home-agent-feature-catalog.md`](home-agent-feature-catalog.md) | 9 Oct brainstorm: 105 candidate features in three levels |
| [`home-agent-capability-catalog.html`](home-agent-capability-catalog.html) | The reviewed catalog, which waves are planned from (source: [`catalog-src/`](catalog-src)) |
| [`home-agent-review-confirmation.html`](home-agent-review-confirmation.html) | Record of the over-engineering review and the operator's answers (11–12 Oct) |
| [`happy-wave-a-runbook.html`](happy-wave-a-runbook.html) | Wave A runbook (49 steps) and execution log (source: [`wave-a-runbook-src/`](wave-a-runbook-src)) |
| [`tools/redact`](tools/redact) | The privacy filter described below |

The HTML pages are self-contained. To read one, clone the repo and open the file in a browser
(GitHub shows only the source).

Each `*-runbook-src/happy-config/` folder holds the seed files that runbook adds to the config
repo, and the page embeds them. They contain placeholder values only.

## Rebuilding the pages

Edit the sources, never the output HTML.

```sh
cd m0-runbook-src && perl build.pl . local > ../home-agent-m0-runbook.html      # same for m1
cd wave-a-runbook-src && cat parts/0*.html > body.tpl.html && perl build.pl . local > ../happy-wave-a-runbook.html
cd catalog-src && python3 finalize_review.py && python3 frame.py && python3 render.py local > ../home-agent-capability-catalog.html
```

`catalog-src/data/` holds the research behind the catalog: the brainstorm, the feasibility and
security checks, the source checks, every review round, and the operator's decisions.

## Privacy in this public copy

- At commit time a git clean filter ([`tools/redact`](tools/redact)) replaces private details with
  placeholders: mail addresses, home-network and tailnet addresses, a MAC address, and the names
  of family members other than the operator. The local working copy keeps the real values, so
  the runbooks still work as written. The real values are in a file outside the repo.
- A pre-commit check blocks a commit if any staged path or file still holds one of those values,
  a denied term, a personal mail address or a real phone number.
- Not published: a few generated seed files for the second adult, the live config repo, and local
  tool state. The examples on the catalog cards are made up and say nothing about the family.

To set up the filter in another clone, which needs the private value file in
`~/.config/agent_plan/`:

```sh
git config filter.redact.clean 'tools/redact clean'
git config filter.redact.smudge 'tools/redact smudge'
git config filter.redact.required true
printf '#!/bin/sh\nexec tools/redact check\n' > .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
```

## Stack

OpenClaw 2026.9.7 · macOS 27 on a Mac mini M5 Pro (64 GB) · OpenAI `gpt-6-sol` through
per-person projects · Brave Search · gog (Gmail MCP, read-only) · LuLu · tinyproxy · Colima ·
VictoriaMetrics · Grafana · healthchecks.io · ntfy · promptfoo · SOPS/age · Tailscale. The plans
were written and reviewed with [Claude Code](https://claude.com/claude-code).
