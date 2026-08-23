# Setting up a project from this starting point

This repository is a **starting point, not a finished vault**. It carries the structure,
the instructions and the skills; the project is yours to fill in.

## 1 — Copy it out

```bash
cp -r /path/to/paper_starting_point/. /path/to/new-project/
cd /path/to/new-project
```

The trailing dot matters, or `.claude/` is left behind.

## 2 — Substitute the placeholders

`.claude/settings.json` contains `<PARENT_DIR>` and `<HOME>`. Replace both with real paths,
or delete the `claudeMdExcludes` entries you do not need — they exist to stop a parent
directory's `CLAUDE.md` leaking into this project's instructions, which would silently
change the method.

## 3 — Python environment

```bash
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
```

Invoke it directly as `.venv/bin/python` — never `source .venv/bin/activate && python`.
Activation is a second shell segment, which turns a pre-approved command into a permission
prompt on every call.

## 4 — Pin the analysis environment

The analysis environment is **not** the `.venv` that runs the machinery. Fill in
`environment/environment.yml` with what the analysis itself needs, then `/pin-environment`
to produce the lockfile, and `/pin-environment verify` to confirm it rebuilds clean.

## 5 — Fill in `readme-at-start.md`

Before doing any real work. In particular fix the **project seed**, the **tracking level**
and the **compute budget for stability work** — these are the three settings that otherwise
get decided implicitly, halfway through, by whoever is impatient.

## 6 — State the top-level claim

Edit `analysis/claim.md` with the one question this project answers. Everything in the tree
hangs off it, so it is worth more than one draft.

## 7 — Git

```bash
git init && git add . && git commit -m "Start from paper_starting_point"
```

For a remote, the agent will ask you for the owner/organisation and repository name rather
than inferring either. Keep it **private until release**; `/release` runs the secrets and
data-permission scan that must precede anything becoming public.

## 8 — Check it works before there is anything in it

```bash
.venv/bin/python AI-internal/useful-scripts/check_invariants.py
.venv/bin/python AI-internal/useful-scripts/node.py tree
```

An empty tree should pass cleanly. If it does not, fix that before adding analysis — a
checker you have learned to ignore is worse than none.

## What to change, and what not to

**Change freely**: `readme-at-start.md`, `analysis/claim.md`, the environment, the plans,
anything in `Human-input/`.

**Change deliberately**: `AGENTS.md` and `.claude/commands/`. They are part of the method —
a change to them is a methodological change, and it is published as such. Commit it on its
own, with a message saying what changed about the method.

**Do not weaken**: `check_invariants.py`. When it fails, fix the cause.
