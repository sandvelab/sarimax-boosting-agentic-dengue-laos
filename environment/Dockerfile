# Frozen environment, for when upstream repositories change or disappear.
# Build:  docker build -t analysis -f environment/Dockerfile .
# Run:    docker run --rm -v "$PWD":/work -w /work analysis bash analysis/run.sh
FROM condaforge/miniforge3:latest

COPY environment/environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml && conda clean -afy
SHELL ["conda", "run", "-n", "analysis", "/bin/bash", "-c"]
ENV PATH=/opt/conda/envs/analysis/bin:$PATH

WORKDIR /work
