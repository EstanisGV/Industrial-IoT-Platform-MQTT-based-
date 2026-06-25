import time
import uuid
from datetime import datetime, timezone

class PollingService:
    def __init__(self, settings: dict, collector, publisher, logger):
        self.settings = settings
        self.collector = collector
        self.publisher = publisher
        self.logger = logger

    def run(self):
        machine = self.settings["machine"]
        telemetry_topic = machine["topics"]["telemetry"]
        status_topic = machine["topics"]["status"]
        consecutive_errors = 0
        while True:
            try:
                values = self.collector.read()
                ts = datetime.now(timezone.utc).isoformat()

                telemetry_payload = {
                    "schema_version": "1.0",
                    "message_id": str(uuid.uuid4()),
                    "timestamp": ts,
                    "machine_id": machine["machine_id"],
                    "plant": machine["plant"],
                    "area": machine.get("area"),
                    "line": machine.get("line"),
                    "values": values,
                }

                self.publisher.publish(telemetry_topic, telemetry_payload, wait=True)

                status_payload = {
                    "schema_version": "1.0",
                    "message_id": str(uuid.uuid4()),
                    "timestamp": ts,
                    "machine_id": machine["machine_id"],
                    "service_version": self.settings["env"]["SERVICE_VERSION"],
                    "status": "running",
                }

                self.publisher.publish(status_topic, status_payload, wait=False)

                self.logger.info(
                    "Telemetry published",
                    extra={"event": "telemetry_publish"},
                )
                consecutive_errors = 0

            except Exception as exc:
                consecutive_errors += 1
                self.logger.exception(
                    f"Polling loop error: {exc}",
                    extra={"event": "polling_error"},
                )

                try:
                    error_payload = {
                        "schema_version": "1.0",
                        "message_id": str(uuid.uuid4()),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "machine_id": machine["machine_id"],
                        "service_version": self.settings["env"]["SERVICE_VERSION"],
                        "status": "error",
                        "error_type": type(exc).__name__,
                        "error_message": str(exc),
                        "consecutive_errors": consecutive_errors,
                    }

                    self.publisher.publish(status_topic, error_payload, wait=False)
                    consecutive_errors = 0

                except Exception as publish_exc:
                    consecutive_errors += 1
                    self.logger.exception(
                        f"Failed to publish error status: {publish_exc}",
                        extra={"event": "status_publish_error"},
                    )

            time.sleep(self.settings["env"]["POLL_INTERVAL_SECONDS"])
