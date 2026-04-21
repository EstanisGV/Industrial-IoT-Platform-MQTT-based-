from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class TelemetryMessage:
    machine_id: str
    plant: str
    area: str
    line: str
    controller: str
    source_protocol: str
    config_version: str
    service_version: str
    ts_edge: str
    data: Dict[str, Any]

    def to_dict(self) -> dict:
        return {
            "machine_id": self.machine_id,
            "plant": self.plant,
            "area": self.area,
            "line": self.line,
            "controller": self.controller,
            "source_protocol": self.source_protocol,
            "config_version": self.config_version,
            "service_version": self.service_version,
            "ts_edge": self.ts_edge,
            "data": self.data,
        }
