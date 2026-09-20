"""Derive per-component seeds from the one project seed (Rule 6).

Reads the project seed from `readme-at-start.md`'s settings table rather than carrying a
second copy of it, so there is only one number that could disagree.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def project_seed() -> int:
    text = (REPO_ROOT / "readme-at-start.md").read_text()
    m = re.search(r"Project random seed \| `(\d+)`", text)
    if not m:
        raise RuntimeError("could not find the project seed in readme-at-start.md")
    return int(m.group(1))


def component_seed(component: str) -> int:
    key = f"{project_seed()}:{component}".encode()
    return int.from_bytes(hashlib.blake2b(key, digest_size=8).digest(), "big") % 2**32


if __name__ == "__main__":
    import sys
    print(component_seed(sys.argv[1]) if len(sys.argv) > 1 else project_seed())
