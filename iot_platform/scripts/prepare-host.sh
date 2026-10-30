#!/usr/bin/env bash
set -euo pipefail
MOUNT=/srv/iot-data
EXPECTED_UUID="58f05d81-767d-47be-9600-bec075ab9d36"
ACTUAL="$(findmnt -n -o UUID --target "$MOUNT" || true)"
if [[ "$ACTUAL" != "$EXPECTED_UUID" ]]; then
  echo "ERROR: $MOUNT must be mounted from expected UUID $EXPECTED_UUID (got $ACTUAL)" >&2
  exit 1
fi
install -d -m 0750 /srv/iot-data/timescaledb
install -d -o 10001 -g 100 -m 0750 /srv/iot-data/spool
# Database image manages ownership on the Timescale directory at initialization.
echo "OK: confirmed mounted data volume and required directories"
