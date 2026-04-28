import argparse
from pathlib import Path
import yaml

BASE_PATH = Path(__file__).resolve().parents[1]
INVENTORY_FILE = BASE_PATH / "inventory" / "machines.yaml"
TAG_PROFILES_DIR = BASE_PATH / "inventory" / "tag_profiles"
SECRETS_DIR = BASE_PATH / "backend_server" / "secrets" / "mqtt"
GENERATED_DIR = BASE_PATH / "generated"
EDGE_DIR = BASE_PATH / "edge-rpi-v2"


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_inventory():
    return load_yaml(INVENTORY_FILE) or {}


def load_secret(machine_id: str) -> dict:
    path = SECRETS_DIR / f"{machine_id}.env"
    if not path.exists():
        raise FileNotFoundError(f"Missing MQTT secret for machine {machine_id}: {path}")
    data = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            data[k.strip()] = v.strip()
    return data


def build_machine_info(machine: dict) -> dict:
    machine_id = machine["machine_id"]
    plant = machine["plant"]
    return {
        "machine": {
            "machine_id": machine_id,
            "plant": plant,
            "area": machine.get("area", ""),
            "line": machine.get("line", ""),
            "controller": machine.get("controller", ""),
            "config_version": "1.0.0",
            "topics": {
                "telemetry": f"factory/{plant}/{machine_id}/telemetry",
                "heartbeat": f"factory/{plant}/{machine_id}/heartbeat",
                "status": f"factory/{plant}/{machine_id}/status",
            },
        }
    }


def build_env(machine: dict, secret: dict) -> str:
    machine_id = machine["machine_id"]
    lines = [
        "APP_ENV=development",
        f"PLC_PROTOCOL={machine.get('protocol', 'mock')}",
        "PLC_IP=192.168.1.60",
        "PLC_RACK=0",
        "PLC_SLOT=1",
        "PLC_DB_NUMBER=100",
        "OPCUA_URL=opc.tcp://192.168.1.50:4840",
        "OPCUA_USERNAME=",
        "OPCUA_PASSWORD=",
        "MQTT_HOST=192.168.1.100",
        "MQTT_PORT=1883",
        f"MQTT_USERNAME={secret['MQTT_USERNAME']}",
        f"MQTT_PASSWORD={secret['MQTT_PASSWORD']}",
        f"MQTT_CLIENT_ID=edge-{machine_id}",
        "MQTT_QOS=1",
        "MQTT_RETAIN=false",
        "MQTT_CONNECT_TIMEOUT=10",
        "MQTT_RECONNECT_INITIAL_DELAY=2",
        "MQTT_RECONNECT_MAX_DELAY=60",
        "MQTT_TLS_ENABLED=false",
        "MQTT_TLS_CA_CERT=/app/certs/ca.crt",
        "MQTT_TLS_CLIENT_CERT=/app/certs/client.crt",
        "MQTT_TLS_CLIENT_KEY=/app/certs/client.key",
        "MQTT_TLS_INSECURE=false",
        "POLL_INTERVAL_SECONDS=2",
        "HEARTBEAT_INTERVAL_SECONDS=30",
        "LOG_LEVEL=INFO",
        "SERVICE_VERSION=0.2.0",
    ]
    return "\n".join(lines) + "\n"


def render_machine(machine_id: str):
    inventory = load_inventory()
    machines = inventory.get("machines", [])
    matching = [m for m in machines if m["machine_id"] == machine_id and m.get("enabled", True)]
    if not matching:
        raise SystemExit(f"Machine not found or disabled: {machine_id}")

    machine = matching[0]
    secret = load_secret(machine_id)
    tag_profile = load_yaml(TAG_PROFILES_DIR / f"{machine['tag_profile']}.yaml")

    out = GENERATED_DIR / machine_id
    out.mkdir(parents=True, exist_ok=True)

    (out / ".env").write_text(build_env(machine, secret), encoding="utf-8")
    (out / "machine_info.yaml").write_text(
        yaml.safe_dump(build_machine_info(machine), sort_keys=False),
        encoding="utf-8",
    )
    (out / "machine_tags.yaml").write_text(
        yaml.safe_dump(tag_profile, sort_keys=False),
        encoding="utf-8",
    )
    (out / "docker-compose.yml").write_text(
        (EDGE_DIR / "docker-compose.yml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    print(f"[OK] Generated bundle for {machine_id} at {out}")


def main():
    parser = argparse.ArgumentParser(description="Render per-machine edge config.")
    parser.add_argument("--machine", required=True, help="machine_id to render")
    args = parser.parse_args()
    render_machine(args.machine)


if __name__ == "__main__":
    main()
