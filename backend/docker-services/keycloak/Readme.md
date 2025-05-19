To export the realm settings, run this command in the keycloak container:

```bash
/opt/keycloak/bin/kc.sh export --file /tmp/realm_export.json --realm openbeheer-dev
```

The admin console is accessible with credentials `admin` / `admin`, and there are 2 test users with credentials `alice_doe` / `aNic3Passw0rd` and `john_doe` / `aNic3Passw0rd`.