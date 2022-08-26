#!/usr/bin/env bash
set -eu -o pipefail
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. "$script_dir"/vars
docker build -t "$JAMMY_PYTHON3_IMG_NAME" .
docker tag "$JAMMY_PYTHON3_IMG_NAME" "$JAMMY_PYTHON3_IMG_LATEST"
docker tag "$JAMMY_PYTHON3_IMG_NAME" "$JAMMY_PYTHON3_IMG_VERSIONED"

