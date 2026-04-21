import time
from app.services.payload_builder import build_telemetry_payload, build_status_payload


class PollingService:
    def __init__(self, settings: dict, collector, publisher, logger):
        self.settings = settings
        self.collector = collector
        self.publisher = publisher
        self.logger = logger
        self.interval = settings["env"]["POLL_INTERVAL_SECONDS"]
        self.telemetry_topic = settings["machine"]["topics"]["telemetry"]
        self.status_topic = settings["machine"]["topics"]["status"]

    def run(self):
        self.logger.info(
            f"Polling started with interval={self.interval}s",
            extra={"event": "polling_started"},
        )
        self.publisher.publish(
            self.status_topic,
            build_status_payload(self.settings, "started", "collector service started"),
        )

        while True:
            try:
                data = self.collector.read()
                payload = build_telemetry_payload(self.settings, data)

                self.logger.info(
                    f"Collected data: {data}",
                    extra={"event": "telemetry_collected"},
                )
                self.publisher.publish(self.telemetry_topic, payload)

            except Exception as exc:
                self.logger.exception(
                    f"Error in polling loop: {exc}",
                    extra={"event": "polling_error"},
                )
                try:
                    self.publisher.publish(
                        self.status_topic,
                        build_status_payload(self.settings, "error", str(exc)),
                    )
                except Exception:
                    pass

            time.sleep(self.interval)
