"""Assemble candidate 1's configuration from the six choices above it.

The six forks under this node each take one decision about what the model is. This script
closes that chain the way `02_setup/scripts/assemble_setup.py` closes the setup chain, and
for the same reason: the model must not have to know how many choices there are or which of
them are forks.

**How it does that is not here.** Every candidate family assembles its configuration the
same way, so the mechanism is `03_models/scripts/lib/assemble_config.py` and this file is
the runner that names the candidate — the shape the weighting fork's three children have one
node over. Candidate 1 brings nothing of its own to the merge, so there is nothing below the
call but the call.

Writes, under results/$COMBO/:
  model_configuration.yaml   what chap eval is pointed at
  candidate_spec.json        the six choices, the merged options, and the seed derivation
"""

from __future__ import annotations

import sys
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NODE.parents[1] / "scripts" / "lib"))

from assemble_config import assemble, moved_here  # noqa: E402


def main() -> None:
    spec, out = assemble(NODE, candidate="hier_nb")
    moved = moved_here(spec)
    print(f"candidate[{spec['combo']}]: {spec['choices']}, "
          f"covariates {spec['additional_continuous_covariates']}, "
          f"seed {spec['seed_derivation']['seed']}"
          + (f"; taken here: {moved}" if spec["combo"] != "main" else "")
          + f" -> {out}")


if __name__ == "__main__":
    main()
