#!/usr/bin/env python3
"""Generate the hierarchical analysis report from the claim tree (Rule 8).

Reported results are heavy summaries; validating and understanding them needs the
detail underneath. This walks `analysis/`, producing linked static HTML in which
each node's claim, answers, results and provenance are one click from its parent,
all the way down to the raw files.

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
import html
import re
import subprocess
from datetime import date
from pathlib import Path

CSS = """
:root { --fg:#1a1a1a; --muted:#666; --line:#ddd; --accent:#0b5; --warn:#b40; --bg:#fff; }
@media (prefers-color-scheme: dark) {
  :root { --fg:#e8e8e8; --muted:#999; --line:#333; --accent:#4d8; --warn:#f86; --bg:#161616; }
}
body { font: 15px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
       max-width: 46rem; margin: 2rem auto; padding: 0 1.2rem; color: var(--fg);
       background: var(--bg); }
h1 { font-size: 1.4rem; margin-bottom: .2rem; }
h2 { font-size: 1.05rem; margin-top: 1.8rem; border-bottom: 1px solid var(--line);
     padding-bottom: .3rem; }
.claim { font-size: 1.05rem; margin: .6rem 0 1rem; }
.crumb, .meta { color: var(--muted); font-size: .85rem; }
.tag { display:inline-block; font-size:.72rem; padding:.1rem .45rem; border-radius:3px;
       border:1px solid var(--line); color:var(--muted); margin-left:.4rem; }
.main-path { border-color: var(--accent); color: var(--accent); }
.not-taken { border-color: var(--warn); color: var(--warn); }
ul { padding-left: 1.1rem; } li { margin: .25rem 0; }
a { color: inherit; } a:hover { color: var(--accent); }
pre { background: rgba(128,128,128,.1); padding: .7rem; overflow-x: auto; font-size: .82rem; }
table { border-collapse: collapse; width: 100%; font-size: .88rem; }
td, th { border-bottom: 1px solid var(--line); padding: .3rem .5rem; text-align: left; }
"""


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


def _files(d: Path) -> list[Path]:
    if not d.is_dir():
        return []
    return sorted(p for p in d.rglob("*") if p.is_file() and p.name != ".gitkeep")


def _page(root: Path, node: Path, out: Path, ancestors: list[str]) -> str:
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

    parts = [f"<!doctype html><meta charset=utf-8>",
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

    for label, sub in (("Results", "results"), ("Scripts", "scripts"),
                       ("Provenance", "provenance")):
        files = _files(node / sub)
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
        _page(root, c, out, ancestors + [node.name])
    return str(page)


def build_report(root: str | Path = ".", out: str | Path = "AI-generated/hierarchical-report") -> Path:
    root = Path(root).resolve()
    analysis = root / "analysis"
    if not (analysis / "claim.md").exists():
        raise SystemExit(f"no claim tree at {analysis}")
    out = root / out
    out.mkdir(parents=True, exist_ok=True)
    _page(root, analysis, out, [])

    try:
        commit = subprocess.run(["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
                                capture_output=True, text=True).stdout.strip() or "not committed"
    except FileNotFoundError:
        commit = "git unavailable"

    index = out / "index.html"
    index.write_text(
        f"<!doctype html><meta charset=utf-8><title>Analysis report</title>"
        f"<style>{CSS}</style>"
        f"<h1>Analysis report</h1>"
        f"<p class=meta>Generated {date.today().isoformat()} at commit {html.escape(commit)}. "
        f"Regenerate with <code>/hierarchical-report</code>; never hand-edit.</p>"
        f'<p><a href="analysis/index.html">Enter the claim tree &rarr;</a></p>'
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
