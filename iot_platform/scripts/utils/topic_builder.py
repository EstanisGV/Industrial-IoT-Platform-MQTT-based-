def machine_topic(plant: str, machine_id: str, message_type: str) -> str:
    return f"factory/{plant}/{machine_id}/{message_type}"

def build_topics(machine: dict) -> dict:
    plant = machine["plant"]
    machine_id = machine["machine_id"]
    return {
        "telemetry": machine_topic(plant, machine_id, "telemetry"),
        "heartbeat": machine_topic(plant, machine_id, "heartbeat"),
        "status": machine_topic(plant, machine_id, "status"),
    }
