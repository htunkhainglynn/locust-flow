from abc import ABC, abstractmethod
from typing import Any, Dict


class BasePlugin(ABC):

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def execute(
        self, input_data: Any, config: Dict[str, Any], context: Dict[str, Any]
    ) -> Any:
        """
        Execute the plugin with the given input data and configuration.

        Args:
            input_data: The input data to process
            config: Plugin-specific configuration
            context: Execution context with variables

        Returns:
            Processed output data
        """
        pass

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> bool:
        """
        Validate the plugin configuration.

        Args:
            config: Plugin configuration to validate

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        return True
