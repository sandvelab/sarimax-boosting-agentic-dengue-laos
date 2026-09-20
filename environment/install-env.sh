#!/usr/bin/env bash
# Build the pinned analysis environment at environment/env/, from lock.txt.
# RESOLVE=1 re-resolves environment.yml's dependencies and rewrites lock.txt instead.
set -euo pipefail
cd "$(dirname "$0")/.."

PY=3.13
ENV_DIR="environment/env"
LOCK="environment/lock.txt"

rm -rf "$ENV_DIR"
uv venv --python "$PY" "$ENV_DIR" >/dev/null

if [[ "${RESOLVE:-}" == "1" || ! -f "$LOCK" ]]; then
    uv pip install --python "$ENV_DIR/bin/python" \
        pandas numpy scipy statsmodels properscoring
    uv pip freeze --python "$ENV_DIR/bin/python" > "$LOCK"
    echo "Resolved and wrote $LOCK"
else
    uv pip install --python "$ENV_DIR/bin/python" -r "$LOCK"
    built="$(uv pip freeze --python "$ENV_DIR/bin/python" | sort)"
    locked="$(sort "$LOCK")"
    if [[ "$built" != "$locked" ]]; then
        echo "WARNING: built environment differs from $LOCK:"
        diff <(echo "$locked") <(echo "$built") || true
    else
        echo "Built environment matches $LOCK exactly."
    fi
fi

"$ENV_DIR/bin/python" -V
