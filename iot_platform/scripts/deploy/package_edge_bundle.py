import argparse
import shutil
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parents[2]
GENERATED_EDGES_DIR = BASE_PATH / "generated" / "edges"
DIST_DIR = BASE_PATH / "dist" / "edge_bundles"


def main():
    parser = argparse.ArgumentParser(description="Package generated edge bundle.")
    parser.add_argument("--machine", required=True)
    args = parser.parse_args()

    src = GENERATED_EDGES_DIR / args.machine
    if not src.exists():
        raise SystemExit(f"Generated edge config not found: {src}")

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    archive_base = DIST_DIR / f"edge_bundle_{args.machine}"
    archive = shutil.make_archive(str(archive_base), "zip", root_dir=str(src))
    print(f"[OK] Bundle created: {archive}")


if __name__ == "__main__":
    main()
