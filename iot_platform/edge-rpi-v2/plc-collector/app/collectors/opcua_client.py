from opcua import Client


class OpcUaCollector:
    def __init__(self, settings: dict):
        env = settings["env"]
        self.url = env["OPCUA_URL"]
        self.username = env["OPCUA_USERNAME"]
        self.password = env["OPCUA_PASSWORD"]

        self.client = Client(self.url)

        if self.username:
            self.client.set_user(self.username)
        if self.password:
            self.client.set_password(self.password)

        self.client.connect()

        self.nodes = {
            "machine_running": self.client.get_node("ns=2;s=Machine.Running"),
            "part_count": self.client.get_node("ns=2;s=Machine.PartCount"),
            "spindle_load_pct": self.client.get_node("ns=2;s=Machine.SpindleLoad"),
            "cycle_time_s": self.client.get_node("ns=2;s=Machine.CycleTime"),
            "alarm_code": self.client.get_node("ns=2;s=Machine.AlarmCode"),
        }

    def read(self) -> dict:
        return {
            "machine_running": self.nodes["machine_running"].get_value(),
            "part_count": self.nodes["part_count"].get_value(),
            "spindle_load_pct": float(self.nodes["spindle_load_pct"].get_value()),
            "cycle_time_s": float(self.nodes["cycle_time_s"].get_value()),
            "alarm_code": int(self.nodes["alarm_code"].get_value()),
        }
