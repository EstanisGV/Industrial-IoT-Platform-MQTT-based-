import math
import time


class MockCollector:
    def __init__(self, settings: dict):
        self.settings = settings
        self.counter = 0

    def read(self):
        self.counter += 1
        now = time.time()
        return {
            "machine_running": self.counter % 12 != 0,
            "part_count": self.counter,
            "spindle_load_pct": round(45 + 20 * math.sin(now / 8), 2),
            "cycle_time_s": round(18 + 3 * math.sin(now / 10), 2),
            "alarm_code": 0 if self.counter % 20 else 101,
        }
