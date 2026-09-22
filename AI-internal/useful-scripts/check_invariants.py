#!/usr/bin/env python3
"""Check the structural invariants the ten rules imply.

This is the part of the setup that does not depend on anyone remembering. An
instruction in AGENTS.md can be honoured for twenty steps and dropped at the
twenty-first without anything looking wrong; these checks have no attention
budget. Run at the end of every analysis and before every commit.

A failing check is fixed at the cause. Never weaken a check so it passes.

Checks
  tree        every node is well-formed; alternatives nodes have exactly one main
              path, store no scripts of their own, and call only that child;
              sub-analysis parents call every child; children are named for the
              relationship they stand in (numbered siblings, lettered alternatives)
  provenance  every file under a node's results/ has a provenance record, and every
              record names an existing script, commit and environment
  hashes      every file a record gives a sha256 for exists, and the record names that
              file's current digest somewhere -- so a script cannot change without a
              section being appended
  plots       every plot image has its plotted values and its plotting script beside it
  seeds       every script that draws randomness has a recorded seed
  claims      every claim in the collection resolves to an existing result
  combos      every results/<combination>/ directory is one a stability manifest
              names -- the development manifest or the frozen holdout one -- and the
              development manifest names every non-main child in the tree
  freeze      the frozen phase-E set still hashes to what holdout_freeze.json recorded,
              and no holdout result exists at the commit it was frozen at -- so the set
              was fixed before the held-out year was opened, and has not moved since
  git         the working tree is clean, and every commit a provenance record names is
              an ancestor of HEAD -- not merely an object that exists
  crossing    no result file looks like a value transcribed between steps by hand
  pool        a registered pool membership holds one member per model rather than one
              per contract directory, names the members the pool was actually built
              from, and agrees with the copy the family assembler embeds

Dual interface:
    API:  run_checks(root=".", only=None) -> list[Finding]
    CLI:  python check_invariants.py [--root .] [--only tree,plots] [--quiet]
          exits non-zero if anything failed
"""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

PLOT_SUFFIXES = {".png", ".pdf", ".svg", ".jpg", ".jpeg"}
DATA_SUFFIXES = {".tsv", ".csv", ".txt", ".json", ".parquet"}
SCRIPT_SUFFIXES = {".py", ".R", ".r", ".sh", ".jl"}
RANDOM_HINTS = re.compile(
    r"\b(random|rand\(|randn|sample\(|shuffle|permut|np\.random|torch\.rand|"
    r"set\.seed|rng|Random\()", re.I
)
SEED_HINTS = re.compile(r"\b(seed|set_seed|manual_seed|set\.seed|SEED)\b")
# A node's scripts/ may hold a subdirectory of supporting material -- a Chap model
# contract directory, say -- and chap-core builds that model's environment *inside* it.
# The built environment is not a script of this node: it is generated, git ignores it,
# and its contents are third-party source. Walking into it would have this file reporting
# that numpy draws randomness without recording a seed, which is true and useless.
GENERATED = ("__pycache__", "site-packages", "node_modules")


def script_files(directory: Path) -> list[Path]:
    """Every script file a node owns, skipping generated and vendored trees."""
    if not directory.is_dir():
        return []
    return sorted(
        p for p in directory.rglob("*")
        if p.is_file() and p.suffix in SCRIPT_SUFFIXES
        and not any(part.startswith(".") or part in GENERATED
                    for part in p.relative_to(directory).parts)
    )


# This project's stability node is `06_stability` (batch 11): `05` went to the residual
# diagnostics in batch 10, and a sub-analysis's number is its run order, not a fixed slot.
MANIFEST = Path("analysis/06_stability/results/manifest.csv")
# The frozen phase-E set. Its rows are the development rows under holdout names, so a
# `results/` directory produced by the holdout run is planned exactly as a development one
# is -- and a holdout directory whose name is in neither manifest is the same failure.
MANIFEST_HOLDOUT = Path("analysis/06_stability/results/manifest_holdout.csv")
# The external check's four rows, planned and committed before they ran, exactly as the
# other two manifests were. They move no fork -- the reported model runs unchanged and the
# country underneath is what differs -- so they never appear in the fork agreement below;
# what they are here for is the same thing the other two are, which is that the
# combination space stays closed. A third planned source keeps this check something a
# directory has to be named by, rather than something it can be excused from.
MANIFEST_EXTERNAL = Path("analysis/06_external/results/manifest_external.csv")
# Combination directories a node may hold without a manifest naming them. `main` is the
# reported analysis, which is not a perturbation of anything and so has no fork row.
ALWAYS_ALLOWED = {"main"}

