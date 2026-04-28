import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Restart remote edge service.")
    parser.add_argument("--host", required=True)
    parser.add_argument("--remote-dir", default="~/iot_edge")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cmd = ["ssh", args.host, f"cd {args.remote_dir} && docker compose up -d --force-recreate"]
    print("[CMD]", " ".join(cmd))
    if not args.dry_run:
        subprocess.run(cmd, check=True)

if __name__ == "__main__":
    main()
