#! /usr/bin/env bash
set -o errexit -o nounset -o pipefail
IFS=$'\n\t'

echo "Installing shfmt"

# shfmt doesn't have an apt package, so we install it using
# webinstaller, but unfortunately that requires quite a bit of
# cleanup after to remove unnecessary stuff, and also put
# shfmt in a place on the PATH for non-login shells

cleanup() {
    rm -rf .config
    rm -rf .local
    rm -rf Downloads
}
trap cleanup EXIT

curl -sS https://webinstall.dev/shfmt | bash
mv ~/.local/opt/shfmt-v3.4.0/bin/shfmt /usr/bin/