SUB_ANALYSIS_NAME = re.compile(r"^\d{2}_[A-Za-z]")
ALTERNATIVE_NAME = re.compile(r"^[a-z]_[A-Za-z]")


@dataclass
class Finding:
    check: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"[{self.check}] {self.path}: {self.message}"


def nodes(root: Path) -> list[Path]:
    return sorted(p.parent for p in (root / "analysis").rglob("claim.md"))


def _field(text: str, key: str) -> str | None:
    m = re.search(rf"^{re.escape(key)}:\s*(.*)$", text, re.M)
    if not m:
        return None
    v = m.group(1).strip()
    return None if v in ("", "-", "none", "n/a") else v


def check_tree(root: Path) -> list[Finding]:
    out: list[Finding] = []
    for node in nodes(root):
        rel = str(node.relative_to(root))
        run = node / "run.sh"
        if not run.exists():
            out.append(Finding("tree", rel, "no run.sh"))
            continue
        run_text = run.read_text()
        claim_text = (node / "claim.md").read_text()
        kids = sorted(p for p in node.iterdir() if p.is_dir() and (p / "claim.md").exists())
        if not kids:
            continue
        kind = _field(claim_text, "kind")
        if kind not in ("alternatives", "sub-analyses"):
            out.append(Finding("tree", rel, f"has children but kind is {kind!r}"))
            continue
        # AGENTS.md §8: a child's name carries the relationship it stands in.
        # Sub-analyses run in order and are numbered; alternatives are unordered and
        # mutually exclusive and are lettered. A number on an alternative asserts a
        # sequence that does not exist.
        wanted = ALTERNATIVE_NAME if kind == "alternatives" else SUB_ANALYSIS_NAME
        for k in kids:
            if not wanted.match(k.name):
                out.append(Finding(
                    "tree", f"{rel}/{k.name}",
                    f"child of a {kind} node should be named "
                    f"{'a_name, b_name (lettered)' if kind == 'alternatives' else 'NN_name (numbered)'}"))
        if kind == "alternatives":
            main = _field(claim_text, "main-path")
            names = [k.name for k in kids]
            if main not in names:
                out.append(Finding("tree", rel, f"main-path {main!r} not among {names}"))
                continue
            called = set(re.findall(r'bash "([^"/]+)/run\.sh"', run_text))
            if called != {main}:
                out.append(Finding(
                    "tree", rel,
                    f"alternatives node must call only the main path {main!r}, calls {sorted(called)}"))
            own = [p for p in (node / "scripts").glob("*") if p.name != ".gitkeep"] \
                if (node / "scripts").is_dir() else []
            if own:
                out.append(Finding(
                    "tree", rel,
                    f"alternatives node is a pure switch but stores {len(own)} script(s)"))
        else:
            called = set(re.findall(r'bash "([^"/]+)/run\.sh"', run_text))
            missing = {k.name for k in kids} - called
            if missing:
                out.append(Finding(
                    "tree", rel, f"sub-analyses node does not call {sorted(missing)}"))
    return out


def combinations(root: Path) -> set[str] | None:
    """Every combination a manifest names, or None before any of them exists.

    Three manifests. Phase D freezes the holdout set before phase E runs it and the
    holdout rows carry their own names; batch 20's external check plans its four rows the
    same way. A directory is planned if any of the three files names it.
    """
    names: set[str] = set()
    found = False
    import csv
    for manifest in (MANIFEST, MANIFEST_HOLDOUT, MANIFEST_EXTERNAL):
        path = root / manifest
        if not path.exists():
            continue
        found = True
        with path.open() as handle:
            names |= {row["combination"] for row in csv.DictReader(handle)
                      if row["combination"]}
    return names if found else None


def _provenance_records(node: Path) -> dict[str, str]:
    prov = node / "provenance"
    if not prov.is_dir():
        return {}
    return {p.name: p.read_text() for p in prov.glob("*.md")}


def check_provenance(root: Path) -> list[Finding]:
    out: list[Finding] = []
    for node in nodes(root):
        rel = str(node.relative_to(root))
        results = node / "results"
        if not results.is_dir():
            continue
        records = _provenance_records(node)
        blob = "\n".join(records.values())
        known = combinations(root)
        for f in sorted(results.rglob("*")):
            if f.is_dir() or f.name == ".gitkeep":
                continue
            name = f.relative_to(results).as_posix()
            # One script produces the same artefact under every combination, from the
            # same inputs, by the same invocation -- the combination is a parameter, and
            # each file records its own in a `combo` field. So a record may name the
            # artefact by its combination-invariant path, `results/$COMBO/eval.nc`, and
            # cover every combination of it. The obligation is unchanged: some record
            # still has to name the artefact. What is not allowed is the placeholder
            # standing in for a combination nobody planned, so it only satisfies files
            # whose combination the manifest names, and `check_combos` is what makes
            # that set closed.
            head, _, tail = name.partition("/")
            aliases = [name]
            if tail and known is not None and head in (known | ALWAYS_ALLOWED):
                aliases += [f"$COMBO/{tail}", f"<combo>/{tail}"]
            if not any(alias in blob for alias in aliases):
                out.append(Finding("provenance", f"{rel}/results/{name}",
                                   "no provenance record names this result"))
        for rec_name, rec in records.items():
            for key in ("script:", "commit:", "environment:"):
                if key not in rec:
                    out.append(Finding("provenance", f"{rel}/provenance/{rec_name}",
                                       f"record is missing '{key}'"))
    return out


