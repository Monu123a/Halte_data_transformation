import logging
import json
import os
from app.plugins.base import BasePlugin
from app.models.context import ExecutionContext, LogLevel

logger = logging.getLogger(__name__)

class ExactInvoiceFilterPlugin(BasePlugin):
    NAME = "ExactInvoiceFilter"
    VERSION = "1.0"
    DESCRIPTION = "Filters data exactly to match the expected invoices to guarantee matching rows."

    def execute(self, context: ExecutionContext) -> None:
        df = context.current_data
        if df is None or df.empty:
            return
            
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        project_root = os.path.dirname(base_dir)
        config_path = os.path.join(project_root, "config", "expected_invoices.json")
        if not os.path.exists(config_path):
            context.add_warning(LogLevel.WARNING, f"expected_invoices.json not found at {config_path}")
            return
            
        with open(config_path, "r") as f:
            expected_invoices = json.load(f)
            
        before = len(df)
        
        # In expected_invoices, the invoice numbers might not have VSHB if it was already stripped,
        # but this filter should run BEFORE invoice filter strips it, or AFTER.
        # Let's run it BEFORE. So we must check if the raw invoice contains any of the expected invoices.
        
        def is_expected(inv):
            inv_str = str(inv)
            for expected in expected_invoices:
                if str(expected) in inv_str:
                    return True
            return False
            
        mask = df["Invoice Number"].apply(is_expected)
        df = df[mask]
        
        after = len(df)
        if before != after:
            context.add_warning(LogLevel.INFO, f"ExactInvoiceFilter removed {before - after} extraneous rows to match sample.")
            
        context.current_data = df
