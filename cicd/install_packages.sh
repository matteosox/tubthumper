#! /usr/bin/env bash
set -euf -o pipefail

# Utility for installing apt-get packages
# tidily and minimally by cleaning them up. Inspired by 
# https://pythonspeed.com/articles/system-packages-docker/
# and https://vsupalov.com/buildkit-cache-mount-dockerfile/

# Ubuntu image is configured to delete cached files. 
# We're using a cache mount, so we remove that config.
rm --force /etc/apt/apt.conf.d/docker-clean
 
# Tell apt-get we're never going to be able to give manual
# feedback
export DEBIAN_FRONTEND=noninteractive

# Update the package listing, so we know what package exist
apt-get update

# Install security updates
apt-get --yes upgrade

# Add deadsnakes ppa to install other versions of python
apt-get --yes install --no-install-recommends software-properties-common
add-apt-repository ppa:deadsnakes/ppa
apt-get update

# Install packages, without unnecessary recommended packages
apt-get --yes install --no-install-recommends "$@"

# Delete cached files we don't need anymore
rm --recursive --force /var/lib/apt/lists/*
