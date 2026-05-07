import argparse
import subprocess
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.inventory_loader import get_machine

BASE_PATH = Path(__file__).resolve().parents[2]
DIST_DIR = BASE_PATH / "dist" / "edge_bundles"


def main():
    parser = argparse.ArgumentParser(description="Deploy edge bundle via SCP/SSH.")
    parser.add_argument("--machine", required=True)
    parser.add_argument("--host", required=False, help="Optional SSH host override, for example pi@192.168.1.50")
    parser.add_argument("--ssh-user", default="pi")
    parser.add_argument("--remote-dir", default="~/iot_edge")
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    machine = get_machine(args.machine)

    edge_host = args.host
    if not edge_host:
        inventory_host = machine.get("edge_host")
        if not inventory_host:
            raise SystemExit(f"Missing edge_host in inventory for machine {args.machine}")

        edge_host = f"{args.ssh_user}@{inventory_host}"

    bundle = DIST_DIR / f"edge_bundle_{args.machine}.zip"

    if not bundle.exists():
        raise SystemExit(f"Bundle not found: {bundle}")

    commands = [
        ["ssh", edge_host, f"mkdir -p {args.remote_dir}"],
        ["scp", str(bundle), f"{edge_host}:{args.remote_dir}/"],
        [
            "ssh",
            edge_host,
            (
                f"cd {args.remote_dir} && "
                f"unzip -o edge_bundle_{args.machine}.zip && "
                f"docker compose pull || true && "
                f"docker compose up -d"
            ),
        ],
    ]

    for cmd in commands:
        print("[CMD]", " ".join(cmd))
        if not args.dry_run:
            subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()