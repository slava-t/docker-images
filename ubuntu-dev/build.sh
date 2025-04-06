#!/usr/bin/env bash
set -eu -o pipefail
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. "$script_dir"/vars
docker build -t "$UBUNTU_DEV_IMG_NAME" .
docker tag "$UBUNTU_DEV_IMG_NAME" "$UBUNTU_DEV_IMG_LATEST"
docker tag "$UBUNTU_DEV_IMG_NAME" "$UBUNTU_DEV_IMG_VERSIONED"

