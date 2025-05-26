#!/bin/sh

ZTC_URL=${ZTC_URL-"http://localhost:8003/catalogi/api/v1/schema/openapi.yaml"}

PWD=$(pwd)
BACKEND_ROOT=$(dirname "${0}")/..
DOCKER_DIR="${BACKEND_ROOT}/docker-services/openzaak"
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
    cd "${DOCKER_DIR}" || error "Open Zaak docker not found"
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
    httpx -m HEAD "${ZTC_URL}" > /dev/null
}

url_ready || use_docker

while ! url_ready  ; do
  echo "Waiting for ${ZTC_URL} to be ready."
  sleep 2
done

mkdir -p "${TARGET_DIR}"

datamodel-codegen \
    --input-file-type openapi \
    --url "${ZTC_URL}" \
    --formatters black isort \
    --target-python-version 3.12 \
    --openapi-scopes schemas paths parameters \
    --output-model-type msgspec.Struct \
    --additional-imports datetime.date,datetime.datetime \
    --snake-case-field \
    --use-union-operator \
    --enable-version-header \
    --keyword-only \
    --output "${TARGET_DIR}/ztc.py" \
    || error "Could not generate types"
