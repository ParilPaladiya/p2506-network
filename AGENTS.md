# AI Agent Instructions for P2506-Network IoT Project

## Project Overview
This is a Docker Compose-based IoT sensor monitoring system simulating temperature data from devices D001-D003. It uses MQTT for messaging, PostgreSQL for storage, anomaly detection, a REST API, and Grafana for visualization.

See [README.md](README.md) for architecture diagram, services, and ports.

The `alert-manager`, `alert-api`, and `data-generator` folders are build sources for published Docker images. The current Compose file runs those services from image tags, not local bind-mounted code.

## Build and Run Commands
- Start all services: `docker-compose up -d`
- Check status: `docker-compose ps`
- View logs: `docker-compose logs -f` or `docker-compose logs -f <service>`
- Stop: `docker-compose stop`
- Start: `docker-compose start`
- Remove: `docker-compose down`
- Restart service: `docker-compose restart <service>`
- Rebuild/publish a Python service image from local source: `docker build -t <image>:<tag> ./alert-manager` (same pattern for `alert-api` and `data-generator`)

## Architecture Decisions
- MQTT broker (Mosquitto) for decoupled pub/sub communication.
- Dual data paths: Raw data via Node-RED to PostgreSQL, anomaly alerts via Alert Manager to PostgreSQL.
- Anomaly detection uses statistical methods (rolling window, standard deviation multiplier).
- PostgreSQL tables: `temperature_data` (raw), `temperature_alerts` (alerts with levels: NORMAL/WARNING/CRITICAL/ANOMALY).
- Alert API provides REST endpoints for querying alerts.
- Grafana auto-provisions PostgreSQL datasource and dashboards via files.

## Project Conventions
- Service names: Hyphenated (e.g., `alert-manager`).
- Environment variables: Prefixed by service (e.g., `MQTT_BROKER`), stored in `.env`.
- Networks: `p2506_network` bridge for inter-service communication.
- Volumes: Named for persistence (e.g., `postgres_data`), bind mounts for configs.
- Dependencies: Python services use `paho-mqtt` and `psycopg2-binary`; Node-RED adds PostgreSQL nodes.
- Code style: Python scripts with env var configs and retry loops; Node-RED flows parse JSON payloads.
- Runtime state under `node-red/data/node_modules`, `node-red/data/flows_cred.json`, and `grafana/data` is persistent local state, not intended for source control.
- Shareable Grafana assets belong under `grafana/provisioning/`; shareable Node-RED flow logic belongs in `node-red/data/flows.json` and `node-red/data/settings.js`.
- The shared Grafana dashboard is provisioned from `grafana/provisioning/dashboards/`; UI edits in Grafana do not automatically update the tracked provisioning files.

## Potential Pitfalls
- Wait for PostgreSQL healthcheck before accessing; services auto-retry.
- Ensure Mosquitto and PostgreSQL are healthy before starting dependent services.
- MQTT is anonymous; passwords hardcoded in configs (for example, the PostgreSQL password).
- Grafana requires plugins: `grafana-mqtt-datasource` and `marcusolsson-json-datasource`.
- API has no authentication.
- `docker-compose up -d --build` will not refresh published-image services unless their image tag changes or the image is rebuilt locally under the same tag.
- PostgreSQL init scripts under `postgres/init/` are bootstrap-only and run only on first initialization of the PostgreSQL data directory.

## Key Files and Directories
- `docker-compose.yaml`: Service definitions, dependencies, volumes.
- `postgres/init/01-schema.sql`: Database initialization.
- `data-generator/generator.py`: MQTT publisher with JSON payloads.
- `alert-manager/alert_manager.py`: MQTT subscriber with anomaly detection logic.
- `alert-api/alert_api.py`: Flask API for alert queries.
- `node-red/data/flows.json`: Flow definitions for raw data processing.
- `node-red/data/settings.js`: Node-RED runtime settings.
- `grafana/provisioning/`: Datasource and dashboard configs.
- `grafana/data/`: Local Grafana runtime state and plugins; persistent, but not intended for git.
- `mosquitto/config/mosquitto.conf`: Broker configuration.

For detailed setup, troubleshooting, and API docs, see [README.md](README.md).
