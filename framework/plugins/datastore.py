"""Plugins for interacting with the shared data store."""

from typing import Any, Dict, List
from .base import BasePlugin


class GetStoreKeysPlugin(BasePlugin):
    """Plugin to retrieve all keys from the shared data store."""

    def __init__(self):
        super().__init__("get_store_keys")

    def execute(
        self, input_data: Any, config: Dict[str, Any], context: Dict[str, Any]
    ) -> List[str]:
        """
        Retrieve all keys from the shared data store.

        Args:
            input_data: Not used
            config: Optional configuration (not used)
            context: Execution context containing _data_store

        Returns:
            List of all keys in the data store

        Raises:
            ValueError: If data store is not found in context
        """
        data_store = context.get("_data_store")
        if not data_store:
            raise ValueError("SharedDataStore not found in context")

        keys = data_store.get_all_identifiers()
        
        import logging
        logging.info(f"[get_store_keys] Retrieved {len(keys)} keys from data store: {keys}")
        
        return keys
