import json
import os
from app.models.config import AppSettings

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'settings.json')

def load_settings() -> AppSettings:
    with open(CONFIG_PATH, 'r') as f:
        data = json.load(f)
    return AppSettings(**data)

def save_settings(settings: AppSettings):
    with open(CONFIG_PATH, 'w') as f:
        f.write(settings.model_dump_json(indent=2))
