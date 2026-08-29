#!/usr/bin/env bash
# Fetch the annual Lao national population series the population fork back-casts from.
#
# The archived dataset carries one population figure per province for the whole
# 1998-2010 record -- a WorldPop snapshot the schema dates to 2020. The alternative
# child of `02_setup/01_population` needs a per-year series to scale it by, and the
# repository holds none. This script brings one in.
#
# Writes into Archive/lao-population/, which is write-once for the same reason
# Archive/lao-dataset/ is: Archive/ is never edited (AGENTS.md §8). Re-running the
# script against a populated archive therefore *verifies* rather than refetches.
#
# Usage:  bash AI-internal/data-acquisition/fetch_lao_population.sh          # fetch or verify
#         bash AI-internal/data-acquisition/fetch_lao_population.sh --verify # verify only
set -euo pipefail

# World Bank Open Data, indicator SP.POP.TOTL (population, total), Lao PDR. The World
# Bank redistributes the UN World Population Prospects estimates under CC BY 4.0.
#
# There is no commit to pin here, which is a weaker guarantee than the dataset has:
# the World Bank revises the series and the same URL returns different numbers after a
# revision. Two things stand in for a commit. The request fixes the year range, so the
# rows do not move for reasons of coverage; and the response carries a `lastupdated`
# field naming the vintage, which is recorded in provenance.md beside the checksum of
# the bytes actually stored. The analysis reads the archived file, never the API, so
# the project reproduces from the archive whatever the World Bank does later.
INDICATOR="SP.POP.TOTL"
COUNTRY="LAO"
YEARS="1990:2021"
FILE="worldbank_${INDICATOR}_${COUNTRY}_${YEARS/:/-}.json"
URL="https://api.worldbank.org/v2/country/${COUNTRY}/indicator/${INDICATOR}?format=json&per_page=200&date=${YEARS}"

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DEST="$ROOT/Archive/lao-population"
MANIFEST="$DEST/sha256sums.txt"
VERIFY_ONLY="${1:-}"

mkdir -p "$DEST"

if [[ -f "$DEST/$FILE" ]]; then
  echo "present, not refetched: $FILE"
else
  if [[ "$VERIFY_ONLY" == "--verify" ]]; then
    echo "MISSING (verify-only run): $FILE" >&2
    exit 1
  fi
  echo "fetching $URL"
  curl -fsSL --retry 3 -o "$DEST/$FILE" "$URL"
fi

cd "$DEST"
if [[ -f "$MANIFEST" ]]; then
  echo "--- verifying against $MANIFEST ---"
  shasum -a 256 -c "$MANIFEST"
else
  shasum -a 256 "$FILE" > "$MANIFEST"
  echo "--- wrote $MANIFEST ---"
  cat "$MANIFEST"
fi

echo "indicator: $INDICATOR"
echo "country:   $COUNTRY"
echo "years:     $YEARS"
echo "vintage:   $(sed -n 's/.*"lastupdated":"\([^"]*\)".*/\1/p' "$FILE" | head -1)"
