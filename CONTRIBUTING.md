# Contributing Guide

This project is shared as a Docker Compose stack. Contributors should be able to clone the repository, create a local `.env`, and start the full system without installing Python or Node.js locally.

## Development Model

- `docker-compose.yaml` is the main entrypoint for running the stack.
- `alert-manager`, `alert-api`, and `data-generator` are source folders for published images.
- `node-red/data/flows.json` and `node-red/data/settings.js` are the shareable Node-RED sources.
- `grafana/provisioning/` is the shareable Grafana source of truth.
- `node-red/data/flows_cred.json`, `node-red/data/node_modules/`, and `grafana/data/` are local runtime state and should not be committed.

## First-Time Setup

1. Copy `.env.example` to `.env`.
2. Adjust credentials only if your machine or team setup requires it.
3. Start the stack:

```bash
docker-compose up -d
```

4. Verify services:

```bash
docker-compose ps
docker-compose logs -f grafana
docker-compose logs -f nodered
```

## What To Commit

- Commit changes to:
  - `docker-compose.yaml`
  - `README.md`
  - `CONTRIBUTING.md`
  - `docs/`
  - `mysql/init/init.sql`
  - `node-red/data/flows.json`
  - `node-red/data/settings.js`
  - `node-red/data/package.json`
  - `node-red/data/package-lock.json`
  - `grafana/provisioning/`
  - source code under `alert-api/`, `alert-manager/`, and `data-generator/`

- Do not commit:
  - `.env`
  - `grafana/data/`
  - `node-red/data/flows_cred.json`
  - `node-red/data/node_modules/`
  - Node-RED backup files
  - machine-specific cache files

## Node-RED Workflow

- Use the Node-RED UI at `http://localhost:1880`.
- Click `Deploy` after flow edits so `node-red/data/flows.json` is updated.
- Keep `NODE_RED_CREDENTIAL_SECRET` stable across restarts if you want existing credentials to remain decryptable.
- If credentials need to be re-entered on another machine, that is expected when `flows_cred.json` is not shared.

## Grafana Workflow

- Use Grafana at `http://localhost:3000`.
- Shared dashboards belong in `grafana/provisioning/dashboards/`.
- Local UI state under `grafana/data/` is intentionally non-shareable.
- If you want to update the shared dashboard, export the dashboard JSON and replace `grafana/provisioning/dashboards/api-mysql-dashboard.json`.

## Published Image Workflow

Compose currently runs these services from published images:

- `parilpaladiya/alert-manager:1.1`
- `parilpaladiya/alert-api:1.2`
- `parilpaladiya/data-generator:1.1`

When source changes in those folders need to be shared:

1. Rebuild the image locally.
2. Push the image to the registry.
3. Update the image tag in `docker-compose.yaml`.

Example:

```bash
docker build -t <registry>/alert-manager:<tag> ./alert-manager
docker build -t <registry>/alert-api:<tag> ./alert-api
docker build -t <registry>/data-generator:<tag> ./data-generator
```

## Review Checklist Before Sharing Changes

- `docker-compose up -d` starts cleanly.
- `docker-compose ps` shows MySQL healthy.
- Node-RED flows are reflected in `node-red/data/flows.json`.
- Grafana shareable changes are reflected in `grafana/provisioning/`.
- No local runtime state was accidentally added to the commit.
