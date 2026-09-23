#!/usr/bin/env bash
# `/release check`: the safety scan that must precede anything becoming public (Rule 10).
#
# Two questions, answered from the repository and its whole history rather than from memory:
#   1. Secrets — is there a key, token, password or credential file anywhere in the tracked
#      tree or in any commit that has ever existed here?
#   2. Data permission — which data files would be published, and what does each one's own
#      provenance record say about whether it may be?
# and two that a public repository should be able to answer as well:
#   3. Identifying strings — home-directory paths and e-mail addresses in tracked files.
#   4. Size — the largest tracked files and the size of the history.
#
# Nothing here is fixed by the script. It writes what it found to
# AI-generated/validation/<date>_release-scan/ (tracked) and exits non-zero only when a
# secret-shaped string or a credential-shaped filename is found; everything else is reported
# for a reader to judge. The distinction matters: a `password` in prose about scanning for
# passwords is not a leak, and a scan that cannot tell the two apart is ignored after its
# second false alarm.
#
#   AI-internal/useful-scripts/release_scan.sh
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
STAMP="$(date +%Y-%m-%d)"
OUT="$ROOT/AI-generated/validation/${STAMP}_release-scan"
mkdir -p "$OUT"

say() { echo "[release-scan] $*"; }

# --- 1a. Secret-shaped strings: token formats that are a leak whenever they appear. ---------
# Matched in every tracked file at HEAD and in every blob of every commit. Prose that talks
# about tokens does not match these; an actual token does.
TOKEN_RE='AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|gho_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{22,}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|sk-[A-Za-z0-9]{32,}|sk-ant-[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{35}|eyJ[A-Za-z0-9_-]{20,}\.eyJ[A-Za-z0-9_-]{20,}|https?://[^/[:space:]:@]+:[^/[:space:]@]+@[^/[:space:]]+'
# Assignments of a secret-like name to a quoted literal of eight or more characters.
ASSIGN_RE='(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|passw(or)?d)[[:space:]]*[:=][[:space:]]*["'"'"'][^"'"'"'[:space:]]{8,}["'"'"']'

say "--- 1a. secret-shaped strings in tracked files at HEAD ---"
git grep -I -n -E "$TOKEN_RE|$ASSIGN_RE" -- . ":!AI-generated/validation/*_release-scan/*" ":!AI-internal/useful-scripts/release_scan.sh" \
  > "$OUT/secrets_tracked.txt" 2>/dev/null
N_SECRET_TRACKED=$(grep -c . "$OUT/secrets_tracked.txt" || true)
say "$N_SECRET_TRACKED hit(s)"

say "--- 1b. secret-shaped strings in every line ever added, across the whole history ---"
# One pass over the full patch history: every line any commit ever added, so a secret that
# was committed and later removed is still found. Lines from this script and from earlier
# scan outputs are dropped, since they contain the patterns being searched for.
# Lines longer than 4,000 characters are data, not code or prose — the archived boundary
# polygons are single lines megabytes long, and a regex engine does not finish on them. They
# are counted and skipped, and the count is reported, so the omission is visible.
N_COMMITS=$(git rev-list --all | wc -l | tr -d ' ')
LC_ALL=C git log --all -p --no-color --format='### commit %h %ad %s' --date=short \
  | LC_ALL=C awk -v skipfile="$OUT/secrets_history_skipped_long_lines.txt" '
      /^### commit /{c=$0; next} /^diff --git /{f=$0; next}
      /^\+/{ if (length($0) > 4000) { skipped++; next } print c "\t" f "\t" $0 }
      END { print skipped+0 > skipfile }' \
  | LC_ALL=C grep -v -E 'release_scan\.sh|_release-scan/' \
  | LC_ALL=C grep -E "$TOKEN_RE|$ASSIGN_RE" \
  > "$OUT/secrets_history.txt" || true
N_SECRET_HISTORY=$(grep -c . "$OUT/secrets_history.txt" || true)
N_SKIPPED_LONG=$(cat "$OUT/secrets_history_skipped_long_lines.txt" 2>/dev/null || echo 0)
say "$N_SECRET_HISTORY hit(s) across $N_COMMITS commits; $N_SKIPPED_LONG added line(s) over 4,000 characters skipped as data"

say "--- 1c. credential-shaped filenames anywhere in the history ---"
git log --all --pretty=format: --name-only | sort -u | grep -v '^$' \
  | grep -E '(^|/)\.env($|\.)|\.pem$|\.p12$|\.pfx$|\.key$|id_rsa|id_ed25519|id_ecdsa|\.netrc$|credentials?(\.|$)|secrets?\.(json|ya?ml|txt|toml)$|\.npmrc$|\.pypirc$|kubeconfig|\.htpasswd$|settings\.local\.json$' \
  > "$OUT/credential_filenames_history.txt" || true
N_CRED_FILES=$(grep -c . "$OUT/credential_filenames_history.txt" || true)
say "$N_CRED_FILES hit(s)"

say "--- 1d. secret-like words in tracked prose, for a reader (not a failure) ---"
git grep -I -n -i -E '(^|[^A-Za-z_])(api[_-]?key|secret|token|password|passwd|credential)s?([^A-Za-z_]|$)' -- . \
  ":!AI-generated/validation/*_release-scan/*" ":!AI-internal/useful-scripts/release_scan.sh" \
  > "$OUT/secret_words_prose.txt" 2>/dev/null || true
