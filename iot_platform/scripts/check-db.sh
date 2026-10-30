#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose exec -T database psql -U iot -d industrial_iot -c "SELECT machine_id, source, count(*) AS samples, max(time) AS last_sample FROM telemetry GROUP BY machine_id, source ORDER BY machine_id, source;"
