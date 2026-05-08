#!/usr/bin/env sh
set -eu

SA_PASSWORD="${SA_PASSWORD:-StrongPassword123}"
DB_NAME="${DB_NAME:-pension_ai}"
SQLSERVER_HOST="${SQLSERVER_HOST:-sqlserver}"
SQLCMD_IMAGE="${SQLCMD_IMAGE:-mcr.microsoft.com/mssql-tools}"
COMPOSE_NETWORK="${COMPOSE_NETWORK:-pension-ai_default}"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"

run_sqlcmd() {
  docker run --rm --platform linux/amd64 --network "$COMPOSE_NETWORK" "$SQLCMD_IMAGE" \
    /opt/mssql-tools/bin/sqlcmd \
    -S "$SQLSERVER_HOST,1433" \
    -U sa \
    -P "$SA_PASSWORD" \
    "$@"
}

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker er ikke installeret eller findes ikke i PATH."
  exit 1
fi

echo "Starter SQL Server container..."
docker compose -f "$PROJECT_ROOT/docker-compose.yml" up -d sqlserver

echo "Venter på at SQL Server er klar..."
until run_sqlcmd -Q "SELECT 1" >/dev/null 2>&1; do
  sleep 2
done

echo "Opretter database $DB_NAME hvis den ikke findes..."
run_sqlcmd -Q "IF DB_ID('$DB_NAME') IS NULL CREATE DATABASE [$DB_NAME];"

echo "Kører schema.sql..."
docker run --rm --platform linux/amd64 --network "$COMPOSE_NETWORK" \
  -v "$SCRIPT_DIR:/sql" \
  "$SQLCMD_IMAGE" \
  /opt/mssql-tools/bin/sqlcmd \
  -S "$SQLSERVER_HOST,1433" \
  -U sa \
  -P "$SA_PASSWORD" \
  -d "$DB_NAME" \
  -i /sql/schema.sql

echo "Kører seed.sql..."
docker run --rm --platform linux/amd64 --network "$COMPOSE_NETWORK" \
  -v "$SCRIPT_DIR:/sql" \
  "$SQLCMD_IMAGE" \
  /opt/mssql-tools/bin/sqlcmd \
  -S "$SQLSERVER_HOST,1433" \
  -U sa \
  -P "$SA_PASSWORD" \
  -d "$DB_NAME" \
  -i /sql/seed.sql

echo "Database er klar."
