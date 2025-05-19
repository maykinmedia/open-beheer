# Open Zaak

The `docker-compose.yml` compose file is available to run an instance of Open Zaak.

## docker compose

Start an instance in your local environment from this directory:

```bash
docker compose up
```

This brings up the admin at http://localhost:8003/admin/. You can log in with the `admin` / `admin`
credentials.

## Load fixtures

The fixtures in `./fixtures` are automatically loaded when the Open Zaak container starts.

> **Note**: We want to eventually remove fixtures, and create the data in Open Zaak for each test before the test is run when recording VCR cassettes.
