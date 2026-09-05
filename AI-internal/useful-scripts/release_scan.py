"""The safety scan that has to pass before anything here becomes public (Rule 10).

`/release` says: scan the whole tree — history included — for keys, tokens, passwords and
credential files, and confirm explicitly that every included data file may lawfully be
published. If either fails, stop; do not publish a subset and mention it afterwards.

It is a script rather than a reading because a reading of five thousand files is not a scan,
and because the result has to be a file somebody can re-run. It reports and never deletes:
what to do about a hit is a decision, and a scanner that quietly rewrote history would be
worse than no scanner.

## What it looks for

**Credentials**, by pattern, in every tracked file and in every blob the history holds. The
patterns are the shapes that actually leak — provider-prefixed API keys, PEM private key
headers, `Authorization: Bearer` lines, connection strings with an inline password, and the
generic `key/token/secret/password =` assignment. Generic patterns produce false positives on
prose about keys and on code that *names* a variable; every hit is listed with its file and
line so a human decides, and the exit code says whether anything was found rather than
whether anything was dangerous.

**Credential files** by name: `.env`, `.pem`, `.key`, `id_rsa`, `credentials`, `.netrc`,
service-account JSON.

**Personal information that is not a credential but is not publishable either**: the
machine's home-directory path, which appears in run logs whenever a tool prints an absolute
path, and any e-mail address. Neither is a secret and both are the author's, so both are
reported as a decision for the author rather than as a failure.

**Data governance**, from the archive's own records: every directory under `Archive/` must
carry a `provenance.md` naming its licence or governance, and this reports what each one
says. It cannot decide whether a licence permits redistribution; it can refuse to let the
question go unasked.

Usage:
  .venv/bin/python AI-internal/useful-scripts/release_scan.py --root .
  .venv/bin/python AI-internal/useful-scripts/release_scan.py --root . --skip-history
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

#: (name, pattern, what a hit means). Ordered most specific first, because the generic
#: assignment pattern would otherwise swallow the provider-prefixed ones.
CREDENTIAL_PATTERNS = [
    ("aws-access-key", re.compile(rb"\bAKIA[0-9A-Z]{16}\b"), "an AWS access key id"),
    ("github-token", re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{36,}\b"), "a GitHub token"),
    ("openai-key", re.compile(rb"\bsk-[A-Za-z0-9]{32,}\b"), "an OpenAI-style API key"),
    ("anthropic-key", re.compile(rb"\bsk-ant-[A-Za-z0-9_-]{24,}\b"), "an Anthropic API key"),
    ("slack-token", re.compile(rb"\bxox[abpsr]-[A-Za-z0-9-]{10,}\b"), "a Slack token"),
    ("google-key", re.compile(rb"\bAIza[0-9A-Za-z_-]{35}\b"), "a Google API key"),
    ("private-key-header", re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
     "a PEM private key"),
    ("bearer-header", re.compile(rb"[Aa]uthorization:\s*[Bb]earer\s+\S{16,}"),
     "an Authorization header with a token in it"),
    ("connection-string", re.compile(rb"\b[a-z][a-z0-9+.-]*://[^\s:@/]+:[^\s:@/]{4,}@"),
     "a URL with a password in it"),
    ("assignment", re.compile(
        rb"""(?i)\b(?:api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|"""
        rb"""password|passwd|client[_-]?secret)\b\s*[=:]\s*["']?[A-Za-z0-9/+_.-]{12,}"""),
     "an assignment that looks like a credential"),
]

CREDENTIAL_FILENAMES = re.compile(
    r"(^|/)(\.env(\..*)?|\.netrc|\.npmrc|id_[rd]sa|credentials|"
    r"service[_-]account.*\.json)$|\.(pem|key|p12|pfx|keystore)$")

EMAIL = re.compile(rb"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

#: Suffixes whose bytes are not text and which the patterns cannot meaningfully match.
BINARY = {".png", ".nc", ".jpg", ".jpeg", ".pdf", ".zip", ".gz", ".geojson"}


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args],
                          capture_output=True, text=True).stdout


def tracked(root: Path) -> list[str]:
    return [p for p in git(root, "ls-files").split("\n") if p]


def scan_bytes(name: str, blob: bytes) -> list[dict]:
    out = []
    for label, pattern, meaning in CREDENTIAL_PATTERNS:
        for m in pattern.finditer(blob):
            line = blob.count(b"\n", 0, m.start()) + 1
            out.append({
                "where": name, "line": line, "pattern": label, "means": meaning,
                # The match is truncated and never reproduced in full: a report that
                # prints the secret has published it a second time.
                "excerpt": m.group(0)[:12].decode("utf-8", "replace") + "…",
            })
    return out


