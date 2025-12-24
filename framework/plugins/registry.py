from typing import Dict, Type

from .base import BasePlugin
from .datastore import GetStoreKeysPlugin
from .encryption import (Base64DecodePlugin, Base64EncodePlugin, HMACPlugin,
                         RSAEncryptPlugin, SHA256Plugin)
from .generators import (AppendToListPlugin, IncrementPlugin,
                         RandomChoicePlugin, RandomNumberPlugin,
                         RandomStringPlugin, SelectFromListPlugin,
                         SelectMsisdnPlugin, StoreDataPlugin, TimestampPlugin,
                         UUIDPlugin)
from .lookup import LookupAllPlugin, LookupPlugin


class PluginRegistry:

    def __init__(self):
        self._plugins: Dict[str, BasePlugin] = {}
        self._register_default_plugins()

    def _register_default_plugins(self):
        default_plugins = [
            RandomStringPlugin(),
            RandomNumberPlugin(),
            RandomChoicePlugin(),
            TimestampPlugin(),
            UUIDPlugin(),
            IncrementPlugin(),
            SelectMsisdnPlugin(),
            SelectFromListPlugin(),
            AppendToListPlugin(),
            StoreDataPlugin(),
            Base64EncodePlugin(),
            Base64DecodePlugin(),
            SHA256Plugin(),
            HMACPlugin(),
            RSAEncryptPlugin(),
            LookupPlugin(),
            LookupAllPlugin(),
            GetStoreKeysPlugin(),
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
