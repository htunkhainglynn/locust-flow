import random
import string
import threading
import time
import uuid
from typing import Any, Dict

from .base import BasePlugin


class UUIDPlugin(BasePlugin):

    def __init__(self):
        super().__init__("uuid")

    def execute(
        self, input_data: Any, config: Dict[str, Any], context: Dict[str, Any]
    ) -> str:
        version = config.get("version", 4)
        if version == 1:
            return str(uuid.uuid1())
        else:
            return str(uuid.uuid4())


class TimestampPlugin(BasePlugin):

    def __init__(self):
        super().__init__("timestamp")

    def execute(
        self, input_data: Any, config: Dict[str, Any], context: Dict[str, Any]
    ) -> int:
        unit = config.get("unit", "seconds")
        current_time = time.time()

        if unit == "milliseconds":
            return int(current_time * 1000)
        elif unit == "microseconds":
            return int(current_time * 1000000)
        else:
            return int(current_time)


class RandomNumberPlugin(BasePlugin):

    def __init__(self):
        super().__init__("random_number")

    def execute(
        self, input_data: Any, config: Dict[str, Any], context: Dict[str, Any]
    ) -> int:
        min_val = config.get("min", 0)
        max_val = config.get("max", 100)
        return random.randint(min_val, max_val)


class RandomChoicePlugin(BasePlugin):

    def __init__(self):
        super().__init__("random_choice")

    def execute(
        self, input_data: Any, config: Dict[str, Any], context: Dict[str, Any]
    ) -> Any:
        choices = config.get("choices", [])

        if not choices:
            choices_var = config.get("choices_var")
            if choices_var:
                choices = context.get(choices_var, [])

        if not choices:
            raise ValueError("No choices provided for random_choice plugin")
        return random.choice(choices)


class RandomStringPlugin(BasePlugin):

    def __init__(self):
        super().__init__("random_string")

    def execute(
        self, input_data: Any, config: Dict[str, Any], context: Dict[str, Any]
    ) -> str:
        length = config.get("length", 10)
        charset = config.get("charset", "alphanumeric")

        if charset == "alphanumeric":
            chars = string.ascii_letters + string.digits
        elif charset == "alphabetic":
            chars = string.ascii_letters
        elif charset == "numeric":
            chars = string.digits
        elif charset == "lowercase":
            chars = string.ascii_lowercase
        elif charset == "uppercase":
            chars = string.ascii_uppercase
        else:
            chars = charset

        return "".join(random.choice(chars) for _ in range(length))


class IncrementPlugin(BasePlugin):

    def __init__(self):
        super().__init__("increment")
        self._counters = {}

    def execute(
        self, input_data: Any, config: Dict[str, Any], context: Dict[str, Any]
    ) -> int:
        key = config.get("key", "default")
        start = config.get("start", 1)
        step = config.get("step", 1)

        if key not in self._counters:
            self._counters[key] = start
        else:
            self._counters[key] += step

        return self._counters[key]


class SelectFromListPlugin(BasePlugin):
    _round_robin_counters = {}
    _counter_lock = threading.Lock()

    def __init__(self):
        super().__init__("select_from_list")

    def execute(
        self, input_data: Any, config: Dict[str, Any], context: Dict[str, Any]
    ) -> str:
        # Get the list to select from - supports multiple ways to specify
        items = config.get("items", [])

        if not items:
            # Try to get from context using variable name
            items_var = config.get("from")
            item_list = context.get(items_var)

            if item_list:
                # If items_var is already a list (template engine rendered it), use it directly
                if isinstance(item_list, list):
                    items = item_list
                else:
                    # Otherwise, look it up in context by name
                    items = context.get(item_list, [])

        if not items:
            raise ValueError(
                "No items provided for select_from_list plugin. Use 'items' or 'from' config."
            )

        # Ensure items is a list
        if not isinstance(items, list):
            raise TypeError(
                f"Items must be a list, got {type(items).__name__}: {items}"
            )

        selection_mode = config.get("mode", "random")

        if selection_mode == "random":
            selected = random.choice(items)
        elif selection_mode == "round_robin":
            # Use a unique counter per list variable to support multiple lists
            counter_key = config.get("from", "default")
            with self._counter_lock:
                if counter_key not in self._round_robin_counters:
                    self._round_robin_counters[counter_key] = 0
                index = self._round_robin_counters[counter_key] % len(items)
                selected = items[index]
                self._round_robin_counters[counter_key] += 1
        else:
            selected = random.choice(items)

        return selected


