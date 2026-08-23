# claims

`claims.md` holds everything the analysis supports: short statements, each bound to the
result grounding it, with its scope, the alternatives that would have supported something
different, and who authored it.

Maintained through `/claims`, which wraps `AI-internal/useful-scripts/claims.py`:

```bash
.venv/bin/python AI-internal/useful-scripts/claims.py audit
.venv/bin/python AI-internal/useful-scripts/claims.py check-text \
    Human-AI-collaboration/manuscript/<draft>.md
```

Two things this file is for beyond writing the paper. It is the searchable record of what
the analysis established, independent of what reached the manuscript — including the
findings that did not. And it is the practical control against generated text drifting away
from the analysis: a sentence that cannot name the result it rests on does not get written.
