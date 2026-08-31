"""Open the seal: assemble the file phase E evaluates on, from the two parts beside it.

Plan §3 cuts 2010 out of the data before any work begins and opens it **once**, for the
final validation. This script is that opening, and it is here rather than in `02_setup`
because this node is the only one licensed to read the whole record -- a licence phase E
does not repeal, it exercises.

**What it produces is not a new reading of the data.** It is the concatenation of the two
files the sibling script wrote, in the archived source's own line order, verified to be
byte-identical to that source. Nothing is recomputed and no case value of 2010 is read,
summarised, plotted or characterised here any more than it was in development: the file
is assembled from lines and checked by hash. What looks at 2010 is `chap eval`, running
the models the frozen manifest names, in the batch that opens it.

**Why a third file rather than pointing `02_setup` at the archive.** Two reasons, and
neither is tidiness. The archived source is `(IS_SHADOW)` material with a checksum
manifest, and a setup stage reaching into `Archive/` would put the read outside the tree
where nothing records it. And the property this node exists to establish -- that
development and holdout partition the source exactly -- is what makes the concatenation
legitimate; assembling the file here is where that proof is in scope.

The development file is unchanged and nothing that reads it is touched. Which of the two
a combination reads is decided by `analysis/scripts/lib/combos.py`, from the `__holdout`
suffix the frozen manifest names its rows with.

Seeds: none. The assembly is a deterministic re-ordering of lines already on disk, so the
project seed 20260822 has no surface here.

Writes, under results/:
  phase_e_1998-01_2010-12.csv   the file phase E's setup chain starts from
  phase_e_opening.json          what was assembled, from what, and what was verified

Usage:  "$PYTHON" scripts/open_holdout.py
"""
from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

NODE = Path(__file__).resolve().parent.parent
ROOT = NODE.parents[2]
SOURCE = ROOT / "Archive" / "lao-dataset" / "chap_LAO_admin1_monthly.csv"
RESULTS = NODE / "results"
DEV = RESULTS / "development_1998-01_2009-12.csv"
HOLDOUT = RESULTS / "holdout_2010_SEALED.csv"
OUT = RESULTS / "phase_e_1998-01_2010-12.csv"

DEV_LAST = "2009-12"
PHASE_E_FIRST, PHASE_E_LAST = "1998-01", "2010-12"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_table(path: Path) -> tuple[str, list[str]]:
    """The file as its header line and its data lines, keeping the line endings.

    Text, not a parse. The partition was made on lines for the reason batch 3 gave -- a
    round trip through a parser re-formats an integer column that also holds blanks --
    and putting the parts back together has to be the inverse of that or the file phase E
    reads would differ from the archive by a rounding rule.
    """
    raw = path.read_text().splitlines(keepends=True)
    return raw[0], [line for line in raw[1:] if line.strip()]


def main() -> int:
    header, source_lines = read_table(SOURCE)
    dev_header, dev_lines = read_table(DEV)
    hold_header, hold_lines = read_table(HOLDOUT)

    # Assembled from the parts, ordered by the source. The source is ordered by province
    # and then by month, so the holdout is not a suffix of it: taking the order from the
    # source rather than concatenating the parts is what makes the result the archive
    # again rather than a re-sorted copy of it.
    available = {}
    for line in dev_lines:
        available.setdefault(line, []).append("development")
    for line in hold_lines:
        available.setdefault(line, []).append("holdout")

    assembled, provenance_of_line = [], []
    for line in source_lines:
        parts = available.get(line)
        if not parts:
            raise SystemExit(
                "a line of the archived source is in neither part; the partition this "
                "node verified no longer describes the files on disk")
        assembled.append(line)
        provenance_of_line.append(parts[0])

    OUT.write_text(header + "".join(assembled))

    written_header, written_lines = read_table(OUT)
    check = {
        "source_lines_data": len(source_lines),
        "development_lines": len(dev_lines),
        "holdout_lines": len(hold_lines),
        "assembled_lines": len(written_lines),
        "parts_sum_to_assembled": len(dev_lines) + len(hold_lines) == len(written_lines),
        "header_preserved": written_header == header == dev_header == hold_header,
        "byte_identical_to_archived_source": sha256(OUT) == sha256(SOURCE),
        "lines_from_development": provenance_of_line.count("development"),
        "lines_from_holdout": provenance_of_line.count("holdout"),
        "period_range": [min(l.split(",", 1)[0] for l in written_lines),
                         max(l.split(",", 1)[0] for l in written_lines)],
        "span_declared": [PHASE_E_FIRST, PHASE_E_LAST],
        "development_last_period": DEV_LAST,
    }
    check["spans_match_declaration"] = (
        check["period_range"] == [PHASE_E_FIRST, PHASE_E_LAST])
    check["assembly_is_exact"] = all(check[k] for k in (
        "parts_sum_to_assembled", "header_preserved",
        "byte_identical_to_archived_source", "spans_match_declaration"))

    (RESULTS / "phase_e_opening.json").write_text(json.dumps({
        "what_this_is": (
            "The file phase E evaluates on: the development period and the held-out "
            "year, back together, in the archived source's own order."),
        "written_on": date.today().isoformat(),
        "batch": 16,
        "why_now": (
            "Plan §3: the holdout is opened once, for the final validation, on the "
            "perturbation set frozen in batch 15 "
            "(analysis/05_stability/results/manifest_holdout.csv)."),
        "inputs": {
            str(DEV.relative_to(ROOT)): sha256(DEV),
            str(HOLDOUT.relative_to(ROOT)): sha256(HOLDOUT),
            str(SOURCE.relative_to(ROOT)): sha256(SOURCE),
        },
        "output": {str(OUT.relative_to(ROOT)): sha256(OUT)},
        "assembly_check": check,
        "read_by": (
            "the setup chain, for combinations whose name ends in `__holdout`; "
            "analysis/scripts/lib/combos.py decides which of the two files a "
            "combination reads and is the only place that decision is made."),
        "not_read_here": (
            "no case value of 2010 is parsed, summarised or plotted by this script. "
            "The assembly is on lines and the verification is on hashes."),
    }, indent=1, sort_keys=True) + "\n")

    (RESULTS / "phase_e_outputs.sha256").write_text(
        "".join(f"{sha256(f)}  {f.name}\n"
                for f in (OUT, RESULTS / "phase_e_opening.json")))

    print(f"phase-E file: {len(written_lines)} rows "
          f"({check['lines_from_development']} development + "
          f"{check['lines_from_holdout']} holdout), "
          f"{check['period_range'][0]}..{check['period_range'][1]}, "
          f"identical to archive: {check['byte_identical_to_archived_source']}")
    return 0 if check["assembly_is_exact"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
