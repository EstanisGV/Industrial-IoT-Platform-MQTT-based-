import time
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

        while True:
            values = self.collector.read()
            ts = datetime.now(timezone.utc).isoformat()

            telemetry_payload = {
                "timestamp": ts,
                "machine_id": machine["machine_id"],
                "plant": machine["plant"],
                "area": machine.get("area"),
                "line": machine.get("line"),
                "values": values,
            }
            self.publisher.publish(telemetry_topic, telemetry_payload)

            status_payload = {
                "timestamp": ts,
                "machine_id": machine["machine_id"],
                "service_version": self.settings["env"]["SERVICE_VERSION"],
                "status": "running",
            }
            self.publisher.publish(status_topic, status_payload)

            self.logger.info(
                "Telemetry published",
                extra={"event": "telemetry_publish"},
            )
            time.sleep(self.settings["env"]["POLL_INTERVAL_SECONDS"])
