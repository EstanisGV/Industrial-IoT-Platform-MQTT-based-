class S7Collector:
    def __init__(self, settings: dict):
        self.settings = settings

    def read(self):
        # Placeholder for future real implementation.
        # Kept intentionally minimal to respect the "thin edge" architecture.
        return {
            "machine_running": True,
            "part_count": 0,
            "spindle_load_pct": 0.0,
            "cycle_time_s": 0.0,
            "alarm_code": 0,
        }
