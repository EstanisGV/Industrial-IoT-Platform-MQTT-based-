import argparse
import shutil
import sys
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parents[2]

sys.path.append(str(BASE_PATH / "scripts"))

from validation.validate_inventory import validate_inventory
from utils.inventory_loader import get_machine

GENERATED_EDGES_DIR = BASE_PATH / "generated" / "edges"
DIST_DIR = BASE_PATH / "dist" / "edge_bundles"

def package_machine(machine_id: str):
    src = GENERATED_EDGES_DIR / machine_id

    if not src.exists():
        raise SystemExit(f"Generated edge config not found: {src}")

    DIST_DIR.mkdir(parents=True, exist_ok=True)

    archive_base = DIST_DIR / f"edge_bundle_{machine_id}"
    archive = shutil.make_archive(str(archive_base), "zip", root_dir=str(src))

    print(f"[OK] Bundle created: {archive}")


def main():
    parser = argparse.ArgumentParser(description="Package generated edge bundle.")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--machine")
    group.add_argument("--all", action="store_true")

    args = parser.parse_args()

    if args.all:
        for machine in get_enabled_machines():
            package_machine(machine["machine_id"])
    else:
        package_machine(args.machine)


if __name__ == "__main__":
    main()