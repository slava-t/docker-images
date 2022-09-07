#!/usr/bin/env bash
set -eu -o pipefail
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. "$script_dir"/vars
docker build -t "$SMTP_DEBUG_IMG_NAME" .
docker tag "$SMTP_DEBUG_IMG_NAME" "$SMTP_DEBUG_IMG_LATEST"
docker tag "$SMTP_DEBUG_IMG_NAME" "$SMTP_DEBUG_IMG_VERSIONED"

