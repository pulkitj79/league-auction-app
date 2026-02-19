import yaml
from pathlib import Path


class Settings:
    def __init__(self):
        config_path = Path("config.yaml")
        if not config_path.exists():
            raise Exception("config.yaml not found")

        with open(config_path, "r") as f:
            self._config = yaml.safe_load(f)

    @property
    def auction(self):
        return self._config.get("auction", {})

    @property
    def database(self):
        return self._config.get("database", {})

    @property
    def features(self):
        return self._config.get("features", {})
    
    @property
    def security(self):
        return self._config.get("security", {})

    # Generic getter
    def get(self, key, default=None):
        return self._config.get(key, default)

settings = Settings()
