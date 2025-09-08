#!/bin/bash

set -ex

cwd="${PWD}"
toplevel=$(git rev-parse --show-toplevel)

cd "${toplevel}/frontend"

if [ "${SKIP_BUILD}" != "yes" ]; then
  npm ci
  export MYKN_API_URL=""
  npm run build
fi

ln -s -f ${toplevel}/frontend/dist/index.html ${toplevel}/backend/src/openbeheer/templates/index.html
ln -s -f ${toplevel}/frontend/dist/static/assets ${toplevel}/backend/src/openbeheer/static/assets
