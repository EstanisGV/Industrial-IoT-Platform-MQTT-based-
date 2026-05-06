import argparse
import subprocess
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.inventory_loader import get_enabled_machines
from utils.secret_store import FileSecretStore
from validation.validate_inventory import validate_inventory

BASE_PATH = Path(__file__).resolve().parents[2]
PASSWORD_FILE = BASE_PATH / "backend_server" / "mosquitto" / "config" / "passwords"

TECHNICAL_USERS = [
    "mqtt-debug",
    "mqtt-ingestor",
]


def upsert_password_file(username: str, password: str):
    PASSWORD_FILE.parent.mkdir(parents=True, exist_ok=True)

    create_file = not PASSWORD_FILE.exists()
    config_dir = PASSWORD_FILE.parent.resolve()

    command = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{config_dir}:/mosquitto/config",
        "eclipse-mosquitto:2",
        "mosquitto_passwd",
    ]

    if create_file:
        command.append("-c")

    command.extend([
        "-b",
        "/mosquitto/config/passwords",
        username,
        password,
    ])

    subprocess.run(command, check=True)


def provision_identity(
    store: FileSecretStore,
    username: str,
    rotate: bool,
) -> str:
    existing = store.read_mqtt_secret(username)

    if existing and not rotate:
        upsert_password_file(username, existing["MQTT_PASSWORD"])
        return "reused"

    password = store.generate_password()
    store.write_mqtt_secret(username, password)
    upsert_password_file(username, password)

    if existing and rotate:
        return "rotated"

    return "created"


def provision(environment: str, rotate: str | None):
    validate_inventory()

    store = FileSecretStore(environment)
    machines = get_enabled_machines()

    created = 0
    reused = 0
    rotated = 0

    machine_users = [machine["machine_id"] for machine in machines]
    identities = machine_users + TECHNICAL_USERS

    for username in identities:
        rotate_this_user = rotate == username if rotate else False

        if rotate and not rotate_this_user:
            continue

        result = provision_identity(
            store=store,
            username=username,
            rotate=rotate_this_user,
        )

        if result == "created":
            print(f"[CREATE] {username}: credentials created")
            created += 1

        elif result == "reused":
            print(f"[REUSE]  {username}: credentials reused")
            reused += 1

        elif result == "rotated":
            print(f"[ROTATE] {username}: credentials rotated")
            rotated += 1

    print("")
    print("[OK] MQTT identities provisioned")
    print(f"[OK] Password file: {PASSWORD_FILE}")
    print("")
    print(f"created={created}, reused={reused}, rotated={rotated}")


def main():
    parser = argparse.ArgumentParser(
        description="Provision MQTT identities idempotently."
    )

    parser.add_argument(
        "--env",
        default="dev",
        choices=["dev", "prod"],
    )

    parser.add_argument(
        "--rotate",
        help="Rotate credentials for one machine_id or technical username",
    )

    args = parser.parse_args()

    provision(
        environment=args.env,
        rotate=args.rotate,
    )


if __name__ == "__main__":
    main()