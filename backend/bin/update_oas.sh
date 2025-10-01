#!/bin/sh

PWD=$(pwd)

go_back() {
    cd "$PWD" || error "Original working directory $PWD doesn't exist anymore"
}
trap go_back EXIT INT TERM

BACKEND_ROOT=$(dirname "${0}")/..
FRONTEND_ROOT=$(dirname "${0}")/../../frontend

cd $BACKEND_ROOT

src/manage.py spectacular \
    --validate \
    --fail-on-warn \
    --lang=en \
    --file openbeheer-oas.yaml

cd $FRONTEND_ROOT
npm ci
npm run update-types
