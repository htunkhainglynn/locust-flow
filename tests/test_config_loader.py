import unittest
import os
import tempfile
import yaml
from framework.config_loader import ConfigLoader


class TestConfigLoader(unittest.TestCase):
    
    def setUp(self):
        self.loader = ConfigLoader()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_yaml_config(self):
        """Test loading YAML configuration"""
        config_data = {
            "service_name": "Test API",
            "base_url": "https://api.test.com",
            "variables": {
                "api_key": "test123"
            },
            "steps": [
                {
                    "name": "Test Step",
                    "method": "GET",
                    "endpoint": "/test"
                }
            ]
        }
        
        config_file = os.path.join(self.temp_dir, "test_config.yaml")
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        config = self.loader.load_config(config_file)
        
        self.assertEqual(config["service_name"], "Test API")
        self.assertEqual(config["base_url"], "https://api.test.com")
        self.assertEqual(config["variables"]["api_key"], "test123")
        self.assertEqual(len(config["steps"]), 1)
    
    def test_load_json_config(self):
        """Test loading JSON configuration"""
        import json
        
        config_data = {
            "service_name": "Test API",
            "base_url": "https://api.test.com",
            "steps": [
                {
                    "name": "Test Step",
                    "method": "GET",
                    "endpoint": "/test"
                }
            ]
        }
        
        config_file = os.path.join(self.temp_dir, "test_config.json")
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        config = self.loader.load_config(config_file)
        
        self.assertEqual(config["service_name"], "Test API")
        self.assertEqual(config["base_url"], "https://api.test.com")
    
    def test_missing_config_file(self):
        """Test loading non-existent config file"""
        with self.assertRaises(FileNotFoundError):
            self.loader.load_config("/nonexistent/config.yaml")
    
    def test_invalid_yaml(self):
        """Test loading invalid YAML"""
        config_file = os.path.join(self.temp_dir, "invalid.yaml")
        with open(config_file, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        with self.assertRaises(Exception):
            self.loader.load_config(config_file)


if __name__ == '__main__':
    unittest.main()
