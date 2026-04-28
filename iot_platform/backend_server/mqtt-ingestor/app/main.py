import json
import paho.mqtt.client as mqtt

from app.config import load_settings

def on_connect(client, userdata, flags, rc):
    print(f"[mqtt-ingestor] connected rc={rc}")
    client.subscribe(userdata["topic"], qos=1)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except Exception:
        payload = {"raw": msg.payload.decode("utf-8", errors="replace")}
    print(f"[mqtt-ingestor] {msg.topic}: {payload}")

def main():
    settings = load_settings()
    client = mqtt.Client(userdata=settings)
    client.username_pw_set(settings["mqtt_username"], settings["mqtt_password"])
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(settings["mqtt_host"], settings["mqtt_port"], 60)
    client.loop_forever()

if __name__ == "__main__":
    main()
