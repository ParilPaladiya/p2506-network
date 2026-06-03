# Sharing and Handoff Guide

This document is for the repository owner when preparing the project for other contributors.

## Recommended Sharing Model

Use this repository as the single source of truth for:

- Docker Compose configuration
- database bootstrap SQL
- Node-RED flow logic
- Grafana provisioning
- source code for services that may later be rebuilt and republished

For a fresh clone, the default startup state should match the committed Node-RED flow in `node-red/data/flows.json` and the committed Grafana dashboard in `grafana/provisioning/dashboards/api-postgres-dashboard.json`.

Do not use your live local runtime folders as the source of truth.

## What Contributors Should Receive

At minimum, contributors need:

- repository access
- Docker Desktop or Docker Engine with Compose v2
- the sample environment file `.env.example`
- the default login credentials documented in `README.md`

They should not need:

- your personal `.env`
- your `grafana/data/grafana.db`
- your local Grafana users/preferences
- your Node-RED `flows_cred.json`

## Clean Clone Experience

For the easiest onboarding flow:

1. Share the Git repository.
2. Tell contributors to copy `.env.example` to `.env`.
3. Tell them to run `docker-compose up -d`.
4. Tell them to wait for PostgreSQL health to turn green in `docker-compose ps`.
5. Tell them to open:
   - Grafana: `http://localhost:3000`
   - Node-RED: `http://localhost:1880`
   - Alert API: `http://localhost:5000/health`

## Important Runtime-State Rules

### Grafana

- `grafana/provisioning/` is shareable.
- `grafana/provisioning/dashboards/api-postgres-dashboard.json` is the current shared dashboard.
- `grafana/data/` is local state only.
- Avoid relying on UI-only dashboard changes.
- File-provisioned dashboards should be updated by exporting JSON back into `grafana/provisioning/dashboards/`.

### Node-RED

- `node-red/data/flows.json` is shareable.
- It should represent the same MQTT-to-PostgreSQL flow that is present after a clean startup.
- `node-red/data/flows_cred.json` is local encrypted credential state.
- `node-red/data/node_modules/` is local installed runtime state.
- `node-red/data/package.json` and `package-lock.json` describe shareable Node-RED dependencies.

## Before You Publish the Repo

- Ensure `.env` is ignored and `.env.example` is present.
- Ensure `grafana/data/` is ignored.
- Ensure `node-red/data/flows_cred.json` and `node-red/data/node_modules/` are ignored.
- Ensure the shared Grafana dashboard JSON matches the intended PostgreSQL dashboard.
- Ensure the tracked Node-RED flow file matches the intended MQTT-to-PostgreSQL flow.
- Ensure `README.md` matches the current service ports and image tags.

## If You Want Contributors To See Exactly Your Current UI

There are two options:

### Preferred

Convert the intended UI state into shareable source files:

- export Grafana dashboards into `grafana/provisioning/dashboards/`
- deploy Node-RED flows so `flows.json` is updated

### Not Preferred

Ship runtime folders directly.

This is fragile because it carries machine-specific state, saved sessions, and UI-only artifacts. Avoid this unless you are creating a disposable demo bundle rather than a maintainable repo.
