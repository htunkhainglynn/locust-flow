from typing import Any, Dict
from .base import BasePlugin


class LookupPlugin(BasePlugin):
    """
    Lookup plugin to retrieve data from SharedDataStore by dynamic key.
    
    This plugin solves the nested template problem by allowing you to:
    1. First select a user ID
    2. Then lookup data for that user from the store
    
    Usage in YAML:
        pre_transforms:
          - type: "select_from_list"
            config:
              from: "user_ids"
              mode: "random"
            output: "selected_user_id"
          - type: "lookup"
            config:
              store_key: "user_{{ selected_user_id }}"
              field: "email_prefix"
            output: "email_prefix"
    
    This replaces the unsupported nested syntax:
        {{ user_{{ selected_user_id }}.email_prefix }}
    
    With a two-step process:
        1. Select user ID → selected_user_id = 1
        2. Lookup data → email_prefix = "abc123xyz"
    """

    def __init__(self):
        super().__init__("lookup")

    def execute(
        self, input_data: Any, config: Dict[str, Any], context: Dict[str, Any]
    ) -> Any:
        from ..shared_data_store import SharedDataStore

        data_store = context.get("_data_store")
        if not data_store:
            raise ValueError("SharedDataStore not found in context")

        store_key = config.get("store_key")
        if not store_key:
            raise ValueError("store_key not provided for lookup plugin")

        field = config.get("field")
        if not field:
            raise ValueError("field not provided for lookup plugin")

        # Retrieve data from store
        import logging
        logging.info(f"[lookup] Looking up key '{store_key}' from store")
        logging.info(f"[lookup] Data store has {data_store.get_count()} keys: {data_store.get_all_identifiers()}")
        
        stored_data = data_store.get(store_key)
        if not stored_data:
            raise ValueError(f"No data found in store for key: {store_key}. Available keys: {data_store.get_all_identifiers()}")

        # Get the specific field
        if field not in stored_data:
            raise ValueError(
                f"Field '{field}' not found in stored data for key '{store_key}'. "
                f"Available fields: {list(stored_data.keys())}"
            )

        return stored_data[field]


class LookupAllPlugin(BasePlugin):
    """
    Lookup all data for a given key from SharedDataStore.
    
    This plugin retrieves all stored data for a key and makes it available
    in the context. Useful when you need multiple fields from the same user.
    
    Usage in YAML:
        pre_transforms:
          - type: "select_from_list"
            config:
              from: "user_ids"
              mode: "random"
            output: "selected_user_id"
          - type: "lookup_all"
            config:
              store_key: "user_{{ selected_user_id }}"
            output: "user_data"
    
    Then access fields like:
        email: "{{ user_data.email_prefix }}@gmail.com"
        phone: "+60{{ user_data.telco_code }}{{ user_data.phone_number }}"
    """

    def __init__(self):
        super().__init__("lookup_all")

    def execute(
        self, input_data: Any, config: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        from ..shared_data_store import SharedDataStore

        data_store = context.get("_data_store")
        if not data_store:
            raise ValueError("SharedDataStore not found in context")

        store_key = config.get("store_key")
        if not store_key:
            raise ValueError("store_key not provided for lookup_all plugin")

        # Retrieve all data from store
        stored_data = data_store.get(store_key)
        if not stored_data:
            raise ValueError(f"No data found in store for key: {store_key}")

        return stored_data
