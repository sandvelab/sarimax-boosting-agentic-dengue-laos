"""Assemble candidate 3's configuration from the choice above it and the pool's members.

The same mechanism the other two candidates use — `03_models/scripts/lib/assemble_config.py`
— with the one thing that is particular to this candidate supplied here.

That thing is the second input. **The pool's membership is not an option value.** It is a
document, listing four contract directories, their entry points, their configurations and
the sha256 of every file behind them, so the configuration carries **the path to that
document and its hash** rather than its contents. The model refuses to run if the two
disagree, which is what stops a members file edited after assembly from producing a run
whose record names a pool it did not contain.

**The covariates are the union of the members'.** The pool needs every column any member
needs, and no member can be handed a frame missing one; asking for the union is the only
setting that is correct whatever the members turn out to be. So the members' covariates go
into the merge before any fork of this node speaks.

Candidate 3 draws from its own component seed, and that seed governs only the pool's own
draw — which member each of the thousand samples comes from. The members draw from their
own seeds, through their own entry points.

Writes, under results/$COMBO/:
  model_configuration.yaml   what chap eval is pointed at
  candidate_spec.json        the choices, the merged options, the members and the seed
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

NODE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NODE.parents[1] / "scripts" / "lib"))

from assemble_config import assemble, moved_here, repo_root  # noqa: E402

ROOT = repo_root(NODE)
COMBO = os.environ.get("COMBO", "main")


def main() -> None:
    members_file = NODE / "results" / COMBO / "members.json"
    if not members_file.exists():
        raise SystemExit(f"no membership for combination {COMBO!r}: {members_file} is "
                         f"missing. scripts/prepare_members.py runs first.")
    membership = json.loads(members_file.read_text())

    options = {
        "members_file": str(members_file.relative_to(ROOT)),
        "members_sha256": hashlib.sha256(members_file.read_bytes()).hexdigest(),
    }
    spec, out = assemble(
        NODE, candidate="ensemble",
        options_first=options,
        covariates_first=list(membership["additional_continuous_covariates"]),
        spec_extra={
            "members": [
                {"name": m["name"], "node": m["node"], "model_dir": m["model_dir"],
                 "model_config": m["model_config"], "configured_by": m["configured_by"]}
                for m in membership["members"]],
            "members_file": options["members_file"],
            "members_sha256": options["members_sha256"],
        })

    moved = moved_here(spec)
    print(f"ensemble[{spec['combo']}]: {spec['choices']}, "
          f"{len(spec['members'])} members, "
          f"covariates {spec['additional_continuous_covariates'] or 'none'}, "
          f"seed {spec['seed_derivation']['seed']}"
          + (f"; taken here: {moved}" if spec["combo"] != "main" else "")
          + f" -> {out}")


if __name__ == "__main__":
    main()
