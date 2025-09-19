#!/bin/sh

API="$1"

case "$API" in
    ztc)
        API_URL=${ZTC_URL:-"http://localhost:8003/catalogi/api/v1/schema/openapi.yaml"}
        DOCKER_DIR="${BACKEND_ROOT}/docker-services/openzaak"
        ;;
    selectielijst)
        API_URL=${SELECTIELIJST_API_URL:-"https://selectielijst.openzaak.nl/api/v1/schema/openapi.json"}
        ;;
    objecttypen)
        API_URL=${OBJECTTYPEN_URL:-"http://localhost:8004/api/v2/schema/openapi.yaml"}
        DOCKER_DIR="${BACKEND_ROOT}/docker-services/objecttypen"
        ;;
    *)
        echo "Invalid argument: $API"
        echo "Usage: $0 {ztc|selectielijst|objecttypen}"
        exit 1
        ;;
esac

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

use_docker() {
    cd "${DOCKER_DIR}" || error "Docker compose YAML not found"
    (type datamodel-codegen) || error "datamodel-codegen not found; try activating venv"

    if (type docker-compose) then
        DOCKER_COMPOSE=docker-compose
    elif (type docker)
        DOCKER_COMPOSE="docker compose"
    then
        echo "No docker compose found" > /dev/null 2>&1
        quit 1
    fi

    $DOCKER_COMPOSE up -d
    cleanup() {
        go_back
        $DOCKER_COMPOSE down
        exit
    }
    trap cleanup EXIT INT TERM
}

url_ready() {
    httpx -m HEAD "${API_URL}" > /dev/null
}

url_ready || use_docker

while ! url_ready  ; do
  echo "Waiting for ${API_URL} to be ready."
  sleep 2
done

mkdir -p "${TARGET_DIR}"

datamodel-codegen \
    --input-file-type openapi \
    --url "${API_URL}" \
    --formatters ruff-check ruff-format \
    --target-python-version 3.12 \
    --openapi-scopes schemas paths parameters \
    --output-datetime-class datetime \
    --output-model-type msgspec.Struct \
    --snake-case-field \
    --use-union-operator \
    --enable-version-header \
    --keyword-only \
    --output "${TARGET_DIR}/${API}.py" \
    || error "Could not generate types"
