import argparse
import subprocess
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parents[2]

def main():
    parser = argparse.ArgumentParser(description="Rotate credentials for one machine.")
    parser.add_argument("machine_id")
    parser.add_argument("--env", default="dev", choices=["dev", "prod"])
    args = parser.parse_args()

    subprocess.run(
        [
            "python",
            str(BASE_PATH / "scripts" / "provisioning" / "provision_mqtt_identities.py"),
            "--env",
            args.env,
            "--rotate",
            args.machine_id,
        ],
        check=True,
    )

if __name__ == "__main__":
    main()
