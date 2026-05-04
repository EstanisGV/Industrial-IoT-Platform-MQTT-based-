from pathlib import Path
import sys
import yaml

BASE_PATH = Path(__file__).resolve().parents[2]
INVENTORY_PATH = BASE_PATH / "inventory" / "machines.yaml"
TAG_PROFILES_DIR = BASE_PATH / "inventory" / "tag_profiles"

REQUIRED_FIELDS = {
    "machine_id",
    "plant",
    "area",
    "line",
    "controller",
    "protocol",
    "tag_profile",
    "edge_host",
    "enabled",
}

ALLOWED_PROTOCOLS = {"mock", "s7", "opcua"}


def load_yaml(path: Path) -> dict:
    if not path.exists():
        raise ValueError(f"File not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}

    if not isinstance(data, dict):
        raise ValueError(f"Invalid YAML root in {path}. Expected a dictionary.")

    return data


def validate_machine(machine: dict, index: int, machine_ids: set, edge_hosts: set) -> list[str]:
    errors = []

    if not isinstance(machine, dict):
        return [f"Machine entry #{index} must be a dictionary."]

    missing_fields = REQUIRED_FIELDS - set(machine.keys())
    if missing_fields:
        errors.append(
            f"Machine entry #{index} is missing required fields: {sorted(missing_fields)}"
        )

    machine_id = machine.get("machine_id")
    edge_host = machine.get("edge_host")
    protocol = machine.get("protocol")
    enabled = machine.get("enabled")
    tag_profile = machine.get("tag_profile")

    if machine_id:
        if not isinstance(machine_id, str):
            errors.append(f"machine_id in entry #{index} must be a string.")
        elif machine_id in machine_ids:
            errors.append(f"Duplicated machine_id: {machine_id}")
        else:
            machine_ids.add(machine_id)

    if edge_host:
        if not isinstance(edge_host, str):
            errors.append(f"edge_host in machine {machine_id} must be a string.")
        elif edge_host in edge_hosts:
            errors.append(f"Duplicated edge_host: {edge_host}")
        else:
            edge_hosts.add(edge_host)

    if protocol and protocol not in ALLOWED_PROTOCOLS:
        errors.append(
            f"Invalid protocol for machine {machine_id}: {protocol}. "
            f"Allowed values: {sorted(ALLOWED_PROTOCOLS)}"
        )

    if not isinstance(enabled, bool):
        errors.append(f"enabled must be boolean for machine {machine_id}.")

    if tag_profile:
        tag_profile_path = TAG_PROFILES_DIR / f"{tag_profile}.yaml"
        if not tag_profile_path.exists():
            errors.append(
                f"tag_profile does not exist for machine {machine_id}: {tag_profile_path}"
            )

    return errors


def validate_inventory() -> None:
    data = load_yaml(INVENTORY_PATH)

    machines = data.get("machines")
    if machines is None:
        raise ValueError("Missing top-level key: machines")

    if not isinstance(machines, list):
        raise ValueError("machines must be a list.")

    if not machines:
        raise ValueError("machines list cannot be empty.")

    errors = []
    machine_ids = set()
    edge_hosts = set()

    for index, machine in enumerate(machines, start=1):
        errors.extend(validate_machine(machine, index, machine_ids, edge_hosts))

    if errors:
        print("[ERROR] Inventory validation failed:\n")
        for error in errors:
            print(f" - {error}")
        raise SystemExit(1)

    print(f"[OK] Inventory is valid. Machines: {len(machines)}")


def main() -> None:
    validate_inventory()


if __name__ == "__main__":
    main()