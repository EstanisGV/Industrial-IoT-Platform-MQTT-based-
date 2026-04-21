import threading
import time
from app.services.payload_builder import build_heartbeat_payload


class HeartbeatService:
    def __init__(self, settings: dict, publisher, logger):
        self.settings = settings
        self.publisher = publisher
        self.logger = logger
        self.interval = settings["env"]["HEARTBEAT_INTERVAL_SECONDS"]
        self.topic = settings["machine"]["topics"]["heartbeat"]
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self.logger.info(
            f"Heartbeat service started with interval={self.interval}s",
            extra={"event": "heartbeat_started"},
        )
        self._thread.start()

    def _run(self):
        while True:
            try:
                payload = build_heartbeat_payload(self.settings)
                self.publisher.publish(self.topic, payload)
                self.logger.info(
                    f"Heartbeat sent to {self.topic}",
                    extra={"event": "heartbeat_sent"},
                )
            except Exception as exc:
                self.logger.exception(
                    f"Heartbeat error: {exc}",
                    extra={"event": "heartbeat_error"},
                )
            time.sleep(self.interval)
