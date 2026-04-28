from pathlib import Path
import secrets

BASE_PATH = Path(__file__).resolve().parents[2]
SECRETS_ROOT = BASE_PATH / "secrets"


class FileSecretStore:
    """
    Secret store local/dev.

    En producció es pot substituir per Azure Key Vault sense canviar els scripts.
    """

    def __init__(self, environment: str):
        self.environment = environment
        self.root = SECRETS_ROOT / environment

    def mqtt_secret_path(self, username: str) -> Path:
        return self.root / "mqtt" / f"{username}.env"

    def read_mqtt_secret(self, username: str):
        path = self.mqtt_secret_path(username)
        if not path.exists():
            return None
        data = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                data[key.strip()] = value.strip()
        return data

    def write_mqtt_secret(self, username: str, password: str):
        path = self.mqtt_secret_path(username)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"MQTT_USERNAME={username}\nMQTT_PASSWORD={password}\n",
            encoding="utf-8",
        )

    @staticmethod
    def generate_password() -> str:
        return secrets.token_urlsafe(32)
