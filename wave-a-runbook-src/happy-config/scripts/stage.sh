#!/bin/zsh
# stage.sh: copy the committed config into the staging folder that happy-deploy reads. Runs as tonyli.
# Only committed files are staged, so every deploy maps to a git revision.
set -euo pipefail
repo=${0:A:h:h}
cd "$repo"
if [[ -n "$(git status --porcelain)" ]]; then
  print -u2 "stage: commit or stash your changes first (only committed config is deployed)"
  exit 1
fi
# The generated files must match family.json5 (regenerate and commit if this fails).
[[ -f family.json5 ]] && node scripts/gen-family.mjs --check
rev=$(git rev-parse --short HEAD)
stage=/usr/local/var/happy-stage
tmp=$(mktemp -d "$stage/.incoming.XXXXXX")
trap '[[ -n ${tmp:-} && -d $tmp ]] && rm -rf -- "$tmp"' EXIT   # cleans up a failed run; no-op after the final mv
dirs=(openclaw launchd bin)
for d in observability evals plugins jobs egress; do if [[ -d $d ]]; then dirs+=($d); fi; done
git archive HEAD $dirs | tar -x -C "$tmp"

# Runtime values that happy needs, decrypted from the SOPS file (tonyli holds the age key).
if [[ -f secrets/ops.yaml ]]; then
  mkdir -p "$tmp/runtime"
  sops decrypt --extract '["hc_backup_url"]' secrets/ops.yaml > "$tmp/runtime/backup-ping-url"
  sops decrypt --extract '["hc_alerts_url"]' secrets/ops.yaml > "$tmp/runtime/hc-alerts-url"   # Grafana's watchdog (O1, B4)
  # ntfy topic -> Grafana's webhook URL, using ntfy's built-in grafana template (O1)
  topic=$(sops decrypt --extract '["ntfy_topic"]' secrets/ops.yaml)   # its own statement, so set -e stops on failure
  print -r -- "https://ntfy.sh/$topic?template=grafana" > "$tmp/runtime/ntfy-grafana-url"   # Grafana alerts (O1)
  print -r -- "https://ntfy.sh/$topic" > "$tmp/runtime/ntfy-url"                           # eval results (E0)
fi

print -r -- "$rev" > "$tmp/REVISION"
chmod -R u=rwX,g=rX,o= "$tmp"          # happy reads through the shared "staff" group
old="$stage/.old.$$"
[[ -d "$stage/current" ]] && mv "$stage/current" "$old"
mv "$tmp" "$stage/current"
rm -rf "$old"
print "staged $rev -> $stage/current"