class SelectMsisdnPlugin(BasePlugin):
    """Deprecated: Use SelectFromListPlugin instead. Kept for backward compatibility."""

    _round_robin_counter = 0
    _counter_lock = threading.Lock()

    def __init__(self):
        super().__init__("select_msisdn")

    def execute(
        self, input_data: Any, config: Dict[str, Any], context: Dict[str, Any]
    ) -> str:
        msisdns = config.get("msisdns", [])

        if not msisdns:
            msisdns_var = config.get("msisdns_var")
            if msisdns_var:
                msisdns = context.get(msisdns_var, [])

        if not msisdns:
            raise ValueError("No msisdns provided for select_msisdn plugin")

        selection_mode = config.get("mode", "random")

        if selection_mode == "random":
            selected = random.choice(msisdns)
        elif selection_mode == "round_robin":
            with self._counter_lock:
                index = self._round_robin_counter % len(msisdns)
                selected = msisdns[index]
                self._round_robin_counter += 1
        else:
            selected = random.choice(msisdns)

        return selected


class AppendToListPlugin(BasePlugin):
    """Append a value to a list variable in the context."""

    def __init__(self):
        super().__init__("append_to_list")

    def execute(
        self, input_data: Any, config: Dict[str, Any], context: Dict[str, Any]
    ) -> Any:
        """
        Append a value to a list variable.

        Args:
            input_data: Not used
            config: Configuration with 'list_var' and 'value'
            context: Execution context

        Returns:
            The updated list
        """
        list_var = config.get("list_var")
        if not list_var:
            raise ValueError("'list_var' is required for append_to_list plugin")

        value = config.get("value")
        if value is None:
            raise ValueError("'value' is required for append_to_list plugin")

        # Get or create the list
        if list_var not in context:
            context[list_var] = []

        current_list = context[list_var]
        if not isinstance(current_list, list):
            raise ValueError(
                f"Variable '{list_var}' is not a list, got {type(current_list).__name__}"
            )

        # Append the value
        current_list.append(value)

        import logging

        logging.info(
            f"[append_to_list] Appended '{value}' to '{list_var}'. List now has {len(current_list)} items"
        )

        return current_list


class StoreDataPlugin(BasePlugin):
    """Store data in shared storage for reuse across virtual users."""

    def __init__(self):
        super().__init__("store_data")

    def execute(
        self, input_data: Any, config: Dict[str, Any], context: Dict[str, Any]
    ) -> Any:
        from ..shared_data_store import SharedDataStore

        data_store = context.get("_data_store")
        if not data_store:
            raise ValueError("SharedDataStore not found in context")

        identifier = config.get("key")
        if not identifier:
            raise ValueError("key not provided for store_data plugin")

        data_to_store = {}
        values_to_store = config.get("values", [])

        for value_name in values_to_store:
            if value_name in context:
                data_to_store[value_name] = context[value_name]

        if data_to_store:
            data_store.store(identifier, data_to_store)
            import logging

            logging.info(
                f"[store_data] Data store now has {data_store.get_count()} keys: {data_store.get_all_identifiers()}"
            )

            for key in data_store.get_all_identifiers():
                stored = data_store.get(key)
                logging.info(f"{key}: {stored}")


        else:
            import logging

            logging.warning(
                f"[store_data] No data to store for key '{identifier}' - values_to_store: {values_to_store}, context keys: {list(context.keys())}"
            )

        # Optional: refresh by returning all stored data for this key
        # If output is specified, this will update the output variable with all stored data
        refresh = config.get("refresh", False)
        if refresh:
            all_data = data_store.get(identifier)

            if all_data:
                import logging

                logging.info(
                    f"[store_data] Refreshing with all data for key '{identifier}': {list(all_data.keys())}. Try `refresh: false` to turn off refreshing."
                )

                return all_data
            else:
                import logging

                logging.warning(
                    f"[store_data] No data found for refresh for key '{identifier}'"
                )

        return input_data
