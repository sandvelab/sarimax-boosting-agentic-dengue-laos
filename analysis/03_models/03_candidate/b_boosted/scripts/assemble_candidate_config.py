"""Assemble candidate 2's configuration from the two choices above it.

The same mechanism candidate 1 uses, and deliberately the same: the model must not have to
know how many choices there are or which of them are forks. It is
`03_models/scripts/lib/assemble_config.py`, and this file is the runner that names the
candidate. Batches 10 and 11 both logged that these scripts were near-copies and scheduled
the lift for the batch that re-runs the combinations they configured; batch 14 is that
batch.

Candidate 2 draws from its own component seed, derived from this node's path rather than
candidate 1's, which is what Rule 6's "one seed derived downward" means: two components of
one project, two derivations, one number behind them both.

Writes, under results/$COMBO/:
  model_configuration.yaml   what chap eval is pointed at
  candidate_spec.json        the two choices, the merged options, and the seed derivation
"""

from __future__ import annotations

import sys
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NODE.parents[1] / "scripts" / "lib"))

from assemble_config import assemble, moved_here  # noqa: E402


def main() -> None:
    spec, out = assemble(NODE, candidate="boosted")
    moved = moved_here(spec)
    print(f"boosted[{spec['combo']}]: {spec['choices']}, "
          f"covariates {spec['additional_continuous_covariates']}, "
          f"seed {spec['seed_derivation']['seed']}"
          + (f"; taken here: {moved}" if spec["combo"] != "main" else "")
          + f" -> {out}")


if __name__ == "__main__":
    main()
