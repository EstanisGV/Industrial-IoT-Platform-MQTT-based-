import argparse
import subprocess
from pathlib import Path
import sys

BASE_PATH = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_PATH / "scripts"))

from validation.validate_inventory import validate_inventory
from utils.inventory_loader import get_machine, get_enabled_machines

DIST_DIR = BASE_PATH / "dist" / "edge_bundles"

def deploy_machine(machine_id: str, host: str | None, ssh_user: str, remote_dir: str, dry_run: bool):
    machine = get_machine(machine_id)

    edge_host = host
    if not edge_host:
        inventory_host = machine.get("edge_host")
        if not inventory_host:
            raise SystemExit(f"Missing edge_host in inventory for machine {machine_id}")
        edge_host = f"{ssh_user}@{inventory_host}"

    bundle = DIST_DIR / f"edge_bundle_{machine_id}.zip"
    if not bundle.exists():
        raise SystemExit(f"Bundle not found: {bundle}")

    commands = [
        ["ssh", edge_host, f"mkdir -p {remote_dir}"],
        ["scp", str(bundle), f"{edge_host}:{remote_dir}/"],
        [
            "ssh",
            edge_host,
            (
                f"cd {remote_dir} && "
                f"unzip -o edge_bundle_{machine_id}.zip && "
                f"docker compose pull || true && "
                f"docker compose up -d"
            ),
        ],
    ]

    for cmd in commands:
        print("[CMD]", " ".join(cmd))
        if not dry_run:
            subprocess.run(cmd, check=True)

def select_machines(args):
    machines = get_enabled_machines()

    if args.machine:
        return [get_machine(args.machine)]

    if args.all:
        return machines

    if args.plant:
        return [m for m in machines if m.get("plant") == args.plant]

    if args.area:
        return [m for m in machines if m.get("area") == args.area]

    return []


def main():
    parser = argparse.ArgumentParser(description="Deploy edge bundle via SCP/SSH.")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--machine")
    group.add_argument("--all", action="store_true")
    group.add_argument("--plant")
    group.add_argument("--area")

    parser.add_argument("--host", required=False, help="Optional SSH host override, for example pi@192.168.1.50")
    parser.add_argument("--ssh-user", default="pi")
    parser.add_argument("--remote-dir", default="~/iot_edge")
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()
    if args.host and not args.machine:
        raise SystemExit("--host override is only allowed with --machine")

    validate_inventory()

    selected_machines = select_machines(args)

    if not selected_machines:
        raise SystemExit("No enabled machines matched the deploy criteria.")

    for machine in selected_machines:
        deploy_machine(
            machine_id=machine["machine_id"],
            host=args.host,
            ssh_user=args.ssh_user,
            remote_dir=args.remote_dir,
            dry_run=args.dry_run,
        )


if __name__ == "__main__":
    main()