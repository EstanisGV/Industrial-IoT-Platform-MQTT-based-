import argparse
import shutil
from pathlib import Path
import sys
import yaml

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.inventory_loader import get_machine, get_enabled_machines, load_environment, load_tag_profile
from utils.secret_store import FileSecretStore
from utils.topic_builder import build_topics
from validation.validate_inventory import validate_inventory


BASE_PATH = Path(__file__).resolve().parents[2]
GENERATED_EDGES_DIR = BASE_PATH / "generated" / "edges"
EDGE_TEMPLATE_COMPOSE = BASE_PATH / "edge-rpi-v2" / "templates" / "docker-compose.edge.template.yml"


def render_env(machine: dict, env_cfg: dict, secret: dict) -> str:
    mqtt_cfg = env_cfg["mqtt"]
    return "\\n".join(
        [
            f"APP_ENV={env_cfg['environment']}",
            f"PLC_PROTOCOL={machine.get('protocol', 'mock')}",
            f"PLC_IP={machine.get('plc_ip', '192.168.1.60')}",
            f"PLC_RACK={machine.get('plc_rack', 0)}",
            f"PLC_SLOT={machine.get('plc_slot', 1)}",
            f"PLC_DB_NUMBER={machine.get('plc_db_number', 100)}",
            f"OPCUA_URL={machine.get('opcua_url', '')}",
            f"OPCUA_USERNAME={machine.get('opcua_username', '')}",
            f"OPCUA_PASSWORD={machine.get('opcua_password', '')}",
            f"MQTT_HOST={mqtt_cfg['host']}",
            f"MQTT_PORT={mqtt_cfg['port']}",
            f"MQTT_USERNAME={secret['MQTT_USERNAME']}",
            f"MQTT_PASSWORD={secret['MQTT_PASSWORD']}",
            f"MQTT_CLIENT_ID=edge-{machine['machine_id']}",
            "MQTT_QOS=1",
            "MQTT_RETAIN=false",
            "MQTT_CONNECT_TIMEOUT=10",
            "MQTT_RECONNECT_INITIAL_DELAY=2",
            "MQTT_RECONNECT_MAX_DELAY=60",
            f"MQTT_TLS_ENABLED={str(mqtt_cfg.get('tls_enabled', False)).lower()}",
            f"MQTT_TLS_CA_CERT={mqtt_cfg.get('ca_cert_path', '/app/certs/ca.crt')}",
            "MQTT_TLS_CLIENT_CERT=",
            "MQTT_TLS_CLIENT_KEY=",
            "MQTT_TLS_INSECURE=false",
            f"POLL_INTERVAL_SECONDS={env_cfg['polling']['interval_seconds']}",
            f"HEARTBEAT_INTERVAL_SECONDS={env_cfg['heartbeat']['interval_seconds']}",
            f"LOG_LEVEL={env_cfg['logging']['level']}",
            "SERVICE_VERSION=0.2.0",
            "",
        ]
    )


def render_machine_info(machine: dict) -> dict:
    return {
        "machine": {
            "machine_id": machine["machine_id"],
            "plant": machine["plant"],
            "area": machine.get("area", ""),
            "line": machine.get("line", ""),
            "controller": machine.get("controller", ""),
            "config_version": "1.0.0",
            "topics": build_topics(machine),
        }
    }


def render(machine_id: str, environment: str):
    validate_inventory()
    machine = get_machine(machine_id)
    env_cfg = load_environment(environment)
    tag_profile = load_tag_profile(machine["tag_profile"])

    store = FileSecretStore(environment)
    secret = store.read_mqtt_secret(machine_id)
    if not secret:
        raise SystemExit(
            f"Missing MQTT secret for {machine_id}. "
            f"Run: python scripts/provisioning/provision_mqtt_identities.py --env {environment}"
        )

    out_dir = GENERATED_EDGES_DIR / machine_id
    config_dir = out_dir / "plc-collector" / "config"
    certs_dir = out_dir / "plc-collector" / "certs"
    logs_dir = out_dir / "plc-collector" / "logs"

    config_dir.mkdir(parents=True, exist_ok=True)
    certs_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / ".env").write_text(render_env(machine, env_cfg, secret), encoding="utf-8")
    shutil.copyfile(EDGE_TEMPLATE_COMPOSE, out_dir / "docker-compose.yml")

    (config_dir / "machine_info.yaml").write_text(
        yaml.safe_dump(render_machine_info(machine), sort_keys=False),
        encoding="utf-8",
    )
    (config_dir / "machine_tags.yaml").write_text(
        yaml.safe_dump(tag_profile, sort_keys=False),
        encoding="utf-8",
    )

    (certs_dir / ".gitkeep").write_text("", encoding="utf-8")
    (logs_dir / ".gitkeep").write_text("", encoding="utf-8")

    backend_ca_cert = BASE_PATH / "backend_server" / "mosquitto" / "config" / "certs" / "ca.crt"

    if env_cfg["mqtt"].get("tls_enabled", False):
        if not backend_ca_cert.exists():
            raise SystemExit(
                f"Missing CA certificate: {backend_ca_cert}\n"
                "Generate TLS certificates before rendering edge config."
            )

        shutil.copyfile(backend_ca_cert, certs_dir / "ca.crt")
    else:
        (certs_dir / ".gitkeep").write_text("", encoding="utf-8")

    print(f"[OK] Edge config rendered: {out_dir}")


def main():
    parser = argparse.ArgumentParser(description="Render per-machine edge config.")
    parser.add_argument("--env", default="dev", choices=["dev", "prod"])

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--machine")
    group.add_argument("--all", action="store_true")

    args = parser.parse_args()

    if args.all:
        validate_inventory()
        for machine in get_enabled_machines():
            render(machine["machine_id"], args.env)
    else:
        render(args.machine, args.env)


if __name__ == "__main__":
    main()
