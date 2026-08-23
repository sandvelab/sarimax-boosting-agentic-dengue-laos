#!/usr/bin/env bash
# Main script for node: analysis (root)
# Running this reproduces the entire reported analysis, following the main path
# at every alternatives fork. Never break that property.
set -euo pipefail
cd "$(dirname "$0")"

# Sub-analyses: every child runs, in order.
# (No children yet -- create them with /node.)

# Own scripts -- add calls here as scripts/ fills up.
