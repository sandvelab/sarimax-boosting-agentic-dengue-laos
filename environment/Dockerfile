# Frozen environment, for when upstream repositories change or disappear.
#
# Build:  docker build -t analysis -f environment/Dockerfile .
# Run:    docker run --rm -v "$PWD":/work -w /work analysis bash analysis/run.sh
#
# Built from environment/lock.txt rather than from environment.yml, so the image carries the
# resolved package set and not a fresh resolution of it.
#
# NOT YET VERIFIED: no Docker daemon was available on the machine that wrote this, so the
# image has never been built. Treat it as a specification until /pin-environment verify has
# run it. See environment/README.md, "What cannot be pinned".
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
