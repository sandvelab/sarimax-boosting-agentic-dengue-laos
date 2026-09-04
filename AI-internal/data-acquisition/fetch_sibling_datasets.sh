#!/usr/bin/env bash
# Fetch the Thai and Vietnamese files of the CHAP harmonized dataset, at the same
# pinned commit as the Lao files.
#
# These are the sibling datasets the plan's §4 names as the optional external check:
# they are not part of the headline analysis and no model is developed on them. The
# check runs the reported model unchanged on each of them, so the only thing this
# script has to guarantee is that the files are the ones a later reader can refetch.
#
# Writes into Archive/sibling-datasets/, which is write-once: the script refuses to
# overwrite an existing file, because Archive/ is never edited (AGENTS.md §8).
# Re-running it against a populated archive therefore *verifies* rather than
# refetches -- it recomputes the checksums and reports any disagreement.
#
# Usage:  bash AI-internal/data-acquisition/fetch_sibling_datasets.sh          # fetch or verify
#         bash AI-internal/data-acquisition/fetch_sibling_datasets.sh --verify # verify only
set -euo pipefail

REPO="dhis2/climate-health-data"
# The same commit the Lao files are pinned at, resolved on 2026-08-23 and recorded in
# Archive/lao-dataset/provenance.md. One pin for the whole repository: the external
# check compares three countries drawn from one state of one dataset, and a sibling
# fetched at a later commit would be a different harmonisation as well as a different
# country.
COMMIT="af362d5260c6e7de1739f3d05314a844bd272613"

COUNTRIES=("tha:THA" "vnm:VNM")
SUFFIXES=("csv" "geojson" "schema.json")

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DEST="$ROOT/Archive/sibling-datasets"
VERIFY_ONLY="${1:-}"

for pair in "${COUNTRIES[@]}"; do
  dir="${pair%%:*}"
  code="${pair##*:}"
  mkdir -p "$DEST/$dir"
  for suffix in "${SUFFIXES[@]}"; do
    case "$suffix" in
      "schema.json") f="chap_${code}_admin1_monthly_schema.json" ;;
      *)             f="chap_${code}_admin1_monthly.${suffix}" ;;
    esac
    if [[ -f "$DEST/$dir/$f" ]]; then
      echo "present, not refetched: $dir/$f"
      continue
    fi
    if [[ "$VERIFY_ONLY" == "--verify" ]]; then
      echo "MISSING (verify-only run): $dir/$f" >&2
      exit 1
    fi
    url="https://raw.githubusercontent.com/$REPO/$COMMIT/$dir/$f"
    echo "fetching $url"
    curl -fsSL --retry 3 -o "$DEST/$dir/$f" "$url"
  done
done

# Checksums: written on the first run, checked on every later one. One manifest for
# both countries, with paths relative to Archive/sibling-datasets/.
cd "$DEST"
MANIFEST="sha256sums.txt"
FILES=()
for pair in "${COUNTRIES[@]}"; do
  dir="${pair%%:*}"
  code="${pair##*:}"
  FILES+=("$dir/chap_${code}_admin1_monthly.csv"
          "$dir/chap_${code}_admin1_monthly.geojson"
          "$dir/chap_${code}_admin1_monthly_schema.json")
done
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
