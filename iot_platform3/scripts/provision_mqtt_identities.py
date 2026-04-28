import argparse
import secrets
import subprocess
from pathlib import Path

import yaml

BASE_PATH = Path(__file__).resolve().parents[1]
INVENTORY_FILE = BASE_PATH / "inventory" / "machines.yaml"
SECRETS_DIR = BASE_PATH / "backend_server" / "secrets" / "mqtt"
PASSWORD_FILE = BASE_PATH / "backend_server" / "mosquitto" / "config" / "passwords"


def load_inventory() -> dict:
    with INVENTORY_FILE.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def generate_password() -> str:
    return secrets.token_urlsafe(24)


def secret_file_for(machine_id: str) -> Path:
    return SECRETS_DIR / f"{machine_id}.env"


def read_existing_secret(machine_id: str):
    path = secret_file_for(machine_id)
    if not path.exists():
        return None

    data = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            data[k.strip()] = v.strip()
    return data


def write_secret(machine_id: str, password: str):
    path = secret_file_for(machine_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"MQTT_USERNAME={machine_id}\nMQTT_PASSWORD={password}\n",
        encoding="utf-8",
    )


def upsert_password_file(machine_id: str, password: str):
    PASSWORD_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not PASSWORD_FILE.exists():
        PASSWORD_FILE.write_text("", encoding="utf-8")

    # mosquitto_passwd -b works as upsert.
    subprocess.run(
        ["mosquitto_passwd", "-b", str(PASSWORD_FILE), machine_id, password],
        check=True,
    )


def provision_machine(machine: dict, rotate: bool = False):
    machine_id = machine["machine_id"]

    existing = read_existing_secret(machine_id)
    if existing and not rotate:
        print(f"[SKIP] {machine_id}: existing credentials reused")
        return False

    password = generate_password()
    write_secret(machine_id, password)
    upsert_password_file(machine_id, password)

    if rotate:
        print(f"[ROTATE] {machine_id}: credentials rotated")
    else:
        print(f"[CREATE] {machine_id}: credentials created")

    return True


def main():
    parser = argparse.ArgumentParser(description="Provision MQTT identities idempotently.")
    parser.add_argument("--rotate", help="Rotate credentials for one machine_id")
    args = parser.parse_args()

    inventory = load_inventory()
    machines = [m for m in inventory.get("machines", []) if m.get("enabled", True)]

    if args.rotate:
        matching = [m for m in machines if m["machine_id"] == args.rotate]
        if not matching:
            raise SystemExit(f"Machine not found in inventory: {args.rotate}")
        provision_machine(matching[0], rotate=True)
        return

    created = 0
    reused = 0
    for machine in machines:
        changed = provision_machine(machine, rotate=False)
        if changed:
            created += 1
        else:
            reused += 1

    print(f"\nDone. created={created}, reused={reused}")


if __name__ == "__main__":
    main()
