import logging
import random
import threading

from locust import (FastHttpUser, between, constant, constant_pacing,
                    constant_throughput, task)

from .config_loader import ConfigLoader
from .flow_executor import FlowExecutor
from .shared_data_store import SharedDataStore


class ConfigDrivenUser(FastHttpUser):
    config_file = None
    wait_time = constant_throughput(1)

    _shared_config = None
    _shared_context = None
    _init_completed = False
    _init_lock = threading.Lock()
    _data_store = SharedDataStore()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_loader = ConfigLoader()
        self.config = None
        self.flow_executor = None

    def on_start(self):
        """Initialize the user with configuration."""
        if not self.config_file:
            raise ValueError("config_file must be set for ConfigDrivenUser")

        try:
            self.config = self.config_loader.load_config(self.config_file)

            if not self.host and "base_url" in self.config:
                self.host = self.config["base_url"]

            run_init_once = self.config.get("run_init_once", False)

            if run_init_once:
                with self.__class__._init_lock:
                    if not self.__class__._init_completed:
                        logging.info(
                            "Running shared initialization (once for all users in the list)..."
                        )

                        user_list_var = self.config.get("init_list_var")
                        if user_list_var:
                            user_list = self.config.get("variables", {}).get(
                                user_list_var, []
                            )
                            if not user_list:
                                raise ValueError(
                                    f"No list found in variables['{user_list_var}'] for run_init_once mode"
                                )

                            logging.info(
                                f"Initializing {len(user_list)} users from '{user_list_var}': {user_list}"
                            )

                            for idx, user_id in enumerate(user_list):
                                logging.info(
                                    f"Initializing user {idx + 1}/{len(user_list)}: {user_id}"
                                )

                                user_flow_executor: FlowExecutor = FlowExecutor(
                                    self.config
                                )
                                user_flow_executor.context["_data_store"] = (
                                    self.__class__._data_store
                                )

                                init_steps = self.config.get("init", [])
                                for step in init_steps:
                                    user_flow_executor._execute_step(step, is_init=True)
                        else:
                            logging.info(
                                "No init_user_list specified, running init once with default context"
                            )
                            shared_flow_executor = FlowExecutor(self.config)
                            shared_flow_executor.context["_data_store"] = (
                                self.__class__._data_store
                            )

                            init_steps = self.config.get("init", [])
                            for step in init_steps:
                                shared_flow_executor._execute_step(step, is_init=True)

                            user_flow_executor = shared_flow_executor

                        self.__class__._shared_config = self.config
                        self.__class__._shared_context = (
                            user_flow_executor.get_context()
                        )
                        self.__class__._init_completed = True

                        logging.info("Shared initialization completed!")
                        logging.info(
                            f"Data store has {self.__class__._data_store.get_count()} identifiers with stored data"
                        )
                        if self.__class__._data_store.get_count() > 0:
                            logging.info(
                                f"All initialized users: {self.__class__._data_store.get_all_identifiers()}"
                            )

                self.flow_executor = FlowExecutor(self.config)
                self.flow_executor.context["_data_store"] = self.__class__._data_store
                for key, value in self.__class__._shared_context.items():
                    if not key.startswith("_"):
                        self.flow_executor.set_variable(key, value)

                logging.info(
                    f"User initialized with shared context for service: {self.config.get('service_name')}"
                )
            else:
                self.flow_executor = FlowExecutor(self.config)
                self.flow_executor.context["_data_store"] = self.__class__._data_store
                init_steps = self.config.get("init", [])
                for step in init_steps:
                    self.flow_executor._execute_step(step, is_init=True)

                logging.info(
                    f"Initialized user for service: {self.config.get('service_name')}"
                )

        except Exception as e:
            logging.error(f"Failed to initialize user: {e}")
            raise

    @task
    def execute_flow(self):
        """Execute the configured test flow."""
        if not self.flow_executor:
            return

        try:
            steps = self.config.get("steps", [])
            if not steps:
                return

            for i, step in enumerate(steps):
                step_name = step.get("name", f"Step {i + 1}")

                weight = step.get("weight", 1)

                # Cast weight to float if it's a string number
                if isinstance(weight, str):
                    try:
                        weight = float(weight)
                    except (ValueError, TypeError):
                        logging.warning(
                            f"Invalid weight '{weight}' for step '{step_name}', using default 1"
                        )
                        weight = 1

                # Validate weight range at runtime
                if not isinstance(weight, (int, float)):
                    logging.warning(
                        f"Weight must be a number for step '{step_name}', using default 1"
                    )
                    weight = 1
                elif weight < 0 or weight > 1:
                    logging.warning(
                        f"Weight {weight} is out of range (0-1) for step '{step_name}', clamping to valid range"
                    )
                    weight = max(0, min(1, weight))  # Clamp to 0-1 range

                if weight < 1 and random.random() > weight:
                    continue

                try:
                    step_result = self.flow_executor._execute_step(step, step_index=i)

                    if not step_result.get("success", True):
                        error_msg = step_result.get("error", "Unknown error")
                        logging.error(f"Step '{step_name}' failed: {error_msg}")

                except Exception as e:
                    logging.error(f"Step '{step_name}' failed: {e}")

                    if step.get("fail_fast", False):
                        break

        except Exception as e:
            logging.error(f"Flow execution failed: {e}")


def create_user_class(config_file_path: str, wait_time=None, class_name=None):
    config_loader = ConfigLoader()

    if not class_name:
        try:
            config = config_loader.load_config(config_file_path)
            service_name = config.get("service_name", "Unknown")
            class_name = f"{service_name.replace(' ', '')}User"
        except Exception as e:
            class_name = (
                f"ConfigUser_{config_file_path.replace('.', '_').replace('/', '_')}"
            )
            print(f"Warning: Could not load config for host setting: {e}")

    # Determine wait_time from config or use provided/default
    config_wait_time = None
    try:
        config = config_loader.load_config(config_file_path)

        # Check if locust config section exists
        if "locust" in config:
            locust_config = config["locust"]
            wait_time_type = locust_config.get("wait_time", "constant_throughput")

            if wait_time_type == "constant_throughput":
                throughput = locust_config.get("throughput", 1)
                config_wait_time = constant_throughput(throughput)
            elif wait_time_type == "constant":
                wait_seconds = locust_config.get("min_wait", 1)
                config_wait_time = constant(wait_seconds)
            elif wait_time_type == "between":
                min_wait = locust_config.get("min_wait", 1)
                max_wait = locust_config.get("max_wait", 3)
                config_wait_time = between(min_wait, max_wait)
            elif wait_time_type == "constant_pacing":
                pacing = locust_config.get("pacing", 1)
                config_wait_time = constant_pacing(pacing)
    except Exception as e:
        print(f"Warning: Could not load locust config: {e}")

    # Priority: provided wait_time > config wait_time > default
    final_wait_time = (
        wait_time
        if wait_time
        else (config_wait_time if config_wait_time else constant_throughput(1))
    )

    user_class = type(
        class_name,
        (ConfigDrivenUser,),
        {
            "config_file": config_file_path,
            "wait_time": final_wait_time,
            "__module__": "__main__",
        },
    )

    try:
        config = config_loader.load_config(config_file_path)
        if "base_url" in config:
            user_class.host = config["base_url"]
    except Exception:
        pass

    return user_class
