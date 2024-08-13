import yaml
from typing import Any, Dict, Optional


def init_def_config():
    def_config = Config("config.yml")
    def_config.load()

    if not def_config.contains("downloads-folder"):
        def_config.set("downloads-folder", 'downloads')
        def_config.save()


class Config:

    def __init__(self, file_path: str):
        self.file_path: str = file_path
        self.data: Dict[str, Any] = {}

    def load(self) -> None:
        try:
            with open(self.file_path, 'r') as file:
                self.data = yaml.safe_load(file) or {}
        except FileNotFoundError:
            self.data = {}
        except yaml.YAMLError as e:
            print(f"Error loading YAML file: {e}")

    def save(self) -> None:
        try:
            with open(self.file_path, 'w') as file:
                yaml.safe_dump(self.data, file)
        except yaml.YAMLError as e:
            print(f"Error saving YAML file: {e}")

    def get(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        keys: list[str] = key.split('.')
        value: Any = self.data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value

    def contains(self, key: str) -> bool:
        keys: list[str] = key.split('.')
        value: Any = self.data
        for k in keys:
            if isinstance(value, dict):
                if k in value:
                    value = value[k]
                else:
                    return False
            else:
                return False
        return True

    def set(self, key: str, value: Any) -> None:
        keys: list[str] = key.split('.')
        d: Dict[str, Any] = self.data
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value