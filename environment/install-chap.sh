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

echo "=== uv version ==="
uv --version

echo "=== creating $ENVDIR on python $PYTHON_VERSION ==="
uv venv --python "$PYTHON_VERSION" "$ENVDIR"

echo "=== installing chap-core==$CHAP_VERSION ==="
VIRTUAL_ENV="$ENVDIR" uv pip install --python "$ENVDIR/bin/python" "chap-core==$CHAP_VERSION"

echo "=== resolved package set -> environment/lock.txt ==="
{
  echo "# Resolved analysis environment. Produced by environment/install-chap.sh."
  echo "# chap-core==$CHAP_VERSION on CPython $("$ENVDIR/bin/python" -c 'import platform;print(platform.python_version())')"
  echo "# Built $(date -u +%Y-%m-%dT%H:%M:%SZ) on $(uname -srm)"
  VIRTUAL_ENV="$ENVDIR" uv pip freeze --python "$ENVDIR/bin/python"
} > "$HERE/lock.txt"

echo "=== chap version ==="
"$ENVDIR/bin/chap" --version || true