# A record's `script:` block names the files that produced the result and gives a sha256
# for each. Until batch 23 nothing made those digests keep up with the files, and the worst
# case was the headline result's own record: `analysis/provenance/conclude.md` named a
# version of `conclude.py` that had not existed since batch 16 changed the script, ran it to
# produce the holdout conclusion, and appended no section.
#
# Twenty records were stale, and nineteen of them have one shape: a batch appended its
# section when it ran the script, changed the script again later in the same batch, and did
# not append again. Nothing looks wrong afterwards, which is why this is code and not a
# resolution to be more careful.
#
# The twentieth is the one that makes this worth doing at the level of files rather than of
# `script:` lines. Four records name `03_models/scripts/lib/chap_eval.py` -- a library, not
# their own script -- with its digest, and it changed twice after they were written. A check
# that read only the first line of the block would have passed all four.
DIGEST = re.compile(r"sha256:([0-9a-f]{8,64})")
# The tokens a `script:` block is made of, matched in one pass so they come out in the order
# they appear and cannot overlap. `dir` is a heading like
# `the model itself, scripts/persistence_model/:`, which the bare filenames under it are
# relative to; `MLproject` is in the path alternative because chap-core's model contract
# requires that name and it has no suffix to recognise it by.
RECORD_TOKEN = re.compile(
    r"(?P<digest>sha256:[0-9a-f]{8,64})"
    r"|(?P<dir>[\w./$-]+/(?=[:\s]|$))"
    r"|(?P<path>[\w./$-]*(?:\.(?:py|sh|R|r|jl|toml|lock|ya?ml|ipynb)|MLproject)\b)")


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _script_blocks(text: str) -> list[str]:
    """Each `script:` field with the continuation lines that belong to it."""
    out, lines = [], text.splitlines()
    for i, line in enumerate(lines):
        if not line.startswith("script:"):
            continue
        block = [line]
        for nxt in lines[i + 1:]:
            if not nxt.strip() or nxt.startswith("```") or re.match(r"^[a-z-]+:", nxt):
                break
            block.append(nxt)
        out.append("\n".join(block))
    return out


def _hashed_files(block: str) -> list[tuple[str, str]]:
    """(directory, path) for each file the block names *and gives a digest for*.

    A path claims the digest that is the next token after it. If the next token is another
    path it carries no digest of its own -- `scripts/run_hier_nb.py   (unchanged)` followed
    by the model files that did change -- and nothing is claimed on its behalf. A record
    naming a library without hashing it is being less precise, not wrong, and is left alone.
    """
    tokens = [(m.lastgroup, m.group()) for m in RECORD_TOKEN.finditer(block)]
    out, directory = [], ""
    for j, (kind, value) in enumerate(tokens):
        if kind == "dir":
            directory = value
        elif kind == "path":
            following = tokens[j + 1] if j + 1 < len(tokens) else None
            if following and following[0] == "digest":
                out.append((directory, value))
    return out


def check_hashes(root: Path) -> list[Finding]:
    """Every file a record hashes exists, and the record names its current digest.

    Somewhere in the record, not in its newest section: an old section records the version
    that ran then and is right to keep it. The obligation is that the record has caught up
    with the file, not that it has forgotten what came before. An abbreviated digest --
    `sha256:cbd3158db12438ac...`, as the model contract files are recorded -- satisfies it
    as a prefix, because abbreviating is a formatting choice and not a weaker claim.

    What this does not check, and it matters because this file is a large part of why the
    records are trusted: that a digest is paired with the run it sits beside, that a library
    a script imports is named at all, or that anything in the record is true. It narrows
    where a human has to look. It does not do the looking.
    """
    out: list[Finding] = []
    for node in nodes(root):
        rel = node.relative_to(root)
        for rec_name, rec in _provenance_records(node).items():
            where = f"{rel}/provenance/{rec_name}"
            recorded = DIGEST.findall(rec)
            seen: set[str] = set()
            for directory, named in (f for b in _script_blocks(rec)
                                     for f in _hashed_files(b)):
                if named in seen:
                    continue
                seen.add(named)
                candidates = [node / named, root / named]
                if directory:
                    candidates += [node / directory / named, root / directory / named]
                path = next((p for p in candidates if p.is_file()), None)
                if path is None:
                    out.append(Finding("hashes", where,
                                       f"gives a sha256 for '{named}', which is not a "
                                       f"file at this node or at the repository root"))
                    continue
                current = sha256_of(path)
                if not any(current.startswith(d) for d in recorded):
                    out.append(Finding("hashes", where, (
                        f"{path.relative_to(root)} now hashes to {current[:12]}…, which "
                        f"this record does not name: the file changed and no section was "
                        f"appended")))
    return out


