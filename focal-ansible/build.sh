#!/usr/bin/env bash
set -eu -o pipefail
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. "$script_dir"/vars
docker build -t "$FOCAL_ANSIBLE_IMG_NAME" .
docker tag "$FOCAL_ANSIBLE_IMG_NAME" "$FOCAL_ANSIBLE_IMG_LATEST"
docker tag "$FOCAL_ANSIBLE_IMG_NAME" "$FOCAL_ANSIBLE_IMG_VERSIONED"

