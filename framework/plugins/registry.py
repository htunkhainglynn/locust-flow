from typing import Dict, Type

from .base import BasePlugin
from .encryption import (Base64DecodePlugin, Base64EncodePlugin, HMACPlugin,
                         RSAEncryptPlugin, SHA256Plugin)
from .generators import (IncrementPlugin, RandomChoicePlugin,
                         RandomNumberPlugin, RandomStringPlugin,
                         SelectFromListPlugin, SelectMsisdnPlugin,
                         StoreDataPlugin, TimestampPlugin, UUIDPlugin)


class PluginRegistry:

    def __init__(self):
        self._plugins: Dict[str, BasePlugin] = {}
        self._register_default_plugins()

    def _register_default_plugins(self):
        default_plugins = [
            RSAEncryptPlugin(),
            HMACPlugin(),
            SHA256Plugin(),
            Base64EncodePlugin(),
            Base64DecodePlugin(),
            UUIDPlugin(),
            TimestampPlugin(),
            RandomNumberPlugin(),
            RandomChoicePlugin(),
            RandomStringPlugin(),
            IncrementPlugin(),
            SelectFromListPlugin(),
            SelectMsisdnPlugin(),  # Kept for backward compatibility
            StoreDataPlugin(),
        ]

        for plugin in default_plugins:
            self.register_plugin(plugin)

    def register_plugin(self, plugin: BasePlugin):
        self._plugins[plugin.name] = plugin

    def get_plugin(self, name: str) -> BasePlugin:
        if name not in self._plugins:
            raise ValueError(f"Plugin not found: {name}")
        return self._plugins[name]

    def execute_plugin(self, plugin_name: str, input_data, config: Dict, context: Dict):
        plugin = self.get_plugin(plugin_name)
        return plugin.execute(input_data, config, context)

    def list_plugins(self) -> list:
        return list(self._plugins.keys())


plugin_registry = PluginRegistry()
