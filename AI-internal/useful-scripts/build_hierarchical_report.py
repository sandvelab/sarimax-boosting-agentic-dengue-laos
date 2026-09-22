#!/usr/bin/env python3
"""Generate the hierarchical analysis report from the claim tree (Rule 8).

Reported results are heavy summaries; validating and understanding them needs the
detail underneath. This walks `analysis/`, producing linked static HTML in which
each node's claim, answers, results and provenance are one click from its parent,
all the way down to the raw files.

**Two halves, and the second is what makes it hierarchical rather than a file
index.** The tree supplies the upper levels — root to node to fork to child. Below
that sits the within-result detail: for every combination that was scored, the
national mean each model was reported at, then that mean broken out by province,
then each province broken out into the evaluated months, down to the per-cell CRPS
that everything above it is an average of. Four levels, each one click from the
one above, so a reported number can be descended to the values it is made of.

Static HTML on purpose: it costs nothing to keep, needs no server, and will still
open in twenty years. It is generated from the tree, so its structure follows the
analysis rather than being maintained separately — never hand-edit the output.

Two consumers. The agent, which reads stored detail instead of recomputing it or
inserting temporary debug output into working code. And the human, for whom
descending a structure by clicking is far faster than asking for it in a dialogue.

Dual interface:
    API:  build_report(root=".", out="AI-generated/hierarchical-report") -> Path
    CLI:  python build_hierarchical_report.py [--root .] [--out DIR] [--open]
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import claims as claim_collection  # noqa: E402  — the sibling module, for Rule 9's side

CSS = """
:root { --fg:#1a1a1a; --muted:#666; --line:#ddd; --accent:#0b5; --warn:#b40; --bg:#fff; }
@media (prefers-color-scheme: dark) {
  :root { --fg:#e8e8e8; --muted:#999; --line:#333; --accent:#4d8; --warn:#f86; --bg:#161616; }
}
body { font: 15px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
       max-width: 52rem; margin: 2rem auto; padding: 0 1.2rem; color: var(--fg);
       background: var(--bg); }
h1 { font-size: 1.4rem; margin-bottom: .2rem; }
h2 { font-size: 1.05rem; margin-top: 1.8rem; border-bottom: 1px solid var(--line);
     padding-bottom: .3rem; }
h3 { font-size: .95rem; margin-top: 1.3rem; }
.claim { font-size: 1.05rem; margin: .6rem 0 1rem; }
.crumb, .meta { color: var(--muted); font-size: .85rem; }
.tag { display:inline-block; font-size:.72rem; padding:.1rem .45rem; border-radius:3px;
       border:1px solid var(--line); color:var(--muted); margin-left:.4rem; }
.main-path { border-color: var(--accent); color: var(--accent); }
.not-taken { border-color: var(--warn); color: var(--warn); }
ul { padding-left: 1.1rem; } li { margin: .25rem 0; }
a { color: inherit; } a:hover { color: var(--accent); }
pre { background: rgba(128,128,128,.1); padding: .7rem; overflow-x: auto; font-size: .82rem; }
.scroll { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; font-size: .88rem; }
td, th { border-bottom: 1px solid var(--line); padding: .3rem .5rem; text-align: left;
         white-space: nowrap; }
td.n, th.n { text-align: right; font-variant-numeric: tabular-nums; }
tr.ours td { font-weight: 600; }
details { margin: .4rem 0; }
summary { cursor: pointer; color: var(--muted); font-size: .9rem; }
.claimblock { border-left: 2px solid var(--line); padding-left: .8rem; margin: .8rem 0; }
.claimblock .cid { font-weight: 600; }
"""

# The three levels below the tree, and the file each is read from. Nothing here
# recomputes an aggregate: every level is displayed from the file the analysis
# wrote, so the report cannot disagree with the analysis about a number.
# This project stores one per-cell score file per scored result; the drill-down is
# discovered from those rather than from a fixed set of node paths.
PER_CELL = "per_cell_scores.csv"


# --------------------------------------------------------------------------- tree


def _field(text: str, key: str) -> str | None:
    m = re.search(rf"^{re.escape(key)}:\s*(.*)$", text, re.M)
    if not m:
        return None
    v = m.group(1).strip()
    return None if v in ("", "-", "none", "n/a") else v


def _section(text: str, heading: str) -> str:
    m = re.search(rf"^## {re.escape(heading)}\s*$", text, re.M)
    if not m:
        return ""
    nxt = re.compile(r"^## ", re.M).search(text, m.end())
    return text[m.end():nxt.start() if nxt else len(text)].strip()


def _read(node: Path) -> dict:
    text = (node / "claim.md").read_text()
    body = text.split("## Children")[0]
    claim = "\n".join(l for l in body.splitlines()
                      if l.strip() and not l.startswith("#")).strip()
    return {
        "path": node,
        "claim": claim,
        "kind": _field(text, "kind"),
        "main_path": _field(text, "main-path"),
        "answers": _section(text, "Answers"),
        "children": sorted(p for p in node.iterdir()
                           if p.is_dir() and (p / "claim.md").exists()),
    }


# Paths git ignores, collapsed to their topmost ignored directory. Filled once per
# build. A model's contract directory acquires a `uv`-built virtual environment and a
# `__pycache__` the first time chap-core runs it, and a node's `results/` acquires
# chap-core's per-split `work/` — none of which is the node's own material. Listing
# them made one node's "Scripts" section 6 117 files of somebody else's wheels, which
# is not a report of the analysis. What the repository declines to version is exactly
# what this declines to show, so the two cannot drift apart.
_IGNORED: set[str] = set()


def _load_ignored(root: Path) -> set[str]:
    try:
        r = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--others", "--ignored",
             "--exclude-standard", "--directory"],
            capture_output=True, text=True)
    except FileNotFoundError:
        return set()
    return {line.rstrip("/") for line in r.stdout.splitlines() if line.strip()}


def _is_ignored(p: Path, root: Path) -> bool:
    if not _IGNORED:
        return False
    rel = p.relative_to(root)
    for i in range(len(rel.parts)):
        if "/".join(rel.parts[:i + 1]) in _IGNORED:
            return True
    return False


def _files(d: Path, root: Path | None = None) -> list[Path]:
    if not d.is_dir():
        return []
    out = [p for p in d.rglob("*") if p.is_file() and p.name != ".gitkeep"]
    if root is not None:
        out = [p for p in out if not _is_ignored(p, root)]
    return sorted(out)


def _read_csv(p: Path) -> list[dict]:
    if not p.is_file():
        return []
    with p.open(newline="") as fh:
        return list(csv.DictReader(fh))


def _f(v: str | float | None) -> float:
    """Sort key for a stored number that may be blank.

    A province Chap keeps but which contributes no evaluable cell has an empty mean
    rather than a zero, and an empty mean must sort last rather than crash the report
    or be silently read as nothing.
    """
    try:
        return float(v)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return float("inf")


def _num(v: str | float | None, places: int = 3) -> str:
    """Format a stored value for display without changing what it is."""
    if v in (None, "", "nan"):
        return "—"
    try:
        f = float(v)
    except (TypeError, ValueError):
        return str(v)
    return f"{f:,.{places}f}"


# ------------------------------------------------------------------- the detail


def _scored_results(root: Path) -> dict[str, Path]:
    """Every directory holding a per-cell score file, labelled by where it sits in the tree.

    Discovered from what is on disk rather than from a manifest, because the report's job is
    to show what the analysis produced. A node's own `results/` is labelled by the node; a
    combination directory inside one is labelled `<node>/<combination>`.
    """
    out: dict[str, Path] = {}
    for f in sorted((root / "analysis").rglob(PER_CELL)):
        parts = f.parent.relative_to(root / "analysis").parts
        label = ("/".join(parts[:-1]) if parts[-1] == "results"
                 else "/".join(parts[:-2] + (parts[-1],)))
        out[label or "analysis"] = f.parent
    lead = [k for k in ("02_stage1", "04_stage2/h_levelOnlyBoosting",
                        "06_stability/main@h__holdout", "06_stability/baseline=climatology__holdout",
                        "06_stability/baseline=persistence__holdout",
                        "03_baselines/01_persistence", "03_baselines/02_climatology") if k in out]
    return {k: out[k] for k in lead + [k for k in out if k not in lead]}


def _stored_conclusion(d: Path) -> tuple[dict | None, str | None]:
    """The conclusion file beside a per-cell file, whichever of the two names it uses."""
    for name in ("comparison.json", "conclusion.json"):
        if (d / name).is_file():
            return json.loads((d / name).read_text()), name
    return None, None


def _location_names(root: Path) -> dict[str, str]:
    rows = _read_csv(root / "analysis/01_data/02_characterise/results/province_summary.csv")
    return {r["location"]: r.get("location_name", "") for r in rows if r.get("location")}


def _table(headers: list[tuple[str, bool]], rows: list[list[str]],
           ours: set[int] | None = None) -> list[str]:
    """A table; `headers` pairs a label with whether the column is numeric."""
    out = ['<div class=scroll><table><tr>']
    out += [f'<th class="{"n" if n else ""}">{html.escape(h)}</th>' for h, n in headers]
    out.append("</tr>")
    for i, r in enumerate(rows):
        cls = ' class=ours' if ours and i in ours else ""
        out.append(f"<tr{cls}>")
        out += [f'<td class="{"n" if n else ""}">{c}</td>'
                for c, (_, n) in zip(r, headers)]
        out.append("</tr>")
    out.append("</table></div>")
    return out


def _flatten(concl: dict) -> list[list[str]]:
    """The conclusion file's own numbers, one row each. Scalars and one level of nesting;
    long lists and configuration blocks are left to the file itself."""
    rows: list[list[str]] = []
    for k, v in concl.items():
        if k in ("config", "province_set", "evaluated_months", "by_split", "by_horizon",
                 "n_training_rows_by_split", "verification_vs_main_path"):
            continue
        if isinstance(v, dict):
            for k2, v2 in v.items():
                if isinstance(v2, (int, float, str, bool)) or v2 is None:
                    rows.append([html.escape(f"{k}.{k2}"), _num(v2) if isinstance(v2, float)
                                 else html.escape(str(v2))])
        elif isinstance(v, (int, float, str, bool)) or v is None:
            rows.append([html.escape(k), _num(v) if isinstance(v, float) else html.escape(str(v))])
    return rows


def _conclusion_block(concl: dict, fname: str, to_files: str, d_rel: str) -> list[str]:
    parts = ["<h2>The conclusion, as the file states it</h2>",
             f'<p class=meta>Every value below is displayed from '
             f'<a href="{html.escape(to_files + d_rel + "/" + fname)}"><code>{html.escape(fname)}</code></a>; '
             f'nothing on this line of the page is recomputed.</p>']
    parts += _table([("", False), ("value", True)], _flatten(concl))
    for key, label, cols in (("by_split", "By split", "split"), ("by_horizon", "By horizon", "horizon")):
        block = concl.get(key)
        if not isinstance(block, dict) or not block:
            continue
        inner = next(iter(block.values()))
        if isinstance(inner, dict):
            heads = [(cols, False)] + [(k, True) for k in inner]
            rows = [[html.escape(k)] + [_num(v.get(h[0])) for h in heads[1:]] for k, v in block.items()]
        else:
            heads, rows = [(cols, False), ("mean CRPS", True)], [[html.escape(k), _num(v)] for k, v in block.items()]
        parts.append(f"<h3>{label}</h3>")
        parts.append(f'<p class=meta>Stored in <code>{html.escape(fname)}</code>.</p>')
        parts += _table(heads, rows)
    return parts


def _group(cells: list[dict], key: str, names: dict[str, str]) -> list[list[str]]:
    """Group the per-cell file by one column. A grouping of the values shown below it on the
    same page, not a separately stored result -- the page says so."""
    acc: dict[str, dict] = {}
    for r in cells:
        if r.get("crps") in ("", None):
            continue
        e = acc.setdefault(r[key], {"n": 0, "crps": 0.0, "crps1": 0.0, "has1": False, "actual": 0.0})
        e["n"] += 1
        e["crps"] += _f(r["crps"])
        e["actual"] += _f(r.get("actual"))
        if r.get("crps_stage1") not in ("", None):
            e["crps1"] += _f(r["crps_stage1"])
            e["has1"] = True
    rows = []
    for k in sorted(acc, key=lambda x: -acc[x]["crps"]):
        e = acc[k]
        label = f"{k} {names[k]}" if key == "province" and names.get(k) else k
        row = [html.escape(label), str(e["n"]), _num(e["actual"] / e["n"]), _num(e["crps"] / e["n"])]
        row += [_num(e["crps1"] / e["n"]), _num((e["crps"] - e["crps1"]) / e["n"])] if e["has1"] else ["", ""]
        rows.append(row)
    return rows


def _detail_pages(root: Path, out: Path) -> dict[str, str]:
    """One page per scored result: the stored conclusion, then the same values grouped by
    province and by month, then a link to the per-cell file every number above averages.

    Returns label -> page path relative to the report root.
    """
    names = _location_names(root)
    written: dict[str, str] = {}
    for label, d in _scored_results(root).items():
        slug = label.replace("/", "__")
        page = out / "detail" / f"{slug}.html"
        page.parent.mkdir(parents=True, exist_ok=True)
        to_report_root, to_files = "../", "../../"
        d_rel = d.relative_to(root).as_posix()
        cells = _read_csv(d / PER_CELL)
        scored = [r for r in cells if r.get("crps") not in ("", None)]
        concl, fname = _stored_conclusion(d)

        parts = ["<!doctype html><meta charset=utf-8>",
                 f"<title>{html.escape(label)}</title><style>{CSS}</style>",
                 f'<div class=crumb><a href="{to_report_root}index.html">Analysis report</a>'
                 f' / <a href="{to_report_root}analysis/index.html">analysis</a>'
                 f' / detail / {html.escape(label)}</div>',
                 f"<h1>{html.escape(label)}</h1>",
                 f'<p class=meta>{len(scored)} scored cell(s) of {len(cells)}. '
                 f'Source directory: <a href="{html.escape(to_files + d_rel)}">'
                 f'<code>{html.escape(d_rel)}</code></a>.</p>']
        if concl and fname:
            parts += _conclusion_block(concl, fname, to_files, d_rel)
        else:
            parts.append('<p class=meta>No conclusion file beside this per-cell file.</p>')

        heads = [("", False), ("cells", True), ("mean actual", True), ("mean CRPS", True),
                 ("mean CRPS, stage 1", True), ("difference", True)]
        for key, title in (("province", "By province"), ("month", "By month")):
            if not scored or key not in scored[0]:
                continue
            parts.append(f"<h2>{title}</h2>")
            parts.append('<p class=meta>A grouping of the per-cell values linked below, shown so '
                         'the mean above can be taken apart. It is not a separately stored '
                         'result; the file underneath it is.</p>')
            parts += _table(heads, _group(scored, key, names))

        parts.append("<h2>The values</h2>")
        parts.append(f'<p class=meta>Every number on this page is an average of these.</p>'
                     f'<ul><li><a href="{html.escape(to_files + d_rel + "/" + PER_CELL)}">'
                     f'<code>{html.escape(PER_CELL)}</code></a> — one row per evaluated cell'
                     f'</li></ul>')
        page.write_text("\n".join(parts), encoding="utf-8")
        written[label] = f"detail/{slug}.html"
    return written


def _claims_for(node_rel: str, all_claims: list[dict]) -> list[dict]:
    return [c for c in all_claims if c.get("node") == node_rel]


def _results_section(node: Path, root: Path, to_repo_root: str) -> list[str]:
    """A node's results, grouped by the combination that produced them.

    A flat listing was readable when there was one combination and is not when there
    are sixty-five: the reported analysis would be one row among sixty-four
    perturbations of it. `main` and its holdout twin are shown open; the rest fold.
    """
    rdir = node / "results"
    if not rdir.is_dir():
        return []
    loose = sorted(p for p in rdir.iterdir() if p.is_file() and p.name != ".gitkeep")
    combos = sorted(p for p in rdir.iterdir() if p.is_dir())
    if not loose and not combos:
        return []

    def listing(files: list[Path], base: Path) -> list[str]:
        out = ["<ul>"]
        for f in files:
            href = to_repo_root + f.relative_to(root).as_posix()
            out.append(f'<li><a href="{html.escape(href)}">'
                       f'{html.escape(f.relative_to(base).as_posix())}</a>'
                       f' <span class=meta>({f.stat().st_size:,} B)</span></li>')
        out.append("</ul>")
        return out

    parts = ["<h2>Results</h2>"]
    if loose:
        parts += listing(loose, rdir)
    lead = [c for c in combos if c.name in ("main", "main__holdout")]
    rest = [c for c in combos if c not in lead]
    for c in lead:
        parts.append(f"<h3>{html.escape(c.name)}</h3>")
        parts += listing(_files(c, root), c)
    if rest:
        parts.append(f"<details><summary>{len(rest)} other combination(s)</summary>")
        for c in rest:
            parts.append(f"<h3>{html.escape(c.name)}</h3>")
            parts += listing(_files(c, root), c)
        parts.append("</details>")
    return parts


def _page(root: Path, node: Path, out: Path, ancestors: list[str],
          all_claims: list[dict], detail: dict[str, str]) -> str:
    """Write one node's page. `ancestors` are the node names from the tree root down."""
    info = _read(node)
    rel = node.relative_to(root)
    page_dir = out / rel
    page_dir.mkdir(parents=True, exist_ok=True)
    page = page_dir / "index.html"
    depth = len(rel.parts)
    # Pages live at <root>/AI-generated/hierarchical-report/<rel>/index.html, so
    # reaching a file at <root>/<path> means climbing out of <rel>, then out of
    # hierarchical-report and AI-generated.
    to_repo_root = "../" * (depth + 2)
    to_report_root = "../" * depth

    parts = ["<!doctype html><meta charset=utf-8>",
             f"<title>{html.escape(node.name)}</title><style>{CSS}</style>"]

    if ancestors:
        trail = " / ".join(
            f'<a href="{"../" * (len(ancestors) - i)}index.html">{html.escape(n)}</a>'
            for i, n in enumerate(ancestors)
        )
        parts.append(f'<div class=crumb>{trail} / {html.escape(node.name)}</div>')
    parts.append(f"<h1>{html.escape(node.name)}</h1>")
    parts.append(f'<div class=claim>{html.escape(info["claim"])}</div>')

    if info["answers"] and not info["answers"].startswith("_("):
        parts.append("<h2>Answers</h2>")
        parts.append(f"<p>{html.escape(info['answers'])}</p>")

    mine = _claims_for(rel.as_posix(), all_claims)
    if mine:
        parts.append("<h2>Claims resting on this node</h2>")
        parts.append('<p class=meta>From the claim collection. Nothing enters the manuscript '
                     'that is not there.</p>')
        for c in mine:
            parts.append('<div class=claimblock>')
            parts.append(f'<span class=cid>{html.escape(c["id"])}</span> '
                         f'{html.escape(c["statement"])}')
            grounds = []
            for t in c.get("grounds", "").split("·"):
                t = t.strip().strip("`")
                if not t:
                    continue
                grounds.append(f'<a href="{html.escape(to_repo_root + t)}">'
                               f'{html.escape(Path(t).name)}</a>')
            if grounds:
                parts.append(f'<br><span class=meta>grounds: {" · ".join(grounds)}'
                             f' &nbsp;·&nbsp; {html.escape(c.get("by", "-"))}</span>')
            parts.append("</div>")

    if info["children"]:
        kind = info["kind"] or "?"
        parts.append(f"<h2>Children <span class=tag>{html.escape(kind)}</span></h2>")
        if kind == "alternatives":
            parts.append("<p class=meta>Only the main path is run by this node. "
                         "The others are run by the stability node.</p>")
        parts.append("<ul>")
        for c in info["children"]:
            ci = _read(c)
            tag = ""
            if kind == "alternatives":
                tag = (' <span class="tag main-path">main path</span>'
                       if c.name == info["main_path"]
                       else ' <span class="tag not-taken">not taken</span>')
            first = ci["claim"].splitlines()[0] if ci["claim"] else ""
            parts.append(f'<li><a href="{html.escape(c.name)}/index.html">'
                         f'{html.escape(c.name)}</a>{tag}<br>'
                         f'<span class=meta>{html.escape(first)}</span></li>')
        parts.append("</ul>")

    # Every node that produced scored cells hangs its own drill-down, and the root hangs
    # all of them: a summary has to link down to the values it aggregates (Rule 8), and the
    # node that owns those values is where a reader looks first.
    here = rel.as_posix().removeprefix("analysis/").removeprefix("analysis")
    mine = {k: v for k, v in detail.items()
            if rel.as_posix() == "analysis" or k == here or k.startswith(here + "/")}
    if mine:
        parts.append("<h2>Down to the values</h2>")
        parts.append('<p class=meta>The stored conclusion, then that mean grouped by province '
                     'and by month, then the per-cell scores everything above averages — one '
                     'page per scored result.</p><ul>')
        for combo, href in mine.items():
            parts.append(f'<li><a href="{html.escape(to_report_root + href)}">'
                         f'{html.escape(combo)}</a></li>')
        parts.append("</ul>")

    parts += _results_section(node, root, to_repo_root)

    for label, sub in (("Scripts", "scripts"), ("Provenance", "provenance")):
        files = _files(node / sub, root)
        if not files:
            continue
        parts.append(f"<h2>{label}</h2><ul>")
        for f in files:
            href = to_repo_root + f.relative_to(root).as_posix()
            size = f.stat().st_size
            parts.append(f'<li><a href="{html.escape(href)}">'
                         f'{html.escape(f.relative_to(node / sub).as_posix())}</a>'
                         f' <span class=meta>({size:,} B)</span></li>')
        parts.append("</ul>")

    run = node / "run.sh"
    if run.exists():
        parts.append("<h2>run.sh</h2>")
        parts.append(f"<pre>{html.escape(run.read_text())}</pre>")

    page.write_text("\n".join(parts))
    for c in info["children"]:
        _page(root, c, out, ancestors + [node.name], all_claims, detail)
    return str(page)


def build_report(root: str | Path = ".", out: str | Path = "AI-generated/hierarchical-report") -> Path:
    root = Path(root).resolve()
    analysis = root / "analysis"
    if not (analysis / "claim.md").exists():
        raise SystemExit(f"no claim tree at {analysis}")
    out = root / out
    out.mkdir(parents=True, exist_ok=True)

    _IGNORED.clear()
    _IGNORED.update(_load_ignored(root))

    all_claims = claim_collection.load(root)
    detail = _detail_pages(root, out)
    _page(root, analysis, out, [], all_claims, detail)

    try:
        commit = subprocess.run(["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
                                capture_output=True, text=True).stdout.strip() or "not committed"
    except FileNotFoundError:
        commit = "git unavailable"

    concl_path = root / "analysis" / "results" / "main" / "conclusion.json"
    headline = ""
    if concl_path.is_file():
        c = json.loads(concl_path.read_text())
        h = root / "analysis" / "results" / "main__holdout" / "conclusion.json"
        ho = json.loads(h.read_text()) if h.is_file() else None
        headline = (
            f"<h2>The reported conclusion</h2>"
            f"<p class=claim><strong>{html.escape(str(c.get('our_model')))}</strong>, skill "
            f"score {_num(c.get('skill_score'), 4)} against the reference model on the "
            f"development backtest"
            + (f", {_num(ho.get('skill_score'), 4)} on the held-out year" if ho else "")
            + f". Mean CRPS {_num(c.get('crps_ours'))} against "
              f"{_num(c.get('crps_reference'))}"
            + (f", and {_num(ho.get('crps_ours'))} against {_num(ho.get('crps_reference'))} "
               f"on the holdout" if ho else "") + ".</p>"
            f'<p class=meta>It is one member of a distribution over the whole perturbation '
            f'set — see <a href="analysis/05_stability/index.html">05_stability</a>, and '
            f'<a href="detail/main/index.html">descend this number</a> to the values.</p>')

    # The folder README is generated with the report for the same reason the report is:
    # a hand-kept description of a generated folder goes stale silently. `provenance.md`
    # beside it is not generated — it is the append-only record of each build, and it is
    # the one file here that is written by hand.
    (out / "README.md").write_text(
        "# hierarchical-report\n\n"
        "The linked drill-down over the claim tree (Rule 8). **Generated — never hand-edit.**\n"
        "Rebuild with `/hierarchical-report`, which runs\n"
        "`AI-internal/useful-scripts/build_hierarchical_report.py`.\n\n"
        f"Built {date.today().isoformat()} at commit {commit}. Open `index.html`.\n\n"
        "- `index.html` — the reported conclusion, the way into the tree, and every scored\n"
        "  combination.\n"
        "- `analysis/**/index.html` — one page per node: its claim, answers, the claims from\n"
        "  the collection that rest on it, its children with alternatives marked main-path or\n"
        "  not taken, its results grouped by combination, its scripts, its provenance records\n"
        "  and its `run.sh`.\n"
        f"- `detail/<combination>/` — the within-result levels: national mean, then province,\n"
        f"  then month, then the per-cell scores every mean above is an average of. "
        f"{len(detail)} combination(s), {len(detail) and sum(1 for _ in (out / 'detail').rglob('*.html'))} pages.\n\n"
        "Every number shown is displayed from the file the analysis wrote; nothing here\n"
        "recomputes an aggregate, so the report cannot disagree with the analysis. Paths the\n"
        "repository does not version — built virtual environments, `__pycache__`, chap-core's\n"
        "per-split `work/` — are not listed, because they are not the analysis's material.\n\n"
        "`provenance.md` is the exception to the no-hand-editing rule here: it is the record\n"
        "of each build, appended to and never overwritten.\n")

    index = out / "index.html"
    index.write_text(
        f"<!doctype html><meta charset=utf-8><title>Analysis report</title>"
        f"<style>{CSS}</style>"
        f"<h1>Analysis report</h1>"
        f"<p class=meta>Generated {date.today().isoformat()} at commit {html.escape(commit)}. "
        f"Regenerate with <code>/hierarchical-report</code>; never hand-edit.</p>"
        f"{headline}"
        f"<h2>The tree</h2>"
        f'<p><a href="analysis/index.html">Enter the claim tree &rarr;</a> — every node&rsquo;s '
        f'claim, answers, results, scripts, provenance and <code>run.sh</code>, with the claims '
        f'that rest on it and the alternatives marked main-path or not taken.</p>'
        f"<h2>Down to the values</h2>"
        f'<p class=meta>{len(detail)} combination(s) scored. Each is national mean &rarr; '
        f'province &rarr; month &rarr; per-cell score.</p><ul>'
        + "".join(f'<li><a href="{html.escape(href)}">{html.escape(combo)}</a></li>'
                  for combo, href in detail.items())
        + "</ul>"
    )
    return index


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="AI-generated/hierarchical-report")
    ap.add_argument("--open", action="store_true", help="open the report when done")
    a = ap.parse_args(argv)
    index = build_report(a.root, a.out)
    print(f"wrote {index}")
    if a.open:
        subprocess.run(["open", str(index)], check=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
