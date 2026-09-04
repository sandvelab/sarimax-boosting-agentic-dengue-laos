#!/usr/bin/env bash
# Main script for node: 03_siblings
# Generated shape -- edit the "own scripts" block; the child calls are maintained
# by `node.py rebuild`, which enforces the alternatives/sub-analyses semantics.
set -euo pipefail
cd "$(dirname "$0")"
REPO_ROOT="$(cd "../../.." && pwd)"
# Node scripts run under the pinned analysis environment (AGENTS.md §2), not under
# .venv, which is the repository's own machinery. A node needing something beyond it
# declares env/ and overrides PYTHON below.
PYTHON="$REPO_ROOT/environment/chapenv/bin/python"


# Own scripts -- the cut first, then the check that the schemes land where the mirror
# requires. The second reads the files the first writes.
"$PYTHON" "scripts/partition_siblings.py"
"$PYTHON" "scripts/check_external_scheme.py"
