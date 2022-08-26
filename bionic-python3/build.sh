#!/usr/bin/env bash
set -eu -o pipefail
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. "$script_dir"/vars
docker build -t "$BIONIC_PYTHON3_IMG_NAME" .
docker tag "$BIONIC_PYTHON3_IMG_NAME" "$BIONIC_PYTHON3_IMG_LATEST"
docker tag "$BIONIC_PYTHON3_IMG_NAME" "$BIONIC_PYTHON3_IMG_VERSIONED"

