import argparse
from pathlib import Path
import subprocess
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.inventory_loader import get_enabled_machines
from utils.secret_store import FileSecretStore

BASE_PATH = Path(__file__).resolve().parents[2]
PASSWORD_FILE = BASE_PATH / "backend_server" / "mosquitto" / "config" / "passwords"


def upsert_password_file(username: str, password: str):
    """
    Uses mosquitto_passwd to store a hash in Mosquitto password_file.
    Requires mosquitto_passwd installed on the host running this script.
    """
    PASSWORD_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not PASSWORD_FILE.exists():
        PASSWORD_FILE.write_text("", encoding="utf-8")

    subprocess.run(
        ["mosquitto_passwd", "-b", str(PASSWORD_FILE), username, password],
        check=True,
    )


def provision(environment: str, rotate: str | None):
    store = FileSecretStore(environment)
    machines = get_enabled_machines()

    created = 0
    reused = 0
    rotated = 0

    for machine in machines:
        machine_id = machine["machine_id"]
        username = machine_id

        if rotate and rotate != machine_id:
            continue

        existing = store.read_mqtt_secret(username)

        if existing and not rotate:
            print(f"[SKIP] {machine_id}: credentials already exist")
            reused += 1
            continue

        password = store.generate_password()
        store.write_mqtt_secret(username, password)
        upsert_password_file(username, password)

        if rotate:
            print(f"[ROTATE] {machine_id}: credentials rotated")
            rotated += 1
        else:
            print(f"[CREATE] {machine_id}: credentials created")
            created += 1

    print(f"Done. created={created}, reused={reused}, rotated={rotated}")


def main():
    parser = argparse.ArgumentParser(description="Provision MQTT identities idempotently.")
    parser.add_argument("--env", default="dev", choices=["dev", "prod"])
    parser.add_argument("--rotate", help="Rotate credentials for one machine_id")
    args = parser.parse_args()
    provision(environment=args.env, rotate=args.rotate)


if __name__ == "__main__":
    main()
