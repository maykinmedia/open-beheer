#!/usr/bin/zsh

docker compose \
  -f docker-compose.
  docker compose -f keycloak/docker-compose.yaml
  docker compose -f objecttypen/docker-compose.yaml
  docker compose -f openzaak/docker-compose.yaml up
  up -d
