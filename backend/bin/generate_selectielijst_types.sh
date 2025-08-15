#!/bin/sh

SELECTIELIJST_API_URL=${SELECTIELIJST_API_URL:-"https://selectielijst.openzaak.nl/api/v1/schema/openapi.json"}

PWD=$(pwd)
BACKEND_ROOT=$(dirname "${0}")/..
TARGET_DIR="${BACKEND_ROOT}/src/openbeheer/types"

go_back() {
    cd "$PWD" || error "Original working directory $PWD doesn't exist anymore"
}
trap go_back EXIT INT TERM

error() {
    echo "$1" > /dev/null 2>&1
    exit 1
}

mkdir -p "${TARGET_DIR}"

datamodel-codegen \
    --input-file-type openapi \
    --url "${SELECTIELIJST_API_URL}" \
    --formatters ruff-check ruff-format \
    --target-python-version 3.12 \
    --openapi-scopes schemas paths parameters \
    --output-model-type msgspec.Struct \
    --snake-case-field \
    --use-union-operator \
    --enable-version-header \
    --keyword-only \
    --output "${TARGET_DIR}/selectielijst.py" \
    || error "Could not generate types"
