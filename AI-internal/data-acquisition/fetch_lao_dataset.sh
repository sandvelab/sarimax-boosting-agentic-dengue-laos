#!/usr/bin/env bash
# Fetch the three Lao files of the CHAP harmonized dataset at a pinned commit.
#
# Writes into Archive/lao-dataset/, which is write-once: the script refuses to
# overwrite an existing file, because Archive/ is never edited (AGENTS.md §8).
# Re-running it against a populated archive therefore *verifies* rather than
# refetches -- it recomputes the checksums and reports any disagreement.
#
# Usage:  bash AI-internal/data-acquisition/fetch_lao_dataset.sh          # fetch or verify
#         bash AI-internal/data-acquisition/fetch_lao_dataset.sh --verify # verify only
set -euo pipefail

REPO="dhis2/climate-health-data"
# Pinned: HEAD of main on 2026-08-23, resolved via the GitHub API, recorded in
# Archive/lao-dataset/provenance.md. An unpinned fetch would make every number in
# this project depend on another repository's current state.
COMMIT="af362d5260c6e7de1739f3d05314a844bd272613"
FILES=(
  "chap_LAO_admin1_monthly.csv"
  "chap_LAO_admin1_monthly.geojson"
  "chap_LAO_admin1_monthly_schema.json"
)

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DEST="$ROOT/Archive/lao-dataset"
MANIFEST="$DEST/sha256sums.txt"
VERIFY_ONLY="${1:-}"

mkdir -p "$DEST"

for f in "${FILES[@]}"; do
  if [[ -f "$DEST/$f" ]]; then
    echo "present, not refetched: $f"
    continue
  fi
  if [[ "$VERIFY_ONLY" == "--verify" ]]; then
    echo "MISSING (verify-only run): $f" >&2
    exit 1
  fi
  url="https://raw.githubusercontent.com/$REPO/$COMMIT/lao/$f"
  echo "fetching $url"
  curl -fsSL --retry 3 -o "$DEST/$f" "$url"
done

# Checksums: written on the first run, checked on every later one.
cd "$DEST"
if [[ -f "$MANIFEST" ]]; then
  echo "--- verifying against $MANIFEST ---"
  shasum -a 256 -c "$MANIFEST"
else
  shasum -a 256 "${FILES[@]}" > "$MANIFEST"
  echo "--- wrote $MANIFEST ---"
  cat "$MANIFEST"
fi

echo "repository: $REPO"
echo "commit:     $COMMIT"
