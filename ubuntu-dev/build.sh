#!/usr/bin/env bash
set -eu -o pipefail
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
distribution=${1:-24}
. "$script_dir"/vars "$distribution"
docker build -f Dockerfile"$distribution" -t "$UBUNTU_DEV_IMG_NAME" .
docker tag "$UBUNTU_DEV_IMG_NAME" "$UBUNTU_DEV_IMG_LATEST"
docker tag "$UBUNTU_DEV_IMG_NAME" "$UBUNTU_DEV_IMG_VERSIONED"

