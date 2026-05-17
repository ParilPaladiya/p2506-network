#!/bin/bash
set -euo pipefail

echo "Running MySQL grant bootstrap..."

if [[ -z "${MYSQL_ROOT_PASSWORD:-}" || -z "${MYSQL_DATABASE:-}" || -z "${MYSQL_USER:-}" ]]; then
  echo "Skipping grants because MYSQL_ROOT_PASSWORD, MYSQL_DATABASE, or MYSQL_USER is missing."
  exit 0
fi

if [[ "${MYSQL_USER}" == "root" ]]; then
  echo "MYSQL_USER is root; skipping additional user/grant setup for the current single-user model."
  exit 0
fi

mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" <<EOSQL
CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_ROOT_PASSWORD}';
GRANT ALL PRIVILEGES ON \`${MYSQL_DATABASE}\`.* TO '${MYSQL_USER}'@'%';
FLUSH PRIVILEGES;
EOSQL

echo "MySQL grant bootstrap completed for user '${MYSQL_USER}'."
