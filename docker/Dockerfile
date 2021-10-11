# syntax=docker/dockerfile:1.2
FROM ubuntu:20.04

# Install apt-get packages
COPY docker/install_packages.sh docker/timer.sh /usr/local/bin/
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    install_packages.sh python3.6 python3.7 python3.8 python3.8-venv python3.9 python3.10 python3.10-distutils pypy3 git shellcheck

# Create and activate virtual environment
ENV VIRTUAL_ENV=/root/.venv
RUN python3.8 -m venv "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Setup root home directory
WORKDIR /root/tubthumper

# Install Python dependencies
COPY requirements/requirements.txt "$VIRTUAL_ENV"
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install pip setuptools wheel --constraint "$VIRTUAL_ENV"/requirements.txt && \
    pip install --requirement "$VIRTUAL_ENV"/requirements.txt

# Copy over source code and install using pip
COPY tubthumper tubthumper/
COPY LICENSE pyproject.toml README.md setup.cfg setup.py ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --editable .

CMD [ "timer.sh" ]
