#!/usr/bin/env bash
set -eu -o pipefail
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. "$script_dir"/vars
docker push "$FOCAL_ANSIBLE_IMG_LATEST"
docker push "$FOCAL_ANSIBLE_IMG_VERSIONED"

