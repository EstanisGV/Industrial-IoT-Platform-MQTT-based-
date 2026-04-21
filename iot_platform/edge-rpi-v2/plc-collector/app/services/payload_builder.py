from app.models.telemetry import TelemetryMessage
from app.utils.timestamps import utc_now_iso


def build_telemetry_payload(settings: dict, data: dict) -> dict:
    machine = settings["machine"]
    env = settings["env"]

    message = TelemetryMessage(
        machine_id=machine["machine_id"],
        plant=machine["plant"],
        area=machine.get("area", ""),
        line=machine.get("line", ""),
        controller=machine["controller"],
        source_protocol=env["PLC_PROTOCOL"],
        config_version=machine.get("config_version", "1.0.0"),
        service_version=env["SERVICE_VERSION"],
        ts_edge=utc_now_iso(),
        data=data,
    )
    return message.to_dict()


def build_heartbeat_payload(settings: dict) -> dict:
    machine = settings["machine"]
    env = settings["env"]

    return {
        "machine_id": machine["machine_id"],
        "plant": machine["plant"],
        "area": machine.get("area", ""),
        "line": machine.get("line", ""),
        "controller": machine["controller"],
        "source_protocol": env["PLC_PROTOCOL"],
        "config_version": machine.get("config_version", "1.0.0"),
        "service_version": env["SERVICE_VERSION"],
        "ts_edge": utc_now_iso(),
        "collector_status": "alive",
    }


def build_status_payload(settings: dict, status: str, detail: str = "") -> dict:
    machine = settings["machine"]
    env = settings["env"]

    return {
        "machine_id": machine["machine_id"],
        "plant": machine["plant"],
        "area": machine.get("area", ""),
        "line": machine.get("line", ""),
        "source_protocol": env["PLC_PROTOCOL"],
        "config_version": machine.get("config_version", "1.0.0"),
        "service_version": env["SERVICE_VERSION"],
        "ts_edge": utc_now_iso(),
        "status": status,
        "detail": detail,
    }
