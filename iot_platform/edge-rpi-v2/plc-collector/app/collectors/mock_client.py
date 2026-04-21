import random


class MockCollector:
    def __init__(self, settings: dict):
        self.settings = settings
        self.part_count = 1000

    def read(self) -> dict:
        running = random.choice([True, True, True, False])
        if running:
            self.part_count += random.randint(0, 2)

        return {
            "machine_running": running,
            "part_count": self.part_count,
            "spindle_load_pct": round(random.uniform(30.0, 85.0), 2),
            "cycle_time_s": round(random.uniform(15.0, 25.0), 2),
            "alarm_code": 0 if running else random.choice([0, 0, 101, 202]),
        }
