import glob
import os
import sys

from locust import constant_throughput

sys.path.insert(0, os.path.dirname(__file__))

from framework.locust_user import create_user_class

CONFIGS_DIR = os.path.join(os.path.dirname(__file__), "configs")
config_files = glob.glob(os.path.join(CONFIGS_DIR, "*.yaml"))
config_files.extend(glob.glob(os.path.join(CONFIGS_DIR, "*.yml")))

user_classes = {}
for config_path in config_files:
    config_file = os.path.basename(config_path)
    file_size = os.path.getsize(config_path)

    if file_size == 0:
        continue

    service_name = os.path.splitext(config_file)[0]
    class_name = "".join(word.capitalize() for word in service_name.split("_")) + "User"

    if class_name in user_classes:
        print(
            f"Warning: Duplicate class name '{class_name}' for config '{config_file}', skipping..."
        )
        continue

    user_classes[class_name] = create_user_class(
        config_file, wait_time=constant_throughput(1), class_name=class_name
    )
    globals()[class_name] = user_classes[class_name]

__all__ = list(user_classes.keys())

if __name__ == "__main__":
    print("Config-Driven Locust Framework")
    print("=" * 50)
    print(f"\nAuto-discovered {len(user_classes)} service(s) from configs/:")
    for class_name, user_class in user_classes.items():
        config_file = user_class.config_file
        print(f"  - {class_name}: {config_file}")
    print("\nTo run tests:")
    print("  locust -f main.py --class-picker")
    if user_classes:
        first_class = list(user_classes.keys())[0]
        print(f"  or")
        print(f"  locust -f main.py {first_class}")
