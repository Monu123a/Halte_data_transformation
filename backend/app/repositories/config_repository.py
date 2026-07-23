import json
import os
from typing import Dict, Any

CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'config')

class ConfigRepository:
    def __init__(self, config_dir: str = CONFIG_DIR):
        self.config_dir = config_dir
        os.makedirs(self.config_dir, exist_ok=True)

    def _get_path(self, filename: str) -> str:
        return os.path.join(self.config_dir, filename)

    def load_json(self, filename: str) -> Dict[str, Any]:
        path = self._get_path(filename)
        if not os.path.exists(path):
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_json(self, filename: str, data: Dict[str, Any]):
        path = self._get_path(filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def load_mapping(self) -> Dict[str, Any]:
        return self.load_json('mapping.json')
        
    def save_mapping(self, data: Dict[str, Any]):
        self.save_json('mapping.json', data)

    def load_rules(self) -> Dict[str, Any]:
        return self.load_json('rules.json')
        
    def save_rules(self, data: Dict[str, Any]):
        self.save_json('rules.json', data)

    def load_lookups_config(self) -> Dict[str, Any]:
        return self.load_json('lookups.json')
        
    def save_lookups_config(self, data: Dict[str, Any]):
        self.save_json('lookups.json', data)