def check_plots(root: Path) -> list[Finding]:
    out: list[Finding] = []
    for node in nodes(root):
        rel = str(node.relative_to(root))
        results = node / "results"
        if not results.is_dir():
            continue
        for f in sorted(results.rglob("*")):
            if f.suffix.lower() not in PLOT_SUFFIXES:
                continue
            stem = f.with_suffix("")
            has_data = any(stem.with_suffix(s).exists() for s in DATA_SUFFIXES)
            has_script = any(
                (node / "scripts" / f"{stem.name}{s}").exists() for s in SCRIPT_SUFFIXES
            ) or any(stem.with_suffix(s).exists() for s in SCRIPT_SUFFIXES)
            if not has_data:
                out.append(Finding("plots", f"{rel}/results/{f.name}",
                                   "no plotted-values file beside the figure"))
            if not has_script:
                out.append(Finding("plots", f"{rel}/results/{f.name}",
                                   "no plotting script for this figure"))
    return out


def check_seeds(root: Path) -> list[Finding]:
    out: list[Finding] = []
    for node in nodes(root):
        rel = str(node.relative_to(root))
        for s in script_files(node / "scripts"):
            text = s.read_text(errors="replace")
            if RANDOM_HINTS.search(text) and not SEED_HINTS.search(text):
                out.append(Finding(
                    "seeds", f"{rel}/scripts/{s.relative_to(node / 'scripts')}",
                    "draws randomness but records no seed"))
    return out


def check_claims(root: Path) -> list[Finding]:
    out: list[Finding] = []
    coll = root / "Human-AI-collaboration" / "claims" / "claims.md"
    if not coll.exists():
        return out
    # Drop fenced code blocks first: the collection documents its own format with an
    # example, and an example must not be checked as if it were a real claim.
    text = re.sub(r"^```.*?^```", "", coll.read_text(), flags=re.S | re.M)
    for m in re.finditer(r"^\s*[-*]?\s*grounds:\s*(.+)$", text, re.M):
        for target in [t.strip() for t in m.group(1).split("·")]:
            target = target.strip("`[] ")
            if not target or target.startswith("("):
                continue
            if not (root / target).exists():
                out.append(Finding("claims", target, "claim points at a result that does not exist"))
    return out


def check_combos(root: Path) -> list[Finding]:
    """The combination space is closed, and the manifest is not behind the tree.

    Two failures this catches, both of which look like nothing on the surface.

    A `results/` subdirectory nobody planned -- a scratch run, a combination renamed
    halfway, a typo that created a second directory beside the real one -- is a set of
    numbers with no row in the manifest, and therefore an analysis that is in the
    repository and not in anything reported. All three manifests count: this project's
    batch 16 froze the holdout set, whose rows are the same analyses under `__holdout`
    names, the prior project's batch 20 planned an external check's four (no such node
    exists here), and a directory nobody planned is the same failure whichever dataset it
    is on.

    And a fork added to the tree after the manifest was written is a reasonable
    alternative the stability run does not know about. That is the silent absence
    `AGENTS.md` §4 forbids, so the manifest's tier-1 rows must agree exactly with the
    tree's non-main children. `06_stability/scripts/02_plan_manifest.py` keeps them in step; this is what says
    so when it has not been re-run.
    """
    import csv
    out: list[Finding] = []
    path = root / MANIFEST
    if not path.exists():
        return out
    with path.open() as handle:
        rows = list(csv.DictReader(handle))
    known = (combinations(root) or set()) | ALWAYS_ALLOWED

    # A node that holds a manifest is a node whose own outputs are not
    # combination-scoped: they describe every combination in it and belong to none.
    # There are two of them since batch 20 -- `05_stability` and `06_external` -- so the
    # exemption is derived from where the manifests are rather than named.
    planners = {(root / m).parents[1] for m in
                (MANIFEST, MANIFEST_HOLDOUT, MANIFEST_EXTERNAL)}
    for node in nodes(root):
        results = node / "results"
        if not results.is_dir():
            continue
        if node in planners:
            continue
        for child in sorted(p for p in results.iterdir() if p.is_dir()):
            if child.name in known:
                continue
            out.append(Finding(
                "combos", f"{node.relative_to(root)}/results/{child.name}",
                "results for a combination the stability manifest does not name"))

    planned = {(r["fork"], r["child"]) for r in rows if r["tier"] == "1"
               and r["fork"] != "-"}
    actual = set()
    for node in nodes(root):
        text = (node / "claim.md").read_text()
        if _field(text, "kind") != "alternatives":
            continue
        main = _field(text, "main-path")
        for kid in sorted(p.name for p in node.iterdir()
                          if p.is_dir() and (p / "claim.md").exists()):
            if kid != main:
                actual.add((str(node.relative_to(root)), kid))
    for fork, child in sorted(actual - planned):
        out.append(Finding("combos", f"{fork}/{child}",
                           "a path not taken with no row in the stability manifest; "
                           "re-run 06_stability/scripts/02_plan_manifest.py"))
    for fork, child in sorted(planned - actual):
        out.append(Finding("combos", f"{fork}/{child}",
                           "the manifest names a child the tree does not have"))
    return out