N_WORDS=$(grep -c . "$OUT/secret_words_prose.txt" || true)
say "$N_WORDS line(s) mention such a word; listed for reading"

# --- 2. Data permission -------------------------------------------------------------------
say "--- 2. data files that would be published, and what their provenance says ---"
{
  echo "# Data files in the tracked tree, and the governance statement in each folder's provenance.md"
  echo
  echo "## Imported data (Archive/)"
  for d in $(git ls-files 'Archive/**' | xargs -n1 dirname | sort -u); do
    files=$(git ls-files "$d" | grep -E '\.(csv|json|geojson|tsv|parquet|nc|xlsx)$' | grep -v -E 'schema|sha256' || true)
    [[ -z "$files" ]] && continue
    echo
    echo "### $d"
    echo "$files" | sed 's/^/- /'
    prov=""
    for cand in "$d/provenance.md" "$(dirname "$d")/provenance.md"; do
      [[ -f "$cand" ]] && { prov="$cand"; break; }
    done
    if [[ -n "$prov" ]]; then
      echo "provenance: $prov"
      grep -n -i -A2 -E 'licen[cs]e|governance' "$prov" | sed 's/^/    /' || echo "    (no licence/governance line found)"
    else
      echo "provenance: NONE FOUND"
    fi
  done
  echo
  echo "## Derived data (analysis/**/results/) — produced here from the imported data above"
  echo "count: $(git ls-files 'analysis/**/results/**' | grep -E '\.(csv|json|tsv)$' | wc -l | tr -d ' ') tracked result files"
  echo
  echo "## Files a data-permission reader should know are NOT tracked"
  for f in .env .claude/settings.local.json; do
    if [[ -e "$f" ]]; then
      if git check-ignore -q "$f"; then echo "- $f: present in the working tree, gitignored, not tracked"; else echo "- $f: PRESENT AND NOT IGNORED"; fi
    else
      echo "- $f: not present"
    fi
  done
} > "$OUT/data_permission.md"
N_ARCHIVE_DATA=$(git ls-files 'Archive/**' | grep -E '\.(csv|json|geojson)$' | grep -v -E 'schema|sha256' | wc -l | tr -d ' ')
say "$N_ARCHIVE_DATA imported data file(s) listed with their governance statements"

# --- 3. Identifying strings ---------------------------------------------------------------
say "--- 3. home-directory paths and e-mail addresses in tracked files ---"
git grep -I -n -E '/Users/[A-Za-z0-9._-]+|/home/[A-Za-z0-9._-]+|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' -- . \
  ":!AI-generated/validation/*_release-scan/*" ":!AI-internal/useful-scripts/release_scan.sh" \
  | grep -v -E '/Users/you/|noreply@|example\.(com|org)' \
  > "$OUT/identifying_tracked.txt" 2>/dev/null || true
N_IDENT=$(grep -c . "$OUT/identifying_tracked.txt" || true)
say "$N_IDENT line(s); the committer identity in git metadata is separate and listed below"
{
  echo "# Author identities recorded in commit metadata (published with any push)"
  git log --all --format='%an <%ae>' | sort -u
} > "$OUT/git_identities.txt"

# --- 4. Size ------------------------------------------------------------------------------
say "--- 4. size ---"
{
  echo "# Largest tracked files (KB) and repository size"
  git ls-files -z | xargs -0 du -k 2>/dev/null | sort -rn | head -15
  echo
  git count-objects -vH
} > "$OUT/size.txt"
N_LARGE=$(git ls-files -z | xargs -0 du -k 2>/dev/null | awk '$1 > 5120' | wc -l | tr -d ' ')
say "$N_LARGE tracked file(s) over 5 MB"

# --- Summary ------------------------------------------------------------------------------
FAIL=0
[[ "$N_SECRET_TRACKED" -gt 0 || "$N_SECRET_HISTORY" -gt 0 || "$N_CRED_FILES" -gt 0 ]] && FAIL=1
cat > "$OUT/summary.json" <<EOF
{
  "date": "$STAMP",
  "head": "$(git rev-parse --short HEAD)",
  "commits_scanned": $N_COMMITS,
  "secret_shaped_hits_tracked": $N_SECRET_TRACKED,
  "secret_shaped_hits_history": $N_SECRET_HISTORY,
  "history_added_lines_over_4000_chars_skipped": $N_SKIPPED_LONG,
  "credential_filenames_history": $N_CRED_FILES,
  "secret_word_prose_lines_for_reading": $N_WORDS,
  "imported_data_files": $N_ARCHIVE_DATA,
  "identifying_lines_tracked": $N_IDENT,
  "tracked_files_over_5mb": $N_LARGE,
  "secrets_scan_failed": $([[ $FAIL -eq 1 ]] && echo true || echo false),
  "note": "secrets_scan_failed is the only automatic verdict. Data permission and identifying strings are listed for a reader; the scan cannot judge them."
}
EOF
say "summary in $OUT/summary.json"
if [[ $FAIL -eq 1 ]]; then say "SECRETS SCAN FAILED — read the files above before anything is pushed"; exit 1; fi
say "no secret-shaped string or credential-shaped filename found in the tree or its history"
exit 0
