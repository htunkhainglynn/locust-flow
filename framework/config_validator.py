"""
Config Validator - Validates YAML configuration files for common errors and required fields.
"""

import logging
from typing import Any, Dict, List, Tuple


class ConfigValidator:
    """Validates configuration files for correctness and completeness."""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate(
        self, config: Dict[str, Any], config_file: str = "config"
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a configuration file.

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []

        # Validate top-level keys first
        self._validate_top_level_keys(config)

        # Required fields
        self._validate_required_fields(config)

        # Conditional validations
        self._validate_run_init_once(config)
        self._validate_steps(config)
        self._validate_init_steps(config)
        self._validate_flow_init(config)
        self._validate_variables(config)
        self._validate_retry_on(config)
        self._validate_validation_format(config)
        self._validate_transforms(config)
        self._validate_locust_config(config)

        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings

    def _validate_top_level_keys(self, config: Dict[str, Any]):
        """Validate top-level configuration keys."""
        # Valid top-level keys
        valid_top_level_keys = [
            "service_name",
            "base_url",
            "variables",
            "init",
            "flow_init",
            "steps",
            "cleanup",
            "run_init_once",
            "init_list_var",
            "headers",
            "timeout",
            "verify",
            "locust",
        ]

        # Check for unknown keys - STRICT: treat as ERROR
        for key in config.keys():
            if key not in valid_top_level_keys:
                self.errors.append(
                    f"Invalid top-level field '{key}'. Valid fields: {', '.join(valid_top_level_keys)}. "
                    "Check for typos."
                )

    def _validate_required_fields(self, config: Dict[str, Any]):
        """Validate required top-level fields."""
        required_fields = ["service_name", "base_url"]

        for field in required_fields:
            if field not in config:
                self.errors.append(f"Missing required field: '{field}'")

        # Must have at least steps or init
        if "steps" not in config and "init" not in config:
            self.errors.append("Config must have at least 'steps' or 'init' section")

    def _validate_run_init_once(self, config: Dict[str, Any]):
        """Validate run_init_once configuration."""
        run_init_once = config.get("run_init_once", False)
        init_list_var = config.get("init_list_var")

        if run_init_once:
            # If run_init_once is true, init_list_var must be specified
            if not init_list_var:
                self.errors.append(
                    "When 'run_init_once: true', you must specify 'init_list_var' "
                    "(e.g., 'init_list_var: name_under_init')"
                )
            else:
                # Check if the variable exists in variables section
                variables = config.get("variables", {})
                if init_list_var not in variables:
                    self.errors.append(
                        f"'init_list_var: {init_list_var}' references a variable that doesn't exist. "
                        f"Add '{init_list_var}' to the 'variables' section."
                    )
                elif not isinstance(variables[init_list_var], list):
                    self.errors.append(
                        f"Variable '{init_list_var}' must be a list for 'init_list_var'. "
                        f"Current type: {type(variables[init_list_var]).__name__}"
                    )
                elif len(variables[init_list_var]) == 0:
                    self.warnings.append(
                        f"Variable '{init_list_var}' is an empty list. "
                        "No users will be initialized."
                    )

    def _validate_steps(self, config: Dict[str, Any]):
        """Validate steps section."""
        steps = config.get("steps", [])

        if not steps:
            self.warnings.append("No 'steps' defined. Only init/cleanup will run.")
            return

        if not isinstance(steps, list):
            self.errors.append("'steps' must be a list")
            return

        for idx, step in enumerate(steps):
            self._validate_step(step, f"steps[{idx}]")

    def _validate_init_steps(self, config: Dict[str, Any]):
        """Validate init section."""
        init = config.get("init", [])

        if not init:
            return

        if not isinstance(init, list):
            self.errors.append("'init' must be a list")
            return

        for idx, step in enumerate(init):
            self._validate_step(step, f"init[{idx}]")

    def _validate_flow_init(self, config: Dict[str, Any]):
        """Validate flow_init section."""
        flow_init = config.get("flow_init", [])

        if not flow_init:
            return

        if not isinstance(flow_init, list):
            self.errors.append("'flow_init' must be a list of transforms")
            return

        # flow_init should contain transforms, not full steps
        # Validate it using the same logic as pre_transforms/post_transforms
        # This will be validated in _validate_transforms method

    def _validate_step(self, step: Dict[str, Any], path: str):
        """Validate a single step."""
        if not isinstance(step, dict):
            self.errors.append(f"{path}: Step must be a dictionary")
            return

        # Valid keys for a step
        valid_step_keys = [
            "name",
            "method",
            "endpoint",
            "headers",
            "data",
            "params",
            "json",
            "pre_request",
            "pre_transforms",
            "post_transforms",
            "extract",
            "validate",
            "retry_on",
            "skip_if",
            "weight",
            "timeout",
            "allow_redirects",
            "verify",
            "cert",
            "auth",
        ]

        # Check for unknown keys
        for key in step.keys():
            if key not in valid_step_keys:
                self.warnings.append(
                    f"{path}: Unknown field '{key}'. Valid fields: {', '.join(valid_step_keys)}. "
                    "This might be a typo."
                )

        # Required fields for a step
        if "name" not in step:
            self.errors.append(f"{path}: Missing required field 'name'")

        if "method" not in step:
            self.errors.append(f"{path}: Missing required field 'method'")
        else:
            valid_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
            if step["method"].upper() not in valid_methods:
                self.errors.append(
                    f"{path}: Invalid HTTP method '{step['method']}'. "
                    f"Valid methods: {', '.join(valid_methods)}"
                )

        if "endpoint" not in step:
            self.errors.append(f"{path}: Missing required field 'endpoint'")

        # Validate that pre_request has a value if present
        if "pre_request" in step:
            if step["pre_request"] is None or step["pre_request"] == "":
                self.errors.append(
                    f"{path}: 'pre_request' cannot be empty. "
                    "Either provide a value or remove the field."
                )

        # Validate that Content-Type header is required when using 'data' field
        if "data" in step:
            if "headers" not in step:
                self.errors.append(
                    f"{path}: 'headers' field with 'Content-Type' is required when using 'data' field. "
                    "Specify Content-Type (e.g., 'application/json', 'application/x-www-form-urlencoded')"
                )
            else:
                headers = step["headers"]
                if isinstance(headers, dict):
                    # Check for Content-Type (case-insensitive)
                    has_content_type = any(
                        key.lower() == "content-type" for key in headers.keys()
                    )
                    if not has_content_type:
                        self.errors.append(
                            f"{path}: 'Content-Type' header is required when using 'data' field. "
                            "Specify Content-Type (e.g., 'application/x-www-form-urlencoded')"
                        )

        # Validate weight if present
        if "weight" in step:
            weight = step["weight"]

            # Skip validation if it's a template variable
            if isinstance(weight, str) and "{{" in weight and "}}" in weight:
                # It's a template variable, skip validation
                pass
            else:
                # Try to cast string numbers to float
                if isinstance(weight, str):
                    try:
                        weight = float(weight)
                    except (ValueError, TypeError):
                        self.errors.append(
                            f"{path}: 'weight' must be a number, got invalid string '{weight}'"
                        )
                        weight = None  # Skip range check

                if weight is not None:
                    if not isinstance(weight, (int, float)):
                        self.errors.append(
                            f"{path}: 'weight' must be a number, got {type(weight).__name__}"
                        )
                    elif weight < 0 or weight > 1:
                        self.errors.append(
                            f"{path}: 'weight' must be between 0 and 1 (inclusive), got {weight}"
                        )

        # Validate retry_on if present
        if "retry_on" in step:
            self._validate_retry_on_step(step["retry_on"], f"{path}.retry_on")

        # Validate validate if present
        if "validate" in step:
            self._validate_validation_step(step["validate"], f"{path}.validate")

    def _validate_variables(self, config: Dict[str, Any]):
        """Validate variables section."""
        variables = config.get("variables", {})

        if not variables:
            self.warnings.append(
                "No 'variables' defined. Consider adding reusable variables."
            )
            return

        if not isinstance(variables, dict):
            self.errors.append("'variables' must be a dictionary")

    def _validate_retry_on(self, config: Dict[str, Any]):
        """Validate retry_on configurations across all steps."""
        all_steps = []
        all_steps.extend(config.get("init", []))
        all_steps.extend(config.get("steps", []))
        all_steps.extend(config.get("cleanup", []))

        for step in all_steps:
            if isinstance(step, dict) and "retry_on" in step:
                retry_on = step["retry_on"]
                step_name = step.get("name", "unnamed")
                self._validate_retry_on_step(retry_on, f"step '{step_name}'.retry_on")

    def _validate_retry_on_step(self, retry_on: Dict[str, Any], path: str):
        """Validate a retry_on configuration."""
        if not isinstance(retry_on, dict):
            self.errors.append(f"{path}: Must be a dictionary")
            return

        # Valid keys for retry_on
        valid_retry_keys = ["condition", "left", "right", "action", "max_retries"]

        # Check for unknown keys
        for key in retry_on.keys():
            if key not in valid_retry_keys:
                self.warnings.append(
                    f"{path}: Unknown field '{key}'. Valid fields: {', '.join(valid_retry_keys)}. "
                    "This might be a typo."
                )

        # Required fields
        required = ["condition", "left", "right"]
        for field in required:
            if field not in retry_on:
                self.errors.append(f"{path}: Missing required field '{field}'")

        # Validate condition type
        if "condition" in retry_on:
            valid_conditions = [
                "equals",
                "not_equals",
                "contains",
                "not_contains",
                "greater_than",
                "less_than",
                "is_empty",
                "is_not_empty",
            ]
            if retry_on["condition"] not in valid_conditions:
                self.errors.append(
                    f"{path}: Invalid condition '{retry_on['condition']}'. "
                    f"Valid: {', '.join(valid_conditions)}"
                )

        # Validate action if present
        if "action" in retry_on:
            action = retry_on["action"]
            if not isinstance(action, str):
                self.errors.append(f"{path}.action: Must be a string (step name)")

        # Validate max_retries if present
        if "max_retries" in retry_on:
            max_retries = retry_on["max_retries"]
            if not isinstance(max_retries, int) or max_retries < 0:
                self.errors.append(
                    f"{path}.max_retries: Must be a positive integer, got '{max_retries}'"
                )
            elif max_retries > 10:
                self.warnings.append(
                    f"{path}.max_retries: Value {max_retries} is very high. "
                    "Consider reducing to avoid long retry loops."
                )

    def _validate_validation_format(self, config: Dict[str, Any]):
        """Validate validation configurations across all steps."""
        all_steps = []
        all_steps.extend(config.get("init", []))
        all_steps.extend(config.get("steps", []))
        all_steps.extend(config.get("cleanup", []))

        for step in all_steps:
            if isinstance(step, dict) and "validate" in step:
                validate = step["validate"]
                step_name = step.get("name", "unnamed")
                self._validate_validation_step(validate, f"step '{step_name}'.validate")

    def _validate_validation_step(self, validate: Any, path: str):
        """Validate a validation configuration."""
        if isinstance(validate, dict):
            # Old format - just check for known fields
            valid_fields = ["status_code", "max_response_time", "json", "fail_on_error"]
            for field in validate.keys():
                if field not in valid_fields:
                    self.warnings.append(
                        f"{path}: Unknown validation field '{field}'. "
                        f"Valid fields: {', '.join(valid_fields)}"
                    )
        elif isinstance(validate, list):
            # New format - validate each item
            for idx, item in enumerate(validate):
                if not isinstance(item, dict):
                    self.errors.append(f"{path}[{idx}]: Must be a dictionary")
                    continue

                # Determine validation format
                field_based_keys = {"field", "condition", "expected"}
                old_format_keys = {
                    "status_code",
                    "max_response_time",
                    "json",
                    "fail_on_error",
                }
                item_keys = set(item.keys())

                has_field_based = bool(item_keys & field_based_keys)
                has_old_format = bool(item_keys & old_format_keys)

                if has_field_based:
                    # Field-based validation
                    valid_field_validation_keys = ["field", "condition", "expected"]

                    # Check for unknown keys
                    for key in item.keys():
                        if key not in valid_field_validation_keys:
                            self.warnings.append(
                                f"{path}[{idx}]: Unknown field '{key}'. Valid fields: {', '.join(valid_field_validation_keys)}. "
                                "This might be a typo."
                            )

                    # Required fields
                    required = ["field", "condition"]
                    for field in required:
                        if field not in item:
                            self.errors.append(
                                f"{path}[{idx}]: Missing required field '{field}'"
                            )

                    if "condition" in item:
                        valid_conditions = [
                            "equals",
                            "not_equals",
                            "contains",
                            "not_contains",
                            "greater_than",
                            "less_than",
                            "is_empty",
                            "is_not_empty",
                        ]
                        if item["condition"] not in valid_conditions:
                            self.errors.append(
                                f"{path}[{idx}]: Invalid condition '{item['condition']}'. "
                                f"Valid: {', '.join(valid_conditions)}"
                            )
                elif has_old_format:
                    # Old format in list
                    valid_fields = [
                        "status_code",
                        "max_response_time",
                        "json",
                        "fail_on_error",
                    ]
                    for field in item.keys():
                        if field not in valid_fields:
                            self.warnings.append(
                                f"{path}[{idx}]: Unknown validation field '{field}'. "
                                f"Valid fields: {', '.join(valid_fields)}"
                            )
                else:
                    # Unknown format
                    self.errors.append(
                        f"{path}[{idx}]: Invalid validation format. "
                        "Expected field-based validation (field, condition, expected) or "
                        "old format (status_code, max_response_time, json, fail_on_error). "
                        f"Found keys: {', '.join(item.keys())}"
                    )
        else:
            self.errors.append(f"{path}: Must be a dictionary or list")

    def _validate_transforms(self, config: Dict[str, Any]):
        """Validate pre_transforms and post_transforms across all steps."""
        # Valid transform types
        valid_types = [
            "rsa_encrypt",
            "hmac",
            "sha256",
            "base64_encode",
            "base64_decode",
            "uuid",
            "timestamp",
            "random_number",
            "random_choice",
            "random_string",
            "increment",
            "select_from_list",
            "select_msisdn",
            "append_to_list",
            "store_data",
            "lookup",
            "lookup_all",
            "get_store_keys",
        ]

        # Valid modes for select_from_list
        valid_modes = ["random", "round_robin", "sequential"]

        # Get variables for cross-reference validation
        variables = config.get("variables", {})

        all_steps = []
        all_steps.extend(config.get("init", []))
        all_steps.extend(config.get("steps", []))
        all_steps.extend(config.get("cleanup", []))

        # Track variables created by transform outputs
        dynamic_variables = set()

        # Validate flow_init transforms
        flow_init = config.get("flow_init", [])
        if flow_init:
            if isinstance(flow_init, list):
                self._validate_transform_list(
                    flow_init,
                    "flow_init",
                    valid_types,
                    valid_modes,
                    variables,
                    dynamic_variables,
                )

        for step in all_steps:
            if not isinstance(step, dict):
                continue

            step_name = step.get("name", "unnamed")

            # Validate pre_transforms and collect output variables
            if "pre_transforms" in step:
                self._validate_transform_list(
                    step["pre_transforms"],
                    f"step '{step_name}'.pre_transforms",
                    valid_types,
                    valid_modes,
                    variables,
                    dynamic_variables,
                )

            # Validate post_transforms and collect output variables
            if "post_transforms" in step:
                self._validate_transform_list(
                    step["post_transforms"],
                    f"step '{step_name}'.post_transforms",
                    valid_types,
                    valid_modes,
                    variables,
                    dynamic_variables,
                )

    def _validate_transform_list(
        self,
        transforms: Any,
        path: str,
        valid_types: list,
        valid_modes: list,
        variables: Dict[str, Any] = None,
        dynamic_variables: set = None,
    ):
        """Validate a list of transforms."""
        if not isinstance(transforms, list):
            self.errors.append(f"{path}: Must be a list")
            return

        for idx, transform in enumerate(transforms):
            if not isinstance(transform, dict):
                self.errors.append(f"{path}[{idx}]: Must be a dictionary")
                continue

            # Valid keys for transforms
            valid_transform_keys = ["type", "config", "input", "output"]

            # Check for unknown keys
            for key in transform.keys():
                if key not in valid_transform_keys:
                    self.warnings.append(
                        f"{path}[{idx}]: Unknown field '{key}'. Valid fields: {', '.join(valid_transform_keys)}. "
                        "This might be a typo."
                    )

            # Validate type field
            if "type" not in transform:
                self.errors.append(f"{path}[{idx}]: Missing required field 'type'")
                continue

            transform_type = transform["type"]
            if transform_type not in valid_types:
                self.errors.append(
                    f"{path}[{idx}]: Invalid transform type '{transform_type}'. "
                    f"Valid types: {', '.join(valid_types)}"
                )

            # Track output variables
            if "output" in transform and dynamic_variables is not None:
                dynamic_variables.add(transform["output"])

            # Validate config structure for specific types
            if transform_type == "select_from_list":
                self._validate_select_from_list_config(
                    transform, f"{path}[{idx}]", valid_modes, variables, dynamic_variables
                )
            elif transform_type == "random_number":
                self._validate_random_number_config(transform, f"{path}[{idx}]")
            elif transform_type == "random_string":
                self._validate_random_string_config(transform, f"{path}[{idx}]")
            elif transform_type == "store_data":
                self._validate_store_data_config(transform, f"{path}[{idx}]")
            elif transform_type == "rsa_encrypt":
                self._validate_rsa_encrypt_config(transform, f"{path}[{idx}]")

    def _validate_select_from_list_config(
        self,
        transform: Dict[str, Any],
        path: str,
        valid_modes: list,
        variables: Dict[str, Any] = None,
        dynamic_variables: set = None,
    ):
        """Validate select_from_list transform configuration."""
        if "config" not in transform:
            self.errors.append(f"{path}: 'select_from_list' requires 'config' field")
            return

        config = transform["config"]
        if not isinstance(config, dict):
            self.errors.append(f"{path}.config: Must be a dictionary")
            return

        # Check required fields
        if "from" not in config:
            self.errors.append(
                f"{path}.config: Missing required field 'from' (variable name)"
            )
        else:
            # Validate that the variable exists
            from_var = config["from"]
            if variables is not None:
                # Skip validation if the variable is dynamically created by a previous transform
                if dynamic_variables and from_var in dynamic_variables:
                    pass  # Variable is created by a previous transform, skip validation
                elif from_var not in variables:
                    self.errors.append(
                        f"{path}.config.from: Variable '{from_var}' does not exist. "
                        f"Add '{from_var}' to the 'variables' section."
                    )
                elif not isinstance(variables[from_var], list):
                    self.errors.append(
                        f"{path}.config.from: Variable '{from_var}' must be a list. "
                        f"Current type: {type(variables[from_var]).__name__}"
                    )

        if "mode" not in config:
            self.errors.append(f"{path}.config: Missing required field 'mode'")
        elif config["mode"] not in valid_modes:
            self.errors.append(
                f"{path}.config.mode: Invalid mode '{config['mode']}'. "
                f"Valid modes: {', '.join(valid_modes)}"
            )

        # Check output field
        if "output" not in transform:
            self.warnings.append(
                f"{path}: Missing 'output' field. Transform result won't be stored."
            )

    def _validate_random_number_config(self, transform: Dict[str, Any], path: str):
        """Validate random_number transform configuration."""
        if "config" not in transform:
            self.errors.append(f"{path}: 'random_number' requires 'config' field")
            return

        config = transform["config"]
        if not isinstance(config, dict):
            self.errors.append(f"{path}.config: Must be a dictionary")
            return

        # Check min and max
        if "min" not in config:
            self.errors.append(f"{path}.config: Missing required field 'min'")
        elif not isinstance(config["min"], int):
            self.errors.append(f"{path}.config.min: Must be an integer")

        if "max" not in config:
            self.errors.append(f"{path}.config: Missing required field 'max'")
        elif not isinstance(config["max"], int):
            self.errors.append(f"{path}.config.max: Must be an integer")

        # Check min < max
        if "min" in config and "max" in config:
            if isinstance(config["min"], int) and isinstance(config["max"], int):
                if config["min"] >= config["max"]:
                    self.errors.append(
                        f"{path}.config: 'min' ({config['min']}) must be less than 'max' ({config['max']})"
                    )

    def _validate_random_string_config(self, transform: Dict[str, Any], path: str):
        """Validate random_string transform configuration."""
        if "config" not in transform:
            self.errors.append(f"{path}: 'random_string' requires 'config' field")
            return

        config = transform["config"]
        if not isinstance(config, dict):
            self.errors.append(f"{path}.config: Must be a dictionary")
            return

        # Check length
        if "length" not in config:
            self.errors.append(f"{path}.config: Missing required field 'length'")
        elif not isinstance(config["length"], int) or config["length"] <= 0:
            self.errors.append(f"{path}.config.length: Must be a positive integer")

        # Check charset if present
        if "charset" in config:
            valid_charsets = ["alpha", "numeric", "alphanumeric"]
            if config["charset"] not in valid_charsets:
                self.errors.append(
                    f"{path}.config.charset: Invalid charset '{config['charset']}'. "
                    f"Valid: {', '.join(valid_charsets)}"
                )

    def _validate_store_data_config(self, transform: Dict[str, Any], path: str):
        """Validate store_data transform configuration."""
        if "config" not in transform:
            self.errors.append(f"{path}: 'store_data' requires 'config' field")
            return

        config = transform["config"]
        if not isinstance(config, dict):
            self.errors.append(f"{path}.config: Must be a dictionary")
            return

        # Check required fields
        if "key" not in config:
            self.errors.append(f"{path}.config: Missing required field 'key'")

        if "values" not in config:
            self.errors.append(f"{path}.config: Missing required field 'values'")
        elif not isinstance(config["values"], list):
            self.errors.append(f"{path}.config.values: Must be a list")

    def _validate_rsa_encrypt_config(self, transform: Dict[str, Any], path: str):
        """Validate rsa_encrypt transform configuration."""
        # Check input and output fields
        if "input" not in transform:
            self.errors.append(f"{path}: 'rsa_encrypt' requires 'input' field")

        if "output" not in transform:
            self.errors.append(f"{path}: 'rsa_encrypt' requires 'output' field")

    def _validate_locust_config(self, config: Dict[str, Any]):
        """Validate optional locust configuration section."""
        if "locust" not in config:
            return

        locust_config = config["locust"]
        path = "locust"

        if not isinstance(locust_config, dict):
            self.errors.append(f"{path}: Must be a dictionary")
            return

        # Valid locust config keys
        valid_locust_keys = [
            "wait_time",
            "throughput",
            "min_wait",
            "max_wait",
            "pacing",
        ]

        # Check for unknown keys
        for key in locust_config.keys():
            if key not in valid_locust_keys:
                self.warnings.append(
                    f"{path}: Unknown field '{key}'. Valid fields: {', '.join(valid_locust_keys)}"
                )

        # Validate wait_time if present
        if "wait_time" in locust_config:
            wait_time = locust_config["wait_time"]
            valid_wait_times = [
                "constant_throughput",
                "constant",
                "between",
                "constant_pacing",
            ]
            if wait_time not in valid_wait_times:
                self.errors.append(
                    f"{path}.wait_time: Invalid value '{wait_time}'. "
                    f"Valid options: {', '.join(valid_wait_times)}"
                )

            # Validate required fields for each wait_time type
            if wait_time == "constant_throughput":
                if "throughput" not in locust_config:
                    self.errors.append(
                        f"{path}: 'throughput' is required when wait_time is 'constant_throughput'"
                    )
                elif not isinstance(locust_config["throughput"], (int, float)):
                    self.errors.append(f"{path}.throughput: Must be a number")
                elif locust_config["throughput"] <= 0:
                    self.errors.append(f"{path}.throughput: Must be greater than 0")

            elif wait_time == "constant":
                if "min_wait" not in locust_config:
                    self.errors.append(
                        f"{path}: 'min_wait' is required when wait_time is 'constant'"
                    )
                elif not isinstance(locust_config["min_wait"], (int, float)):
                    self.errors.append(f"{path}.min_wait: Must be a number")
                elif locust_config["min_wait"] < 0:
                    self.errors.append(f"{path}.min_wait: Must be non-negative")

            elif wait_time == "between":
                if "min_wait" not in locust_config or "max_wait" not in locust_config:
                    self.errors.append(
                        f"{path}: Both 'min_wait' and 'max_wait' are required when wait_time is 'between'"
                    )
                else:
                    min_wait = locust_config.get("min_wait")
                    max_wait = locust_config.get("max_wait")

                    if not isinstance(min_wait, (int, float)):
                        self.errors.append(f"{path}.min_wait: Must be a number")
                    if not isinstance(max_wait, (int, float)):
                        self.errors.append(f"{path}.max_wait: Must be a number")

                    if isinstance(min_wait, (int, float)) and isinstance(
                        max_wait, (int, float)
                    ):
                        if min_wait < 0:
                            self.errors.append(f"{path}.min_wait: Must be non-negative")
                        if max_wait < 0:
                            self.errors.append(f"{path}.max_wait: Must be non-negative")
                        if min_wait > max_wait:
                            self.errors.append(
                                f"{path}: 'min_wait' ({min_wait}) cannot be greater than 'max_wait' ({max_wait})"
                            )

            elif wait_time == "constant_pacing":
                if "pacing" not in locust_config:
                    self.errors.append(
                        f"{path}: 'pacing' is required when wait_time is 'constant_pacing'"
                    )
                elif not isinstance(locust_config["pacing"], (int, float)):
                    self.errors.append(f"{path}.pacing: Must be a number")
                elif locust_config["pacing"] <= 0:
                    self.errors.append(f"{path}.pacing: Must be greater than 0")


def validate_config_file(config: Dict[str, Any], config_file: str = "config") -> bool:
    """
    Convenience function to validate a config file.

    Returns:
        True if valid, False otherwise
    """
    validator = ConfigValidator()
    is_valid, errors, warnings = validator.validate(config, config_file)
    return is_valid
