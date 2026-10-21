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
rev=$(git rev-parse --short HEAD)
stage=/usr/local/var/happy-stage
tmp=$(mktemp -d "$stage/.incoming.XXXXXX")
trap '[[ -n ${tmp:-} && -d $tmp ]] && rm -rf -- "$tmp"' EXIT   # cleans up a failed run; no-op after the final mv
git archive HEAD openclaw launchd bin | tar -x -C "$tmp"

# Runtime values that happy needs, decrypted from the SOPS file (tonyli holds the age key).
if [[ -f secrets/ops.yaml ]]; then
  mkdir -p "$tmp/runtime"
  sops decrypt --extract '["hc_backup_url"]' secrets/ops.yaml > "$tmp/runtime/backup-ping-url"
fi

print -r -- "$rev" > "$tmp/REVISION"
chmod -R u=rwX,g=rX,o= "$tmp"          # happy reads through the shared "staff" group
old="$stage/.old.$$"
[[ -d "$stage/current" ]] && mv "$stage/current" "$old"
mv "$tmp" "$stage/current"
rm -rf "$old"
print "staged $rev -> $stage/current"
