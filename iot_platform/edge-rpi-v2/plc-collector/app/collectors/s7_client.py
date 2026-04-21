import snap7
from snap7.util import get_bool, get_int, get_real
from snap7.type import Areas


class S7Collector:
    def __init__(self, settings: dict):
        env = settings["env"]
        self.plc_ip = env["PLC_IP"]
        self.rack = env["PLC_RACK"]
        self.slot = env["PLC_SLOT"]
        self.db_number = env["PLC_DB_NUMBER"]

        self.client = snap7.client.Client()
        self.client.connect(self.plc_ip, self.rack, self.slot)

    def read(self) -> dict:
        data = self.client.read_area(Areas.DB, self.db_number, 0, 16)

        return {
            "machine_running": get_bool(data, 0, 0),
            "part_count": get_int(data, 2),
            "spindle_load_pct": round(get_real(data, 4), 2),
            "cycle_time_s": round(get_real(data, 8), 2),
            "alarm_code": get_int(data, 12),
        }
