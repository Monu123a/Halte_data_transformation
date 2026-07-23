import pandas as pd
import os
from typing import Dict, Optional

class LookupRepository:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir

    def load_lookup(self, file_path: str) -> Optional[pd.DataFrame]:
        """Loads a lookup Excel file into a pandas DataFrame."""
        full_path = os.path.join(self.base_dir, file_path)
        if not os.path.exists(full_path):
            return None
        try:
            # We assume it's an excel file based on requirements
            return pd.read_excel(full_path)
        except Exception as e:
            print(f"Error loading lookup {full_path}: {e}")
            return None

    def load_all_lookups(self, lookup_config: Dict[str, str]) -> Dict[str, pd.DataFrame]:
        """Loads multiple lookups based on the config mapping."""
        lookups = {}
        for key, path in lookup_config.items():
            df = self.load_lookup(path)
            if df is not None:
                lookups[key] = df
        return lookups