def check_freeze(root: Path) -> list[Finding]:
    """The frozen phase-E set is still the set that was frozen, and it predates the opening.

    The plan's §3 makes the whole holdout spread rest on one file: `manifest_holdout.csv`
    fixes what gets evaluated on 2010, before 2010 is opened, so that the spread is a
    measurement rather than a selection. `holdout_freeze.json` beside it records that file's
    sha256 at the moment it was written, and the commit that added it.

    Two things are asserted from that, and both were prose until batch 24.

    **The frozen set has not been rewritten.** `06_stability/scripts/07_plan_holdout_manifest.py`
    refuses to rewrite it, but the refusal lives in the script; this is the statement that
    holds whatever wrote the file. The prior project's batch 18 found its script rebuilding the
    set on every run of `analysis/run.sh` and returning the same bytes only because the tree had
    not changed.

    **The freeze predates the opening.** `holdout_freeze.json`'s own note claims that no
    holdout result exists at the commit it was frozen at. That is the entire evidence that
    the set was fixed in advance, and it is checkable against git rather than believed.

    A holdout result is a tracked path under `analysis/` carrying `__holdout`, which is the
    suffix every frozen row's name ends in. The prior project wrote its combinations to
    `analysis/results/<combination>/` and this check named that path literally; this project's
    stability node writes to `analysis/06_stability/results/<combination>/`, so the literal
    path matched nothing here and the check passed by looking in an empty place. That is worse
    than a check that fails: it reads as evidence and is not. Fixed in batch 16, before the
    freeze it is meant to protect (a methodological change, AGENTS.md §3 Rule 4).

    The other digests `holdout_freeze.json` carries -- `conclusions.csv`,
    `distribution.json`, the development `manifest.csv` -- are deliberately not checked.
    They are context recorded at the freeze, not the frozen artefact: the development half
    may legitimately be re-run, and the reference model is unseeded, so a clean-room run
    moves them without anything being wrong.
    """
    out: list[Finding] = []
    import json

    # The development set is frozen too (`manifest_freeze.json`, batch 11 and batch 14), and
    # until batch 16 nothing asserted that it stayed frozen. It could not: `est_cost_s` is
    # measured wall-clock and `02_plan_manifest.py` rewrote the file on every run of
    # `analysis/run.sh`, so the frozen digest was a record of a file that no longer existed the
    # moment the tree was reproduced. The script now verifies instead of rewriting; this is the
    # statement that holds whatever wrote the file, and it is the same assertion phase E's set
    # gets below.
    dev_freeze = root / MANIFEST.parent / "manifest_freeze.json"
    if dev_freeze.exists() and (root / MANIFEST).exists():
        record = json.loads(dev_freeze.read_text())
        current = hashlib.sha256((root / MANIFEST).read_bytes()).hexdigest()
        if record.get("sha256") and record["sha256"] != current:
            out.append(Finding("freeze", str(MANIFEST), (
                f"the frozen development set hashes to {current[:12]}… and manifest_freeze.json "
                f"records {record['sha256'][:12]}…: it has been rewritten since it was frozen, so "
                f"the stability report is of a set the repository no longer holds")))

    freeze = root / MANIFEST_HOLDOUT.parent / "holdout_freeze.json"
    manifest = root / MANIFEST_HOLDOUT
    if not freeze.exists() or not manifest.exists():
        return out
    record = json.loads(freeze.read_text())
    where = str(MANIFEST_HOLDOUT)

    recorded = record.get("frozen_inputs", {}).get("results/manifest_holdout.csv")
    current = hashlib.sha256(manifest.read_bytes()).hexdigest()
    if recorded and recorded != current:
        out.append(Finding("freeze", where, (
            f"the frozen phase-E set hashes to {current[:12]}… and holdout_freeze.json "
            f"records {recorded[:12]}…: it has been rewritten since it was frozen, and "
            f"the holdout spread is then a set chosen after the year was opened")))

    # The sealed file itself must still be the sealed file. `08_run_holdout.py` refuses to open
    # anything whose digest differs from the one recorded at the freeze, which is the right
    # behaviour and is also why this has to be checked outside that script: until batch 19 a
    # fresh clone received `holdout.csv` with different bytes (git normalised the line endings
    # the writer emitted), so the runner would have refused and phase E was not reproducible
    # from a clone at all. `.gitattributes` fixes the bytes; this says so if it ever stops
    # holding, in the working copy or in a clone.
    for rel, digest_recorded in (record.get("frozen_inputs") or {}).items():
        if not rel.startswith("analysis/01_data/"):
            continue
        f = root / rel
        if not f.exists():
            out.append(Finding("freeze", rel, "the freeze records this input and it is gone"))
        elif hashlib.sha256(f.read_bytes()).hexdigest() != digest_recorded:
            out.append(Finding("freeze", rel, (
                f"hashes to {hashlib.sha256(f.read_bytes()).hexdigest()[:12]}… and the phase-E "
                f"freeze records {digest_recorded[:12]}…: the sealed data has changed since the "
                f"freeze, and 08_run_holdout.py will refuse to open it")))

    import csv
    rows = list(csv.DictReader(manifest.open()))
    if record.get("rows") not in (None, len(rows)):
        out.append(Finding("freeze", where,
                           f"holdout_freeze.json says {record['rows']} rows and the file "
                           f"has {len(rows)}"))

    commit = record.get("frozen_at_commit", "")
    if commit and (root / ".git").is_dir():
        listed = subprocess.run(["git", "-C", str(root), "ls-tree", "-r", "--name-only",
                                 commit], capture_output=True, text=True)
        if listed.returncode != 0:
            out.append(Finding("freeze", where,
                               f"frozen_at_commit {commit} is not readable in this "
                               f"repository, so the freeze cannot be dated"))
        else:
            leaked = [p for p in listed.stdout.splitlines()
                      if p.startswith("analysis/") and "__holdout" in p
                      and p != str(MANIFEST_HOLDOUT)]
            if leaked:
                out.append(Finding("freeze", where, (
                    f"{len(leaked)} holdout result file(s) already exist at {commit}, the "
                    f"commit the set was frozen at (first: {leaked[0]}): the set was not "
                    f"fixed before the year was opened")))

    # The verification the script writes on every run of `analysis/run.sh`. If it is
    # present it must be about the file that is here, and it must not be carrying a
    # difference the frozen set cannot absorb.
    check = root / MANIFEST_HOLDOUT.parent / "holdout_freeze_check.json"
    if check.exists():
        seen = json.loads(check.read_text())
        if seen.get("frozen", {}).get("sha256") not in (None, current):
            out.append(Finding("freeze", str(check.relative_to(root)),
                               "the last verification was of a different file; re-run "
                               "06_stability/scripts/07_plan_holdout_manifest.py"))
        fatal = seen.get("fatal", {})
        for name in ("frozen_rows_the_tree_no_longer_carries",
                     "frozen_rows_whose_structure_moved"):
            if fatal.get(name):
                out.append(Finding("freeze", str(check.relative_to(root)),
                                   f"{len(fatal[name])} frozen row(s) recorded under "
                                   f"{name}"))
    return out


