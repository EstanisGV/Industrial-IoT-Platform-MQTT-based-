import argparse
import shutil
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parents[1]
GENERATED_DIR = BASE_PATH / "generated"
DIST_DIR = BASE_PATH / "dist"


def package_bundle(machine_id: str):
    src = GENERATED_DIR / machine_id
    if not src.exists():
        raise SystemExit(f"Generated bundle not found: {src}")

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    archive_base = DIST_DIR / f"edge_bundle_{machine_id}"
    archive = shutil.make_archive(str(archive_base), "zip", root_dir=str(src))
    print(f"[OK] Created deployable archive: {archive}")


def main():
    parser = argparse.ArgumentParser(description="Package generated edge bundle.")
    parser.add_argument("--machine", required=True, help="machine_id")
    args = parser.parse_args()
    package_bundle(args.machine)


if __name__ == "__main__":
    main()
