"""One colour and one marker per model, stable across combinations and across batches.

Every figure under `04_score/03_compare` draws one series per model, and until batch 10
each of them built its own colour map by zipping the models it happened to find against a
list of four colours. That worked while the project had four models and broke on the
fifth: `zip` stops at the shorter argument, so the two figures keyed by `marker` would have
silently drawn nothing for the new model, and the third raised a `KeyError`. The failure
mode worth naming is the silent one — a figure missing a series is a figure a reader
believes.

So the mapping lives here, once, and it has two properties the per-script versions did not.

**It does not run out.** The palette is longer than the project can plausibly need, and a
model beyond its end still gets a colour rather than an exception or an absence.

**A model keeps its colour when the set of models changes.** This is the property that
matters and the reason the assignment is not "sorted position in the list". Figures are
drawn per combination, and different combinations hold different sets of models: `main` has
four, a combination that adds a candidate has five, one that inherits has whatever it
inherited. Under positional assignment, adding a model whose name sorts early would
re-colour every other model, and two figures from two combinations could not be laid side
by side. Assigning from the model's own name instead means the reference is the same colour
in every figure in the project, whatever else is in it.

The assignment is BLAKE2b of the name into the palette, with linear probing on collision —
the same construction `project_seed.py` uses to derive a component seed, for the same
reason: a stable function of a name, with no table anybody has to remember to update.

Not a step: `scripts/lib/` is a subdirectory, so `node.py` does not put it in any node's
`run.sh`. It is imported by the figures that need it.
"""

from __future__ import annotations

import hashlib

# Ten hues that stay distinguishable in print and are not the default matplotlib cycle,
# which repeats across figures produced by other tools. Ordered so that the first few are
# the most separable, since most figures use only a handful.
PALETTE = (
    "#2166ac",  # blue
    "#b2182b",  # red
    "#4d9221",  # green
    "#8c510a",  # brown
    "#762a83",  # purple
    "#01665e",  # teal
    "#d6604d",  # salmon
    "#5aae61",  # light green
    "#8073ac",  # violet
    "#bf812d",  # ochre
)

MARKERS = ("o", "s", "^", "D", "v", "P", "X", "*", "<", ">")


def _slot(name: str, taken: set[int], size: int) -> int:
    """A stable slot for `name`, avoiding the slots already taken.

    Linear probing rather than rehashing, so that which slot a colliding name lands in
    depends only on the names before it in a fixed order -- which `assign` fixes by
    sorting. A collision therefore moves one model's colour and never the others'.
    """
    start = int(hashlib.blake2b(name.encode(), digest_size=8).hexdigest(), 16) % size
    for step in range(size):
        slot = (start + step) % size
        if slot not in taken:
            return slot
    raise SystemExit(f"more models than the palette has slots ({size}); lengthen it "
                     f"rather than letting two models share a colour")


def assign(models: list[str] | set[str], table: tuple[str, ...]) -> dict[str, str]:
    """Map each model to one entry of `table`, stably and without repetition."""
    taken: set[int] = set()
    out: dict[str, str] = {}
    # Sorted, so that the probing order is a function of the set and not of the order the
    # caller happened to read the models in.
    for name in sorted(models):
        slot = _slot(name, taken, len(table))
        taken.add(slot)
        out[name] = table[slot]
    return out


def colours(models: list[str] | set[str]) -> dict[str, str]:
    """One colour per model."""
    return assign(models, PALETTE)


def markers(models: list[str] | set[str]) -> dict[str, str]:
    """One matplotlib marker per model."""
    return assign(models, MARKERS)
