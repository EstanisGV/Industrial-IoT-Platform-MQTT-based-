CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE TABLE IF NOT EXISTS telemetry (
  time TIMESTAMPTZ NOT NULL,
  machine_id TEXT NOT NULL,
  sample_id UUID NOT NULL,
  source TEXT NOT NULL CHECK (source IN ('mock','opcua')),
  values_json JSONB NOT NULL,
  ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (time, machine_id, sample_id)
);
SELECT create_hypertable('telemetry','time',if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS telemetry_machine_time_idx ON telemetry (machine_id, time DESC);
