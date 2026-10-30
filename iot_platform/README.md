# Industrial IoT – OPC UA → TimescaleDB (without MQTT)

This is a **NEW, separate prototype**. It does not overwrite the previous MQTT repository. It is designed for your existing Hyper-V VM (`iot-server`, Ubuntu Server 26.04) and its dedicated ext4 volume at `/srv/iot-data`.

## Architecture

INDEX / other OPC UA server → asynchronous Python collector → SQLite durable spool → TimescaleDB (PostgreSQL 17). All components run on **one Ubuntu VM** using Docker Compose. MQTT and Raspberry Pi are **not involved**.

- Multiple machines are configured in `config/machines.yaml` and profiles in `config/profiles/`.
- Each machine has its own poll interval and independent reconnection loop. One collector container manages all enabled machines. Scale out to multiple collector instances only after assigning each a *disjoint* set of machine IDs.
- One snapshot row contains timestamp, machine ID, UUID sample ID, source (`mock` or `opcua`), and a JSONB map of variables.
- Failed database inserts remain in a SQLite WAL spool on the 250 GB data volume; ingestion is idempotent based on composite primary key.
- TimescaleDB uses a hypertable. No external PostgreSQL port is published.
- No OPC UA writes are implemented. The real device must provide endpoint, valid NodeIds, security policy, user/certificates as appropriate.

## IMPORTANT – before installing

- This prototype has **NOT been exercised on the real Siemens INDEX**. The NodeIds in the profiles are **placeholders** and are not real Siemens node identifiers. Current inventory enables **mock only**.
- Verify `scripts/prepare-host.sh` `EXPECTED_UUID` against `sudo blkid /dev/sdb1`. If the server differs, replace it with the real UUID. The script prevents starting the service against an unmounted data directory; Docker bind mounts also refuse to auto-create it.
- IT must authorize routing/firewall access to the CNC and restrict VM egress to approved OPC UA endpoints. Do not bridge corporate and industrial networks casually.
- The `.env` password is passed to containers by Compose (visible to privileged Docker admins). Protect the VM, its files and Docker access; migrate to a secret store for production.
- This is a **development/validation baseline**, not an HA or fully security-hardened production deployment. Add monitoring, data retention, backups outside the VHDX, certificate trust management, audit logs and integration tests prior to production.

## Install (in Ubuntu)

Copy/extract the folder to `/opt/opcua-direct-platform`. Then:

```bash
cd /opt/opcua-direct-platform
sudo blkid /dev/sdb1
sudo bash scripts/prepare-host.sh
cp .env.example .env
python3 -c 'import secrets; print(secrets.token_urlsafe(36))'
# Edit .env, replace DB_PASSWORD with that generated string:
nano .env
chmod 600 .env
sudo docker compose config --quiet
sudo docker compose up -d --build
sudo docker compose ps
sudo docker compose logs -f collector
```

To inspect data:

```bash
sudo docker compose exec -T database psql -U iot -d industrial_iot -c 'SELECT machine_id, count(*) FROM telemetry GROUP BY machine_id;'
```

### IMPORTANT ownership note
TimescaleDB entrypoint initializes the directory ownership when its entrypoint runs as root. The collector runs as UID 10001, group 100, so the `spool` folder is prepared with those permissions by `prepare-host.sh`.

### Next: real OPC UA
1. Obtain the authorized OPC UA endpoint and browse the actual NodeIds on SINUMERIK (e.g. UaExpert), together with maintenance/IT.
2. Replace the placeholder NodeIds in `config/profiles/ms22_demo.yaml` (prefer a newly named production profile).
3. Install the client certificate/key in `secrets/` when applicable, protect them, and configure trust on CNC according to Siemens instructions.
4. Change `mode: opcua`, set `endpoint`, `security` (asyncua security-string syntax), and optional `username_env`/`password_env` with environment variables supplied to the container securely. For a real deployment, configure a dedicated restricted read-only account.
5. `sudo docker compose up -d --build --force-recreate collector` and examine logs. Perform only authorized, read-only network tests.

### Adding machines
Add another unique entry to `config/machines.yaml` and a variables file to `config/profiles/`; set `enabled: true`. Restart the collector. Machines are managed as separate asyncio tasks with independent reconnect behavior.

### Operational limitations
- This version polls instead of OPC UA subscriptions, at the configured interval (10 seconds default).
- TimescaleDB only initializes `db/001_schema.sql` on first creation of an empty database. Use versioned migrations thereafter.
- No automatic schema migrations, bounded spool quota, or remote alerts yet. Monitor free space. A full disk prevents new readings from being queued.
- Reusing the same `machine_id` across separate collectors may make timing and analysis ambiguous; treat each ID as unique.
- Disable live polling when maintenance has not authorized it. Time-series rows are not labeled anomalies/failures.
- Preserve `.env` when re-deploying. Never run `docker compose down -v` or delete the VHDX to update code.

## File reference

| File | Responsibility |
| --- | --- |
| `compose.yaml` | Private Docker networks, DB container, collector container, persistent VHDX bind mounts, healthcheck |
| `Dockerfile`, `requirements.txt` | Collector Python runtime and dependencies |
| `config/machines.yaml` | Device inventory, enablement, polling interval, mode, connection parameters |
| `config/profiles/*.yaml` | Per-device tag names, OPC UA NodeIds, mock generation fields |
| `app/config.py` | Strong config validation and placeholder rejection in real mode |
| `app/reader.py` | Read-only OPC UA client, simulated reader, connection lifecycle |
| `app/spool.py` | Durable SQLite WAL queue (retries, local buffering) |
| `app/main.py` | Orchestrate collectors, DB inserts, retry, clean shutdown |
| `db/001_schema.sql` | TimescaleDB hypertable and indexes |
| `scripts/prepare-host.sh` | Check volume UUID before startup; create durable directories |
| `scripts/check-db.sh` | Quick stored record counts |
| `tests/test_config.py` | Lightweight inventory test |
| `.env.example`, `.gitignore` | Local DB password template and avoid committing secrets |
