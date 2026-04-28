from pathlib import Path
import yaml

BASE_PATH = Path(__file__).resolve().parents[2]

def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def load_inventory():
    return load_yaml(BASE_PATH / "inventory" / "machines.yaml")

def get_enabled_machines():
    return [m for m in load_inventory().get("machines", []) if m.get("enabled", True)]

def get_machine(machine_id: str):
    for machine in get_enabled_machines():
        if machine["machine_id"] == machine_id:
            return machine
    raise ValueError(f"Machine not found or disabled: {machine_id}")

def load_environment(environment: str):
    return load_yaml(BASE_PATH / "inventory" / "environments" / f"{environment}.yaml")

def load_tag_profile(profile: str):
    return load_yaml(BASE_PATH / "inventory" / "tag_profiles" / f"{profile}.yaml")
