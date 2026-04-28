import json
import random
import ssl
import time

import paho.mqtt.client as mqtt


class MqttPublisher:
    def __init__(self, settings: dict, logger):
        self.settings = settings
        self.logger = logger
        self.client = mqtt.Client(client_id=settings["env"]["MQTT_CLIENT_ID"], clean_session=True)

        username = settings["env"]["MQTT_USERNAME"]
        password = settings["env"]["MQTT_PASSWORD"]
        if username:
            self.client.username_pw_set(username, password)

        if settings["env"]["MQTT_TLS_ENABLED"]:
            self.client.tls_set(
                ca_certs=settings["env"]["MQTT_TLS_CA_CERT"] or None,
                certfile=settings["env"]["MQTT_TLS_CLIENT_CERT"] or None,
                keyfile=settings["env"]["MQTT_TLS_CLIENT_KEY"] or None,
                cert_reqs=ssl.CERT_NONE if settings["env"]["MQTT_TLS_INSECURE"] else ssl.CERT_REQUIRED,
            )
            self.client.tls_insecure_set(settings["env"]["MQTT_TLS_INSECURE"])

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

        self._connect_with_retry()
        self.client.loop_start()

    def _on_connect(self, client, userdata, flags, rc):
        self.logger.info("MQTT connected", extra={"event": "mqtt_connect"})

    def _on_disconnect(self, client, userdata, rc):
        self.logger.warning("MQTT disconnected", extra={"event": "mqtt_disconnect"})

    def _connect_with_retry(self):
        initial = self.settings["env"]["MQTT_RECONNECT_INITIAL_DELAY"]
        max_delay = self.settings["env"]["MQTT_RECONNECT_MAX_DELAY"]
        delay = initial

        while True:
            try:
                self.client.connect(
                    host=self.settings["env"]["MQTT_HOST"],
                    port=self.settings["env"]["MQTT_PORT"],
                    keepalive=60,
                )
                return
            except Exception as exc:
                self.logger.warning(
                    f"MQTT connect failed: {exc}",
                    extra={"event": "mqtt_connect_retry"},
                )
                time.sleep(delay + random.uniform(0, 1))
                delay = min(delay * 2, max_delay)

    def publish(self, topic: str, payload: dict):
        result = self.client.publish(
            topic,
            json.dumps(payload),
            qos=self.settings["env"]["MQTT_QOS"],
            retain=self.settings["env"]["MQTT_RETAIN"],
        )
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError(f"MQTT publish failed with code {result.rc}")
