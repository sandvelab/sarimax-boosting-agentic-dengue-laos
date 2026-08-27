"""The project seed, and the derivation of a component seed from it.

Rule 6 asks for **one** project-level seed, deterministically derived per component and
recorded. Two things follow, and this module exists so that neither is left to care.

**The number lives in one place.** It is a project setting, declared in
`readme-at-start.md` beside the environment and the split point, and this module reads it
from that table rather than carrying a copy. A seed written down in two places is a seed
that can disagree with itself, and the disagreement would be invisible: both runs would
look seeded, and only the numbers would differ. If the table is ever reworded so the seed
cannot be found, this raises rather than falling back to a default -- a silent default is
exactly the failure Rule 6 is about.

**The derivation is a hash, not an offset.** A component seed is the first eight bytes of
`blake2b("<project seed>:<component>")`, reduced into the range NumPy accepts. BLAKE2b is
used rather than Python's `hash`, which is salted per process, so the derivation is stable
across runs and across machines. Derived seeds are therefore reproducible from the project
seed and the component name alone, and both are recorded in the file the component reads.

Not a step: `scripts/lib/` is a subdirectory, so `node.py` does not put it in any node's
`run.sh`. It is imported by the scripts that need a seed.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

SETTINGS = "readme-at-start.md"
SEED_ROW = re.compile(r"^\|\s*Project random seed\s*\|\s*`(\d+)`", re.M)

# NumPy's SeedSequence accepts any non-negative integer, but a 32-bit value is what is
# comfortably printable in a specification file and comparable by eye across records.
SEED_MODULUS = 2**32


def repo_root(start: Path) -> Path:
    for p in [start.resolve(), *start.resolve().parents]:
        if (p / "AGENTS.md").exists():
            return p
    raise SystemExit("no repository root above " + str(start))


def project_seed(root: Path) -> int:
    """The one project seed, read from the settings table that declares it."""
    settings = root / SETTINGS
    match = SEED_ROW.search(settings.read_text())
    if not match:
        raise SystemExit(
            f"no project seed in {SETTINGS}: expected a table row of the form "
            f"`| Project random seed | \\`<digits>\\` |`. The seed is a project setting "
            f"and this module will not invent one.")
    return int(match.group(1))


def component_seed(root: Path, component: str) -> dict:
    """The seed for one component, with everything needed to re-derive it.

    Returns the derivation rather than a bare number, because what a provenance record
    has to carry is not the seed but the fact that it came from the project seed and how.
    """
    project = project_seed(root)
    digest = hashlib.blake2b(f"{project}:{component}".encode(), digest_size=8).hexdigest()
    return {
        "project_seed": project,
        "component": component,
        "derivation": "int(blake2b('<project_seed>:<component>', digest_size=8), 16) "
                      f"% {SEED_MODULUS}",
        "seed": int(digest, 16) % SEED_MODULUS,
    }
