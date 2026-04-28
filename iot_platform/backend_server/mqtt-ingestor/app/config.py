import os
from dotenv import load_dotenv

def load_settings():
    load_dotenv()
    return {
        "mqtt_host": os.getenv("MQTT_HOST", "mosquitto"),
        "mqtt_port": int(os.getenv("MQTT_PORT", "1883")),
        "mqtt_username": os.getenv("MQTT_USERNAME", "mqtt-ingestor"),
        "mqtt_password": os.getenv("MQTT_PASSWORD", ""),
        "topic": os.getenv("MQTT_TOPIC", "factory/#"),
    }
