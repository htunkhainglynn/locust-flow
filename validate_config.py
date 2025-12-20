#!/usr/bin/env python3
"""
Config Validator CLI Tool

Usage:
    python validate_config.py <config_file>
    python validate_config.py configs/*.yaml
"""
import sys
import os
import glob
import yaml
import json
from framework.config_validator import ConfigValidator


def load_config_file(config_path: str):
    """Load a config file (YAML or JSON)."""
    with open(config_path, 'r', encoding='utf-8') as f:
        if config_path.endswith('.yaml') or config_path.endswith('.yml'):
            return yaml.safe_load(f)
        elif config_path.endswith('.json'):
            return json.load(f)
        else:
            # Try YAML first
            try:
                return yaml.safe_load(f)
            except yaml.YAMLError:
                f.seek(0)
                return json.load(f)


def validate_file(config_path: str) -> bool:
    """Validate a single config file."""
    print(f"\n{'='*60}")
    print(f"Validating: {config_path}")
    print('='*60)
    
    try:
        config = load_config_file(config_path)
        validator = ConfigValidator()
        is_valid, errors, warnings = validator.validate(config, config_path)
        
        if is_valid:
            print("[VALID] Config is valid")
            if warnings:
                print(f"\n[WARNING] {len(warnings)} Warning(s):")
                for warning in warnings:
                    print(f"  - {warning}")
        else:
            print("[INVALID] Config is invalid")
            print(f"\n[ERROR] {len(errors)} Error(s):")
            for error in errors:
                print(f"  - {error}")
            if warnings:
                print(f"\n[WARNING] {len(warnings)} Warning(s):")
                for warning in warnings:
                    print(f"  - {warning}")
        
        return is_valid
        
    except FileNotFoundError:
        print(f"[ERROR] File not found: {config_path}")
        return False
    except Exception as e:
        print(f"[ERROR] Error loading config: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_config.py <config_file> [config_file2 ...]")
        print("\nExamples:")
        print("  python validate_config.py configs/my-api.yaml")
        print("  python validate_config.py configs/*.yaml")
        sys.exit(1)
    
    # Expand glob patterns
    config_files = []
    for arg in sys.argv[1:]:
        if '*' in arg or '?' in arg:
            config_files.extend(glob.glob(arg))
        else:
            config_files.append(arg)
    
    if not config_files:
        print("[ERROR] No config files found")
        sys.exit(1)
    
    print(f"\nValidating {len(config_files)} config file(s)...")
    
    results = {}
    for config_file in config_files:
        results[config_file] = validate_file(config_file)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    
    valid_count = sum(1 for v in results.values() if v)
    invalid_count = len(results) - valid_count
    
    print(f"Total: {len(results)} file(s)")
    print(f"Valid: {valid_count}")
    print(f"Invalid: {invalid_count}")
    
    if invalid_count > 0:
        print("\n[ERROR] Invalid files:")
        for file, is_valid in results.items():
            if not is_valid:
                print(f"  - {file}")
        sys.exit(1)
    else:
        print("\n[SUCCESS] All config files are valid!")
        sys.exit(0)


if __name__ == '__main__':
    main()
