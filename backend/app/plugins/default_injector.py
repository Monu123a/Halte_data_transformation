import logging
from app.plugins.base import BasePlugin
from app.models.context import ExecutionContext, LogLevel

logger = logging.getLogger(__name__)


class DefaultInjectorPlugin(BasePlugin):
    NAME = "DefaultInjector"
    VERSION = "1.0"
    DESCRIPTION = "Injects default columns (MEM SHIP, TAX REGION, Item Serial No.)."

    def execute(self, context: ExecutionContext) -> None:
        df = context.current_data
        if df is None or df.empty:
            return

        cfg = context.rules.get(self.NAME, {})
        defaults = cfg.get("defaults", {})

        for col_name, default_value in defaults.items():
            df[col_name] = default_value
            logger.info("DefaultInjector: set '%s' = '%s'.", col_name, default_value)

        # Add empty Item Serial No. column if not present
        if "Item Serial No." not in df.columns:
            df["Item Serial No."] = ""

        context.current_data = df
        context.add_warning(LogLevel.INFO, f"DefaultInjector: injected {len(defaults)} default columns + Item Serial No.")