def check_git(root: Path) -> list[Finding]:
    out: list[Finding] = []
    if not (root / ".git").is_dir():
        return [Finding("git", ".", "not a git repository -- Rule 4 cannot be satisfied")]
    try:
        st = subprocess.run(["git", "-C", str(root), "status", "--porcelain"],
                            capture_output=True, text=True, check=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        return [Finding("git", ".", f"could not run git: {e}")]
    if st:
        n = len(st.splitlines())
        out.append(Finding("git", ".", f"working tree not clean ({n} changed path(s))"))
    # Every hash on every `commit:` line, and each one has to be an ancestor of HEAD.
    #
    # Both halves of that are corrections batch 18 made after `/validate outsider` walked
    # the headline result's chain and found the link broken.
    #
    # The pattern used to be anchored -- `^commit:\s*([0-9a-f]{7,40})\s*$` -- so it matched
    # only a line carrying one bare hash and nothing else. `analysis/provenance/conclude.md`
    # reads `commit: 9993d37 (the script), 3fb1280 (the combinations)`, which matched
    # nothing at all, so the provenance record for this project's headline result was the
    # one record the check never looked at. A record that annotates its hashes is being
    # more informative, not less, and was being punished for it.
    #
    # And the test was `cat-file -e`, which asks whether the object is in the store. An
    # object orphaned by a rewritten commit is still in the store of the tree that
    # rewrote it, and is still copied by a *local* `git clone`, which hardlinks the whole
    # object directory -- so it looked fine here and in every clone taken from here. It
    # would not survive a push, and `/release` is next. Ancestry is the property the
    # record actually needs: the commit it names has to be one a reader can check out.
    for node in nodes(root):
        for rec_name, rec in _provenance_records(node).items():
            for line in re.findall(r"^commit:\s*(.+)$", rec, re.M):
                for sha in re.findall(r"\b[0-9a-f]{7,40}\b", line):
                    where = f"{node.relative_to(root)}/provenance/{rec_name}"
                    if subprocess.run(["git", "-C", str(root), "merge-base",
                                       "--is-ancestor", sha, "HEAD"],
                                      capture_output=True).returncode == 0:
                        continue
                    known = subprocess.run(["git", "-C", str(root), "cat-file", "-e",
                                            f"{sha}^{{commit}}"], capture_output=True)
                    out.append(Finding("git", where, (
                        f"recorded commit {sha} is not an ancestor of HEAD"
                        if known.returncode == 0 else
                        f"recorded commit {sha} does not exist")))
    return out


def check_crossing(root: Path) -> list[Finding]:
    """Heuristic for Rule 1's hardest failure: a value carried between steps by hand.

    A literal numeric constant sitting in a script with a comment naming another
    step is the visible symptom. Reported as a warning to look at, not a proof.

    The comment has to be on the constant's own line. A whitespace class matches
    newlines, so the
    first version of this pattern also matched a constant followed by a blank line and
    an unrelated paragraph of prose starting with one of the words below -- which is a
    docstring-style module, not a transcribed value. Batch 8 hit that on a modelling
    constant whose rationale was two lines further down, and the separator was narrowed
    to spaces and tabs. A trailing comment naming another step is still caught; nothing
    that was a finding before stops being one.
    """
    out: list[Finding] = []
    pat = re.compile(r"^[ \t]*[A-Z_]{3,}[ \t]*=[ \t]*-?\d+\.?\d*[ \t]*#.*\b(from|per|see|step|output|above)\b",
                     re.M | re.I)
    for node in nodes(root):
        for s in script_files(node / "scripts"):
            for m in pat.finditer(s.read_text(errors="replace")):
                out.append(Finding("crossing", f"{node.relative_to(root)}/scripts/{s.name}",
                                   f"hard-coded value may have crossed a step by hand: "
                                   f"{m.group(0).strip()[:70]}"))
    return out


def _alternatives_forks_above(root: Path, node: str) -> list[str]:
    """Every alternatives fork between `03_models` and the node at this path."""
    models = root / "analysis" / "03_models"
    out: list[str] = []
    current = root / node
    while current != models and models in current.parents:
        claim = current.parent / "claim.md"
        if claim.exists() and _field(claim.read_text(), "kind") == "alternatives":
            out.append(str(current.parent.relative_to(root)))
        current = current.parent
    return out


def check_pool(root: Path) -> list[Finding]:
    """A registered pool membership is the membership that ran, and it is a set of members.

    Candidate 3's weighting fork registers, before the pool runs, how many members the
    pool will have and which of them are the plan's required baselines. With equal weights
    that statement *is* the model -- the count is the weight -- so a premise describing a
    different pool is a prediction registered about a model that was not run.

    It happened, for ten days and forty combinations. Batch 22 gave the persistence and
    climatology baselines a second published construction each; the weighting child counted
    contract directories while the pool resolved each fork to one child, and the same run
    printed *six members at 1/6* and *four members* three lines apart. Batch 32 gave both
    one rule, and this is the part that does not depend on the two staying imported from
    it.

    Three clauses, in order of how little they need to know:

    1. **no two members under one alternatives fork.** Two constructions of one baseline
       are one member, whichever this combination takes; the family fork is the exception,
       because pooling its children is what the pool is for. This needs only the tree, so
       it holds for a combination that has never been run;
    2. **the premise names the members `prepare_members.py` recorded** for the same
       combination -- `member_selection.json` where there is one, and `members.json` for
       the six pool runs that pre-date that file, so no combination that has run is
       exempt;
    3. **the copy embedded in `candidate_spec.json` is the child's own.** The family
       assembler copies the whole specification into `stages`, so a corrected premise that
       was not re-assembled leaves the contradiction one file further out.
    """
    import json
    out: list[Finding] = []
    models = root / "analysis" / "03_models"
    if not models.exists():
        return out
    family_fork = "analysis/03_models/03_candidate"

    for node in nodes(root):
        if models not in node.parents:
            continue
        for spec_path in sorted(node.glob("results/*/model_option_spec.json")):
            try:
                spec = json.loads(spec_path.read_text())
            except (OSError, json.JSONDecodeError) as exc:
                out.append(Finding("pool", str(spec_path.relative_to(root)),
                                   f"unreadable: {exc}"))
                continue
            registered = (spec.get("premise") or {}).get("members")
            if not registered:
                continue
            combination = spec_path.parent.name
            rel = str(spec_path.relative_to(root))

            # 1 -- one member per model, not one per contract directory.
            by_fork: dict[str, list[str]] = {}
            for member in registered:
                for fork in _alternatives_forks_above(root, member):
                    if fork != family_fork:
                        by_fork.setdefault(fork, []).append(member)
            for fork, together in sorted(by_fork.items()):
                if len(together) > 1:
                    out.append(Finding("pool", rel, (
                        f"registers {len(together)} members under the alternatives fork "
                        f"{fork}: {together}. A fork chooses between constructions of "
                        f"one member; only the child this combination takes is in the "
                        f"pool")))

            # 2 -- against what the pool was actually built from. `member_selection.json`
            # where there is one; `members.json` for the six pool runs that pre-date it,
            # so no combination that has run is exempt from the clause.
            family = node.parents[1]
            recorded = family / "results" / combination / "member_selection.json"
            membership = family / "results" / combination / "members.json"
            ran = None
            if recorded.exists():
                contracts = json.loads(recorded.read_text())["contracts"]
                ran = [c["node"] for c in contracts if c["is_a_member"]]
                source = recorded
            elif membership.exists():
                ran = [m["node"] for m in
                       json.loads(membership.read_text())["members"]]
                source = membership
            if ran is not None and sorted(ran) != sorted(registered):
                out.append(Finding("pool", rel, (
                    f"registers {len(registered)} members and "
                    f"{source.relative_to(root)} records {len(ran)} that ran: "
                    f"registered {registered}, ran {ran}")))

            # 3 -- and against the copy the family assembler carries.
            assembled = family / "results" / combination / "candidate_spec.json"
            if assembled.exists():
                for stage in json.loads(assembled.read_text()).get("stages", []):
                    if stage.get("node") != spec.get("node"):
                        continue
                    embedded = (stage.get("premise") or {}).get("members")
                    if embedded != registered:
                        out.append(Finding("pool", rel, (
                            f"{assembled.relative_to(root)} embeds a different "
                            f"membership for this stage: {embedded} against "
                            f"{registered}. Re-run the family's assembler")))
    return out


CHECKS = {
    "tree": check_tree,
    "provenance": check_provenance,
    "hashes": check_hashes,
    "plots": check_plots,
    "seeds": check_seeds,
    "claims": check_claims,
    "combos": check_combos,
    "freeze": check_freeze,
    "git": check_git,
    "crossing": check_crossing,
    "pool": check_pool,
}


def run_checks(root: str | Path = ".", only: list[str] | None = None) -> list[Finding]:
    root = Path(root).resolve()
    names = only or list(CHECKS)
    findings: list[Finding] = []
    for n in names:
        if n not in CHECKS:
            raise SystemExit(f"unknown check: {n} (have {', '.join(CHECKS)})")
        findings.extend(CHECKS[n](root))
    return findings


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--only", help="comma-separated subset of: " + ", ".join(CHECKS))
    ap.add_argument("--quiet", action="store_true", help="print only failures")
    a = ap.parse_args(argv)

    only = [s.strip() for s in a.only.split(",")] if a.only else None
    findings = run_checks(a.root, only)

    by_check: dict[str, list[Finding]] = {}
    for f in findings:
        by_check.setdefault(f.check, []).append(f)

    for name in (only or list(CHECKS)):
        fs = by_check.get(name, [])
        if fs:
            print(f"FAIL  {name}  ({len(fs)})")
            for f in fs:
                print(f"        {f.path}: {f.message}")
        elif not a.quiet:
            print(f"ok    {name}")

    if findings:
        print(f"\n{len(findings)} invariant failure(s). Fix the cause, not the check.")
        return 1
    if not a.quiet:
        print("\nAll invariants hold.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
