# syntax=docker/dockerfile:1.2
FROM ubuntu:20.04

# Install OS-level packages
COPY docker/install_packages.sh docker/install_shfmt.sh docker/timer.sh /usr/local/bin/
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    install_packages.sh \
    python3.7 python3.7-distutils python3.8 python3.8-distutils \
    python3.9 python3.9-distutils python3.10 python3.10-venv \
    python3.11 pypy3 git shellcheck curl tini
RUN install_shfmt.sh

# Create and activate virtual environment
ENV VIRTUAL_ENV=/root/.venv
RUN python3.10 -m venv "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Setup root home directory
WORKDIR /root/tubthumper

# Install Python dependencies
COPY requirements/requirements.txt "$VIRTUAL_ENV"
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install pip setuptools wheel && \
    pip install --requirement "$VIRTUAL_ENV"/requirements.txt

# Copy over source code and install using pip
COPY tubthumper tubthumper/
COPY LICENSE pyproject.toml README.md ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --editable .

# Trust repo directory
RUN git config --global --add safe.directory /root/tubthumper

ENTRYPOINT ["tini", "-v", "--"]
CMD [ "timer.sh" ]
