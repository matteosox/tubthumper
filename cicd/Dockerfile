# syntax=docker/dockerfile:1.2
FROM ubuntu:20.04

# Install apt-get packages
COPY cicd/install_packages.sh /usr/local/bin/install_packages.sh
RUN --mount=type=cache,target=/var/cache/apt \
    install_packages.sh python3.6 python3.7 python3.8 python3.8-venv python3.9 python3.10 python3.10-distutils pypy3 git shellcheck

# Create cicd user & switch to it
ENV USER=cicd
RUN groupadd --gid 1024 "$USER" && useradd --uid 1024 --create-home --gid 1024 "$USER"
USER "$USER"
WORKDIR "/home/$USER"

# Create and activate virtual environment
ENV VIRTUAL_ENV="/home/$USER/.venv"
RUN python3.8 -m venv "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install python dependencies
RUN mkdir -p .cache/pip
COPY --chown="$USER" requirements/requirements.txt "$VIRTUAL_ENV"
RUN --mount=type=cache,target=/home/cicd/.cache/pip,uid=1024,gid=1024 \
    pip install pip setuptools wheel --constraint "$VIRTUAL_ENV"/requirements.txt && \
    pip install --requirement "$VIRTUAL_ENV"/requirements.txt

WORKDIR "/home/$USER/tubthumper"

# Copy over source code and install using pip
COPY --chown="$USER" tubthumper tubthumper/
COPY --chown="$USER" LICENSE pyproject.toml README.md setup.cfg setup.py ./
RUN --mount=type=cache,target=/home/cicd/.cache/pip,uid=1024,gid=1024 \
    pip install --editable .

CMD ["bash"]
