# happy-config

Source of truth for the OpenClaw gateway that runs as the `happy` user on the Mac mini.
Edited only in the admin account (tonyli). Applied only through the deploy path:

    scripts/stage.sh                                   # stage the committed revision
    sudo -u happy /usr/local/libexec/happy-deploy        # apply it as happy
    sudo -u happy /usr/local/libexec/happy-inspect drift # confirm live == staged

Layout
- openclaw/openclaw.json        hardened gateway config (JSON5, SecretRefs only, no secrets)
- openclaw/bin/keychain-resolver  exec SecretRef provider reading happy's login Keychain
- launchd/                      happy LaunchAgents: Colima, Ollama, nightly backup
- bin/                          scripts installed to /Users/happy/bin
- system/                       root-owned pieces installed once with sudo (deploy, inspect,
                                healthcheck probe, LaunchDaemon, sudoers drop-in)
- secrets/ops.yaml              SOPS-encrypted endpoints (healthchecks ping URLs, ntfy topic)
- baseline/                     audit output, memory baseline and the M0 sign-off
