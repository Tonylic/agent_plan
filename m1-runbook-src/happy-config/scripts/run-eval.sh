#!/bin/zsh
# run-eval.sh: start the E0 eval suite now, on demand. Runs as tonyli; the run itself is happy's
# (local.happy.eval). Takes 10-20 minutes; the result arrives on your phone through ntfy, and
# `sudo -n -u happy /usr/local/libexec/happy-inspect eval-latest` shows the details.
exec sudo -n -u happy /usr/local/libexec/happy-deploy --run-eval
