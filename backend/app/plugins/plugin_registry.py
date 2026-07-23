import importlib
import inspect
import pkgutil
import logging
from typing import List, Type

import app.plugins as plugins_package
from app.plugins.base import BasePlugin
from app.models.context import ExecutionContext

logger = logging.getLogger(__name__)


class PluginRegistry:
    """Auto-discovers and manages transformation plugins."""

    def __init__(self):
        self._plugin_classes: List[Type[BasePlugin]] = []

    def discover_plugins(self) -> None:
        """Scan the plugins package and register all BasePlugin subclasses."""
        self._plugin_classes = []
        for _, module_name, is_pkg in pkgutil.iter_modules(
            plugins_package.__path__, plugins_package.__name__ + "."
        ):
            if is_pkg:
                continue
            try:
                module = importlib.import_module(module_name)
            except Exception as exc:
                logger.warning("Failed to import plugin module %s: %s", module_name, exc)
                continue

            for _name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BasePlugin) and obj is not BasePlugin:
                    self._plugin_classes.append(obj)

        logger.info(
            "Discovered %d plugins: %s",
            len(self._plugin_classes),
            [p.NAME for p in self._plugin_classes],
        )

    def load_enabled_plugins(self, context: ExecutionContext) -> List[BasePlugin]:
        """Return instantiated plugins that are enabled in the rules config,
        ordered by the execution_order list if provided."""
        enabled: List[BasePlugin] = []
        for cls in self._plugin_classes:
            rule_cfg = context.rules.get(cls.NAME, {})
            if rule_cfg.get("enabled", False):
                enabled.append(cls())

        # Sort by execution_order if present in rules
        execution_order: List[str] = context.rules.get("execution_order", [])
        if execution_order:
            order_map = {name: idx for idx, name in enumerate(execution_order)}
            enabled.sort(key=lambda p: order_map.get(p.NAME, 999))

        return enabled


# Module-level singleton
registry = PluginRegistry()
