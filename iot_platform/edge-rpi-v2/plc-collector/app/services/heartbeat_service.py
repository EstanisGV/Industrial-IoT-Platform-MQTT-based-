import threading
import time
import uuid
from datetime import datetime, timezone


class HeartbeatService:
    def __init__(self, settings: dict, publisher, logger):
        self.settings = settings
        self.publisher = publisher
        self.logger = logger
        self._thread = None
        self._running = False

    def _loop(self):
        machine = self.settings["machine"]
        heartbeat_topic = machine["topics"]["heartbeat"]

        while self._running:
            try:
                payload = {
                    "schema_version": "1.0",
                    "message_id": str(uuid.uuid4()),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "machine_id": machine["machine_id"],
                    "plant": machine["plant"],
                    "status": "alive",
                    "service_version": self.settings["env"]["SERVICE_VERSION"],
                }

                self.publisher.publish(heartbeat_topic, payload, wait=False)
                self.logger.info("Heartbeat published", extra={"event": "heartbeat_publish"})

            except Exception as exc:
                self.logger.exception(
                    f"Heartbeat publish failed: {exc}",
                    extra={"event": "heartbeat_publish_error"},
                )

            time.sleep(self.settings["env"]["HEARTBEAT_INTERVAL_SECONDS"])

    def start(self):
        if self._thread:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
