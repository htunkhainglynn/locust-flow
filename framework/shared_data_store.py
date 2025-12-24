import logging
import threading
from typing import Any, Dict, List, Optional


class SharedDataStore:
    """
    Thread-safe shared data store for storing any data across virtual users.
    Supports storing multiple key-value pairs per identifier.
    """

    def __init__(self):
        self._data: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def store(self, identifier: str, data: Dict[str, Any]) -> None:
        """
        Store data for a specific identifier.

        Args:
            identifier: Unique identifier (e.g., user ID, session ID, msisdn)
            data: Dictionary containing data to store
                  e.g., {'token': 'xxx', 'device_id': 'yyy', 'session': 'zzz'}
        """
        with self._lock:
            if identifier not in self._data:
                self._data[identifier] = {}
            self._data[identifier].update(data)

    def get(self, identifier: str, key: Optional[str] = None) -> Any:
        """
        Retrieve data for a specific identifier.

        Args:
            identifier: Unique identifier
            key: Optional specific key to retrieve. If None, returns all data for the identifier.

        Returns:
            Data or None if not found
        """
        with self._lock:
            if identifier not in self._data:
                logging.warning(f"No data found for identifier: {identifier}")
                return None

            if key:
                value = self._data[identifier].get(key)
                if value:
                    logging.debug(f"Retrieved {key} for identifier: {identifier}")
                return value
            else:
                return self._data[identifier].copy()

    def has_data(self, identifier: str) -> bool:
        """Check if data exists for a specific identifier."""
        with self._lock:
            return identifier in self._data and bool(self._data[identifier])

    def remove(self, identifier: str) -> None:
        """Remove all data for a specific identifier."""
        with self._lock:
            if identifier in self._data:
                del self._data[identifier]
                logging.info(f"Removed data for identifier: {identifier}")

    def clear_all(self) -> None:
        """Clear all stored data."""
        with self._lock:
            self._data.clear()
            logging.info("Cleared all stored data")

    def get_all_identifiers(self) -> List[str]:
        """Get list of all identifiers with stored data."""
        with self._lock:
            return list(self._data.keys())

    def get_count(self) -> int:
        """Get the number of identifiers with stored data."""
        with self._lock:
            return len(self._data)

