#!/usr/bin/env bash
set -eu -o pipefail
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. "$script_dir"/vars
docker build -t "$FOCAL_PYTHON3_IMG_NAME" .
docker tag "$FOCAL_PYTHON3_IMG_NAME" "$FOCAL_PYTHON3_IMG_LATEST"
docker tag "$FOCAL_PYTHON3_IMG_NAME" "$FOCAL_PYTHON3_IMG_VERSIONED"

