#!/usr/bin/env bash
# Build the analysis environment: a project-local virtual environment holding a pinned
# chap-core, invoked as environment/chapenv/bin/chap.
#
# Run from the repository root:  bash environment/install-chap.sh
#
# Why a project-local venv rather than the documented `uv tool install chap-core`: a tool
# install lands in the operator's ~/.local/share/uv/tools, outside the repository and
# outside anything analysis/run.sh can rebuild. The pinned version is the same either way;
# the location is what makes it reproducible from the repository alone.

set -euo pipefail

CHAP_VERSION="${CHAP_VERSION:-2.1.0}"
PYTHON_VERSION="${PYTHON_VERSION:-3.13.0}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENVDIR="$HERE/chapenv"

# `uv pip freeze`, as plain text.
#
# uv colours its output when the invoking shell asks for it (FORCE_COLOR, CLICOLOR_FORCE).
# Both uses of the freeze below are machine-read -- one is diffed against lock.txt, the
# other *becomes* lock.txt -- so escape codes are corruption in both. Batch 27's clean-room
# run was launched from a shell with FORCE_COLOR=3 and the comparison reported
# `DOES NOT MATCH environment/lock.txt` against an environment that matched it exactly:
# every one of the 174 lines differed by its colour wrapper, and `sort` ordered the
# wrapped names differently as well. A lockfile written the same way would not install.
# NO_COLOR asks uv not to colour; the sed removes it if something else still does.
freeze() {
  NO_COLOR=1 VIRTUAL_ENV="$ENVDIR" uv pip freeze --python "$ENVDIR/bin/python" \
    | sed $'s/\033\[[0-9;]*m//g'
}

echo "=== uv version ==="
uv --version

echo "=== creating $ENVDIR on python $PYTHON_VERSION ==="
uv venv --python "$PYTHON_VERSION" "$ENVDIR"

# Install from the lockfile when there is one, and resolve only when there is not.
#
# This is the whole of Rule 3 in two branches, and getting it the other way round is how a
# pinned environment stops being pinned without anyone noticing. The first version of this
# script always resolved `chap-core==2.1.0` afresh and then *wrote* lock.txt from what it
# got, so the lockfile was a report of one install rather than a specification of the next.
# Rebuilding three days later resolved a different package set -- click 8.4.2 became 8.5.0,
# cryptography moved, and a dozen others -- while the file claiming to be what reproduces
# sat unchanged in git. The environment README said "this is what reproduces"; it was not,
# because nothing installed from it. environment/Dockerfile always did, which is why the
# image and the local environment could drift apart.
#
# Set RESOLVE=1 to deliberately re-resolve and rewrite the lockfile. That is a
# methodological change and belongs in a commit that says so.
if [ -f "$HERE/lock.txt" ] && [ "${RESOLVE:-0}" != "1" ]; then
  echo "=== installing the pinned package set from environment/lock.txt ==="
  VIRTUAL_ENV="$ENVDIR" uv pip install --python "$ENVDIR/bin/python" -r "$HERE/lock.txt"
else
  echo "=== resolving chap-core==$CHAP_VERSION afresh (RESOLVE=1 or no lockfile) ==="
  VIRTUAL_ENV="$ENVDIR" uv pip install --python "$ENVDIR/bin/python" "chap-core==$CHAP_VERSION"

  echo "=== resolved package set -> environment/lock.txt ==="
  {
    echo "# Resolved analysis environment. Produced by environment/install-chap.sh."
    echo "# chap-core==$CHAP_VERSION on CPython $("$ENVDIR/bin/python" -c 'import platform;print(platform.python_version())')"
    echo "# Built $(date -u +%Y-%m-%dT%H:%M:%SZ) on $(uname -srm)"
    freeze
  } > "$HERE/lock.txt"
fi

echo "=== the built environment against the lockfile ==="
# Reported, not asserted. A difference here means the environment is not what the
# repository says it is, and the run that follows would be unrecordable.
freeze > "$HERE/.freeze.tmp"
if diff <(grep -v '^#' "$HERE/lock.txt" | sort) <(sort "$HERE/.freeze.tmp") > "$HERE/.lockdiff.tmp"; then
  echo "matches environment/lock.txt exactly ($(grep -vc '^#' "$HERE/lock.txt") packages)"
else
  echo "DOES NOT MATCH environment/lock.txt:"
  echo "  in the lockfile, not installed: $(grep -c '^<' "$HERE/.lockdiff.tmp")"
  echo "  installed, not in the lockfile: $(grep -c '^>' "$HERE/.lockdiff.tmp")"
  head -60 "$HERE/.lockdiff.tmp"
fi
rm -f "$HERE/.freeze.tmp" "$HERE/.lockdiff.tmp"

echo "=== chap version ==="
"$ENVDIR/bin/chap" --version || true
