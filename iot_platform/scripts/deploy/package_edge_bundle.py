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


def main():
    parser = argparse.ArgumentParser(description="Package generated edge bundle.")
    parser.add_argument("--machine", required=True)
    args = parser.parse_args()

    validate_inventory()
    get_machine(args.machine)

    src = GENERATED_EDGES_DIR / args.machine

    if not src.exists():
        raise SystemExit(
            f"Generated edge config not found: {src}\n"
            f"Run first: python scripts/rendering/render_edge_config.py --env dev --machine {args.machine}"
        )

    DIST_DIR.mkdir(parents=True, exist_ok=True)

    archive_base = DIST_DIR / f"edge_bundle_{args.machine}"
    archive = shutil.make_archive(str(archive_base), "zip", root_dir=str(src))

    print(f"[OK] Bundle created: {archive}")


if __name__ == "__main__":
    main()