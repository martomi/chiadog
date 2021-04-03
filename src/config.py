# std
from pathlib import Path

# lib
import yaml


class Config:
    def __init__(self, config_path: Path):
        if not config_path.is_file():
            raise ValueError(f"Invalid config.yaml path: {config_path}")

        with open(config_path, 'r') as config_file:
            self._config = yaml.safe_load(config_file)

    def _get_child_config(self, key):
        if not key in self._config.keys():
            raise ValueError(f"Invalid config - cannot find {key} key")

        return self._config[key]

    def get_notifier_config(self):
        return self._get_child_config("notifier")

    def get_chia_logs_config(self):
        return self._get_child_config("chia_logs")

    def get_log_level_config(self):
        return self._get_child_config("log_level")
