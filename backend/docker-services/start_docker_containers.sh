#!/bin/bash
  docker compose -f keycloak/docker-compose.yaml up -d
  docker compose -f objecttypen/docker-compose.yaml up -d
  docker compose -f openzaak/docker-compose.yaml up -d