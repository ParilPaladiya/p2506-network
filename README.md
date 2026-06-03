# P2506 Network IoT Monitoring Stack

Docker Compose-based IoT monitoring setup with MQTT ingestion, PostgreSQL storage, anomaly detection, a Flask alert API, Node-RED processing, and Grafana dashboards.
For a fresh clone, the only setup step should be copying `.env.example` to `.env` and running `docker-compose up -d`.

## What This Repo Contains

- MQTT broker with Mosquitto
- PostgreSQL database with bootstrap schema
- Node-RED flow that stores raw sensor data and is tracked in `node-red/data/flows.json`
- Alert manager that classifies readings and stores alerts
- Alert API for querying alert history
- Grafana datasources and a shared dashboard provisioned from `grafana/provisioning/`

## Architecture

```text
[Data Generator] --MQTT--> [Mosquitto Broker]
                              |
                +-------------+-------------+
                |                           |
                v                           v
           [Node-RED]               [Alert Manager]
        (raw temperature data)      (anomaly detection)
                |                           |
                v                           v
   [PostgreSQL: temperature_data] [PostgreSQL: temperature_alerts]
                                                |
                                                v
                                         [Alert API]
                                                |
                                                v
                                            [Grafana]
```

## Repository Layout

```text
p2506-network/
|-- docker-compose.yaml
|-- .env.example
|-- CONTRIBUTING.md
|-- docs/
|   `-- SHARING.md
|-- mosquitto/
|   `-- config/mosquitto.conf
|-- postgres/
|   `-- init/01-schema.sql
|-- data-generator/          # source for published data-generator image
|-- alert-manager/           # source for published alert-manager image
|-- alert-api/               # source for published alert-api image
|-- node-red/
|   `-- data/
|       |-- flows.json
|       |-- package.json
|       |-- package-lock.json
|       `-- settings.js
`-- grafana/
    |-- provisioning/
    |   |-- dashboards/
    |   `-- datasources/
    `-- data/                # local runtime state, ignored from git
```

## Quick Start

### Prerequisites

- Docker Desktop or Docker Engine with Compose v2
- Around 2 GB free RAM

### Setup

1. Copy `.env.example` to `.env`
2. Start the stack

```bash
docker-compose up -d
```

3. Check status

```bash
docker-compose ps
```

4. Open the services

- Grafana: `http://localhost:3000`
- Node-RED: `http://localhost:1880`
- Alert API health check: `http://localhost:5000/health`

## Services and Ports

| Service | Port | URL |
|---|---:|---|
| Mosquitto MQTT | 1883 | `mqtt://localhost:1883` |
| PostgreSQL | 5432 | `localhost:5432` |
| Node-RED | 1880 | `http://localhost:1880` |
| Alert API | 5000 | `http://localhost:5000` |
| Grafana | 3000 | `http://localhost:3000` |

## Default Credentials

- Grafana username: `admin`
- Grafana password: `admin`
- PostgreSQL password: `qwerty`
- PostgreSQL user: `postgres`

Change them in `.env` when needed.

## Time Zone Standard

All services are configured to use `Asia/Kolkata` (IST, UTC+05:30).

## Shared vs Local State

### Shareable Source of Truth

- `docker-compose.yaml`
- `postgres/init/01-schema.sql`
- `node-red/data/flows.json`
- `node-red/data/settings.js`
- `node-red/data/package.json`
- `node-red/data/package-lock.json`
- `grafana/provisioning/`
- source code inside `alert-api/`, `alert-manager/`, and `data-generator/`

### Local Runtime State

- `.env`
- `node-red/data/flows_cred.json`
- `node-red/data/node_modules/`
- `grafana/data/`

Do not use local runtime state as the shareable version of the project.
If you clone the repo and use `.env.example`, the tracked Node-RED flow and Grafana provisioning files will recreate the same baseline setup on first boot.

## Grafana

- Shared Grafana assets live in `grafana/provisioning/`.
- The shared dashboard file is `grafana/provisioning/dashboards/api-postgres-dashboard.json`.
- The provisioning config keeps the dashboard file managed so contributors all start from the same PostgreSQL dashboard and datasource setup.
- If you want to update the shared dashboard, export the dashboard JSON and replace the provisioned file.

## Node-RED

- The tracked flow file is `node-red/data/flows.json`.
- It is preconfigured for MQTT ingestion and inserts into PostgreSQL `temperature_data`.
- Deploy from the Node-RED UI after edits so the file is updated.
- Credentials are intentionally not shared.

## Image Strategy

`alert-manager` and `alert-api` are run from published images in Compose.

- Current tags: `parilpaladiya/alert-manager:1.2` and `parilpaladiya/alert-api:1.3`
- `data-generator` still uses the published image.
- Rebuild and republish only when the service source changes.

Example:

```bash
docker build -t <registry>/alert-manager:<tag> ./alert-manager
docker build -t <registry>/alert-api:<tag> ./alert-api
docker build -t <registry>/data-generator:<tag> ./data-generator
```

## Useful Commands

```bash
docker-compose up -d
docker-compose ps
docker-compose logs -f
docker-compose logs -f grafana
docker-compose logs -f nodered
docker-compose restart grafana
docker-compose restart nodered
docker-compose down
docker-compose down -v
```

## API Examples

```bash
curl http://localhost:5000/alert/D001
curl http://localhost:5000/alert/D002
curl http://localhost:5000/alert/D003
curl http://localhost:5000/health
```

## Troubleshooting

| Problem | Fix |
|---|---|
| PostgreSQL not ready errors | Wait for the PostgreSQL healthcheck; dependent services retry automatically |
| Node-RED cannot connect to PostgreSQL | Check host `postgres`, port `5432`, database `sensor_db`, and configured credentials |
| Contributors do not see the shared dashboard | Restart Grafana and verify the dashboard JSON in `grafana/provisioning/dashboards/` |
| Port already in use | Change the host-side port in `docker-compose.yaml` |

## Contributor Docs

- Setup and workflow: `CONTRIBUTING.md`
- Repo handoff guidance: `docs/SHARING.md`
