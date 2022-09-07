#!/usr/bin/env bash
set -eu -o pipefail
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. "$script_dir"/vars
docker push "$SMTP_DEBUG_IMG_LATEST"
docker push "$SMTP_DEBUG_IMG_VERSIONED"

