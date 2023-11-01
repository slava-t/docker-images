#!/usr/bin/env bash
set -eu -o pipefail
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. "$script_dir"/vars
#docker push "$FABANSIBLE_IMG_LATEST"
docker push "$FABANSIBLE_IMG_VERSIONED"

