To export the realm settings, run this command in the keycloak container:

```bash
/opt/keycloak/bin/kc.sh export --file /tmp/realm_export.json --realm openarchiefbeheer-dev
```