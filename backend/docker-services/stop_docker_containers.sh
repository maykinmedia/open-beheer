#!/bin/bash
  docker compose -f keycloak/docker-compose.yaml down
  docker compose -f objecttypen/docker-compose.yaml down
  docker compose -f openzaak/docker-compose.yaml down
