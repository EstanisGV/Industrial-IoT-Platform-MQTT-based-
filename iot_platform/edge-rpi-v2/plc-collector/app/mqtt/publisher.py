import json
import ssl
import time
import threading
import paho.mqtt.client as mqtt


class MqttPublisher:
    def __init__(self, settings: dict, logger):
        self.settings = settings
        self.logger = logger
        env = settings["env"]

        self.host = env["MQTT_HOST"]
        self.port = env["MQTT_PORT"]
        self.username = env["MQTT_USERNAME"]
        self.password = env["MQTT_PASSWORD"]
        self.client_id = env["MQTT_CLIENT_ID"]
        self.qos = env["MQTT_QOS"]
        self.retain = env["MQTT_RETAIN"]
        self.connect_timeout = env["MQTT_CONNECT_TIMEOUT"]
        self.reconnect_initial_delay = env["MQTT_RECONNECT_INITIAL_DELAY"]
        self.reconnect_max_delay = env["MQTT_RECONNECT_MAX_DELAY"]

        self.tls_enabled = env["MQTT_TLS_ENABLED"]
        self.tls_ca_cert = env["MQTT_TLS_CA_CERT"]
        self.tls_client_cert = env["MQTT_TLS_CLIENT_CERT"]
        self.tls_client_key = env["MQTT_TLS_CLIENT_KEY"]
        self.tls_insecure = env["MQTT_TLS_INSECURE"]

        self._connected = False
        self._connect_lock = threading.Lock()

        self.client = mqtt.Client(client_id=self.client_id, clean_session=True)

        if self.username:
            self.client.username_pw_set(self.username, self.password)

        if self.tls_enabled:
            self.client.tls_set(
                ca_certs=self.tls_ca_cert or None,
                certfile=self.tls_client_cert or None,
                keyfile=self.tls_client_key or None,
                tls_version=ssl.PROTOCOL_TLS_CLIENT,
            )
            self.client.tls_insecure_set(self.tls_insecure)

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

        self.client.loop_start()
        self._connect_with_retry()

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._connected = True
            self.logger.info(
                "Connected to MQTT broker",
                extra={"event": "mqtt_connected", "broker": f"{self.host}:{self.port}"},
            )
        else:
            self._connected = False
            self.logger.error(
                f"MQTT connect failed with rc={rc}",
                extra={"event": "mqtt_connect_failed"},
            )

    def _on_disconnect(self, client, userdata, rc):
        self._connected = False
        self.logger.warning(
            f"Disconnected from MQTT broker rc={rc}",
            extra={"event": "mqtt_disconnected"},
        )

    def _connect_with_retry(self):
        delay = self.reconnect_initial_delay

        while not self._connected:
            try:
                with self._connect_lock:
                    self.logger.info(
                        "Trying MQTT connection",
                        extra={"event": "mqtt_connect_attempt", "broker": f"{self.host}:{self.port}"},
                    )
                    self.client.connect(self.host, self.port, self.connect_timeout)
                    time.sleep(1.0)
                    if self._connected:
                        break
            except Exception as exc:
                self.logger.error(
                    f"MQTT connection error: {exc}",
                    extra={"event": "mqtt_connect_exception"},
                )

            self.logger.info(
                f"Retrying MQTT connection in {delay}s",
                extra={"event": "mqtt_reconnect_wait"},
            )
            time.sleep(delay)
            delay = min(delay * 2, self.reconnect_max_delay)

    def _ensure_connected(self):
        if not self._connected:
            self._connect_with_retry()

    def publish(self, topic: str, payload: dict) -> None:
        self._ensure_connected()
        message = json.dumps(payload)
        result = self.client.publish(topic, message, qos=self.qos, retain=self.retain)
        result.wait_for_publish()

        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            self.logger.error(
                f"Failed to publish to topic={topic}, rc={result.rc}",
                extra={"event": "mqtt_publish_failed"},
            )
            raise RuntimeError(f"MQTT publish failed with rc={result.rc}")

        self.logger.info(
            f"Published MQTT message to {topic}",
            extra={"event": "mqtt_publish_ok"},
        )
