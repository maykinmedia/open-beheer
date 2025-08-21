#!/bin/bash

set -ex

cwd="${PWD}"
toplevel=$(git rev-parse --show-toplevel)

cd "${toplevel}/frontend"

npm ci

export MYKN_API_URL=""

npm run build

ln -s ${toplevel}/frontend/dist/index.html ${toplevel}/backend/src/openbeheer/templates/index.html
ln -s ${toplevel}/frontend/dist/static/assets ${toplevel}/backend/src/openbeheer/static/assets