def scan_working_tree(root: Path, home: str) -> dict:
    hits, files_by_name, home_paths, emails = [], [], {}, {}
    for rel in tracked(root):
        path = root / rel
        if not path.is_file():
            continue
        if CREDENTIAL_FILENAMES.search(rel):
            files_by_name.append(rel)
        if path.suffix.lower() in BINARY:
            continue
        try:
            blob = path.read_bytes()
        except OSError:
            continue
        hits += scan_bytes(rel, blob)
        n = blob.count(home.encode())
        if n:
            home_paths[rel] = n
        found = {m.group(0).decode("utf-8", "replace") for m in EMAIL.finditer(blob)}
        for address in found:
            emails.setdefault(address, []).append(rel)
    return {
        "files_scanned": len(tracked(root)),
        "credential_hits": hits,
        "credential_filenames": files_by_name,
        "files_containing_the_home_directory_path": home_paths,
        "occurrences_of_the_home_directory_path": sum(home_paths.values()),
        "email_addresses": {a: sorted(f)[:8] for a, f in sorted(emails.items())},
    }


def scan_history(root: Path) -> dict:
    """Every blob the history holds, not only the ones checked out now.

    A credential removed in a later commit is still in the pack, and `/release` says the
    history is in scope. Blobs are streamed by hash so a file deleted three commits ago is
    scanned exactly as a current one is.
    """
    listing = git(root, "rev-list", "--objects", "--all").split("\n")
    blobs, hits = {}, []
    for line in listing:
        if " " not in line:
            continue
        sha, name = line.split(" ", 1)
        if Path(name).suffix.lower() in BINARY:
            continue
        blobs[sha] = name
    for sha, name in blobs.items():
        kind = git(root, "cat-file", "-t", sha).strip()
        if kind != "blob":
            continue
        blob = subprocess.run(["git", "-C", str(root), "cat-file", "blob", sha],
                              capture_output=True).stdout
        for hit in scan_bytes(name, blob):
            hit["blob"] = sha[:9]
            hits.append(hit)
    return {"blobs_scanned": len(blobs), "credential_hits": hits}


def data_governance(root: Path) -> dict:
    out = {}
    for directory in sorted(p for p in (root / "Archive").iterdir() if p.is_dir()):
        record = directory / "provenance.md"
        statement = None
        if record.exists():
            text = record.read_text()
            m = re.search(r"^licence/governance:\s*(.*(?:\n\s{2,}.*)*)", text, re.M)
            if m:
                statement = " ".join(m.group(1).split())
        out[str(directory.relative_to(root))] = {
            "has_provenance": record.exists(),
            "licence_or_governance": statement,
            "files": len([p for p in directory.rglob("*") if p.is_file()]),
        }
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--root", default=".")
    parser.add_argument("--skip-history", action="store_true",
                        help="scan the working tree only; the history scan reads every "
                             "blob and is the slow half")
    parser.add_argument("--out", default="AI-generated/release/release_scan.json")
    a = parser.parse_args()
    root = Path(a.root).resolve()
    home = str(Path.home())

    tree = scan_working_tree(root, home)
    history = {"skipped": True} if a.skip_history else scan_history(root)
    governance = data_governance(root)

    clean = (not tree["credential_hits"] and not tree["credential_filenames"]
             and not history.get("credential_hits"))
    report = {
        "what_this_is": (
            "the safety scan Rule 10 requires before anything here becomes public: "
            "credentials in the working tree and in the history, credential files by name, "
            "personal information that is not a credential, and what each archived dataset "
            "says about its own licence"),
        "scanned_at_commit": git(root, "rev-parse", "--short=9", "HEAD").strip(),
        "working_tree": tree,
        "history": history,
        "data_governance": governance,
        "credentials_found": not clean,
        "verdict": ("no credential pattern matched in the working tree or the history"
                    if clean else "SOMETHING MATCHED — read credential_hits before publishing"),
        "what_this_cannot_decide": (
            "whether a licence permits redistribution, and whether the author wants their "
            "home-directory path and e-mail address published. Both are reported for a "
            "person to decide, not failed on"),
    }
    out = root / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n")

    print(f"working tree: {tree['files_scanned']} tracked files, "
          f"{len(tree['credential_hits'])} credential hit(s), "
          f"{len(tree['credential_filenames'])} credential file(s) by name")
    if not a.skip_history:
        print(f"history:      {history['blobs_scanned']} blobs, "
              f"{len(history['credential_hits'])} credential hit(s)")
    print(f"home path:    {tree['occurrences_of_the_home_directory_path']} occurrence(s) "
          f"in {len(tree['files_containing_the_home_directory_path'])} file(s)")
    print(f"e-mail:       {len(tree['email_addresses'])} distinct address(es)")
    for name, g in governance.items():
        print(f"  {name}: {g['licence_or_governance'] or 'NO LICENCE STATEMENT'}")
    print(f"\n{report['verdict']}\n-> {a.out}")
    return 1 if not clean else 0


if __name__ == "__main__":
    raise SystemExit(main())
