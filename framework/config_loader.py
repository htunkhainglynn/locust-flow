import json
import os
from typing import Any, Dict

import yaml

from framework.config_validator import ConfigValidator


class ConfigLoader:
    def __init__(self, config_dir: str = "configs", validate: bool = True):
        self.config_dir = config_dir
        self.validate = validate
        self.validator = ConfigValidator()

    def load_config(self, config_file: str) -> Dict[str, Any]:
        """
        Load configuration from a YAML or JSON file.

        Args:
            config_file: Path to the configuration file

        Returns:
            Dictionary containing the configuration
        """
        # Handle both relative and absolute paths
        if not os.path.isabs(config_file):
            config_path = os.path.join(self.config_dir, config_file)
        else:
            config_path = config_file

        # If file doesn't exist in config_dir, try relative to current directory
        if not os.path.exists(config_path):
            config_path = config_file

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        # Load based on file extension
        with open(config_path, "r", encoding="utf-8") as f:
            if config_path.endswith(".yaml") or config_path.endswith(".yml"):
                config = yaml.safe_load(f)
            elif config_path.endswith(".json"):
                config = json.load(f)
            else:
                # Try YAML first, then JSON
                try:
                    f.seek(0)
                    config = yaml.safe_load(f)
                except yaml.YAMLError:
                    f.seek(0)
                    config = json.load(f)

        # Validate configuration
        if self.validate:
            is_valid, errors, warnings = self.validator.validate(config, config_file)
            if not is_valid:
                error_msg = f"Config validation failed for '{config_file}':\n"
                error_msg += "\n".join([f"  - {err}" for err in errors])
                raise ValueError(error_msg)

        return config

    @staticmethod
    def _validate_config(config: Dict[str, Any]):
        """Legacy validation method - kept for backward compatibility."""
        required_fields = ["service_name", "base_url"]

        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field in config: {field}")

        # Validate steps structure if present
        if "steps" in config:
            for i, step in enumerate(config["steps"]):
                if "method" not in step:
                    raise ValueError(f"Step {i} missing required 'method' field")
                if "endpoint" not in step:
                    raise ValueError(f"Step {i} missing required 'endpoint' field")
