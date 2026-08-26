# Frozen environment, for when upstream repositories change or disappear.
#
# Build:  docker build -t analysis -f environment/Dockerfile .
# Run:    docker run --rm -v "$PWD":/work -w /work analysis bash analysis/run.sh
#
# Built from environment/lock.txt rather than from environment.yml, so the image carries the
# resolved package set and not a fresh resolution of it.
#
# VERIFIED 2026-08-26 (batch 7): builds in about seven minutes to 1.62 GB, giving CPython
# 3.13.0 and chap 2.1.0. Inside it, 01_data and 02_setup reproduce byte-identically and both
# baselines reproduce their per-cell scores exactly. What it cannot run is
# analysis/03_models/02_reference, which starts a container of its own -- see
# AI-generated/validation/26-08-26_cleanroom.md.
FROM python:3.13.0-slim

RUN apt-get update && apt-get install -y --no-install-recommends git curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV VIRTUAL_ENV=/opt/chapenv
RUN uv venv --python 3.13.0 "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY environment/lock.txt /tmp/lock.txt
RUN uv pip install --python "$VIRTUAL_ENV/bin/python" -r /tmp/lock.txt

WORKDIR /work
