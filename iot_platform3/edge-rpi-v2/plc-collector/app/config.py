import os
import yaml
from dotenv import load_dotenv


def _load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _to_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def load_settings() -> dict:
    load_dotenv()

    machine_info = _load_yaml("/app/config/machine_info.yaml")
    machine_tags = _load_yaml("/app/config/machine_tags.yaml")

    return {
        "env": {
            "APP_ENV": os.getenv("APP_ENV", "development"),
            "PLC_PROTOCOL": os.getenv("PLC_PROTOCOL", "mock"),
            "PLC_IP": os.getenv("PLC_IP", ""),
            "PLC_RACK": int(os.getenv("PLC_RACK", "0")),
            "PLC_SLOT": int(os.getenv("PLC_SLOT", "1")),
            "PLC_DB_NUMBER": int(os.getenv("PLC_DB_NUMBER", "100")),
            "OPCUA_URL": os.getenv("OPCUA_URL", ""),
            "OPCUA_USERNAME": os.getenv("OPCUA_USERNAME", ""),
            "OPCUA_PASSWORD": os.getenv("OPCUA_PASSWORD", ""),
            "MQTT_HOST": os.getenv("MQTT_HOST", ""),
            "MQTT_PORT": int(os.getenv("MQTT_PORT", "1883")),
            "MQTT_USERNAME": os.getenv("MQTT_USERNAME", ""),
            "MQTT_PASSWORD": os.getenv("MQTT_PASSWORD", ""),
            "MQTT_CLIENT_ID": os.getenv("MQTT_CLIENT_ID", "plc-collector"),
            "MQTT_QOS": int(os.getenv("MQTT_QOS", "1")),
            "MQTT_RETAIN": _to_bool(os.getenv("MQTT_RETAIN"), False),
            "MQTT_CONNECT_TIMEOUT": int(os.getenv("MQTT_CONNECT_TIMEOUT", "10")),
            "MQTT_RECONNECT_INITIAL_DELAY": int(os.getenv("MQTT_RECONNECT_INITIAL_DELAY", "2")),
            "MQTT_RECONNECT_MAX_DELAY": int(os.getenv("MQTT_RECONNECT_MAX_DELAY", "60")),
            "MQTT_TLS_ENABLED": _to_bool(os.getenv("MQTT_TLS_ENABLED"), False),
            "MQTT_TLS_CA_CERT": os.getenv("MQTT_TLS_CA_CERT", ""),
            "MQTT_TLS_CLIENT_CERT": os.getenv("MQTT_TLS_CLIENT_CERT", ""),
            "MQTT_TLS_CLIENT_KEY": os.getenv("MQTT_TLS_CLIENT_KEY", ""),
            "MQTT_TLS_INSECURE": _to_bool(os.getenv("MQTT_TLS_INSECURE"), False),
            "POLL_INTERVAL_SECONDS": float(os.getenv("POLL_INTERVAL_SECONDS", "2")),
            "HEARTBEAT_INTERVAL_SECONDS": float(os.getenv("HEARTBEAT_INTERVAL_SECONDS", "30")),
            "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
            "SERVICE_VERSION": os.getenv("SERVICE_VERSION", "0.2.0"),
        },
        "machine": machine_info["machine"],
        "tags": [tag for tag in machine_tags["tags"] if tag.get("enabled", True)],
    }
