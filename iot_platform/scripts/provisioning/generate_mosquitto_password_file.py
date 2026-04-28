import argparse
from pathlib import Path
import subprocess
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.inventory_loader import get_enabled_machines
from utils.secret_store import FileSecretStore

BASE_PATH = Path(__file__).resolve().parents[2]
PASSWORD_FILE = BASE_PATH / "backend_server" / "mosquitto" / "config" / "passwords"


def main():
    parser = argparse.ArgumentParser(description="Regenerate Mosquitto password_file from secrets.")
    parser.add_argument("--env", default="dev", choices=["dev", "prod"])
    args = parser.parse_args()

    store = FileSecretStore(args.env)
    PASSWORD_FILE.parent.mkdir(parents=True, exist_ok=True)
    PASSWORD_FILE.write_text("", encoding="utf-8")

    for machine in get_enabled_machines():
        username = machine["machine_id"]
        secret = store.read_mqtt_secret(username)
        if not secret:
            raise SystemExit(f"Missing secret for {username}. Run provision first.")

        subprocess.run(
            ["mosquitto_passwd", "-b", str(PASSWORD_FILE), username, secret["MQTT_PASSWORD"]],
            check=True,
        )
        print(f"[OK] added {username}")

    print(f"[OK] password file regenerated at {PASSWORD_FILE}")


if __name__ == "__main__":
    main()
