import unittest

from framework.config_validator import ConfigValidator


class TestLocustConfig(unittest.TestCase):
    def setUp(self):
        self.validator = ConfigValidator()

    def test_valid_constant_throughput_config(self):
        """Test valid constant_throughput locust config."""
        config = {
            "service_name": "Test API",
            "base_url": "https://api.example.com",
            "locust": {
                "wait_time": "constant_throughput",
                "throughput": 5,
            },
            "steps": [{"name": "Test", "method": "GET", "endpoint": "/test"}],
        }

        is_valid, errors, warnings = self.validator.validate(config)

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_valid_constant_config(self):
        """Test valid constant wait_time locust config."""
        config = {
            "service_name": "Test API",
            "base_url": "https://api.example.com",
            "locust": {
                "wait_time": "constant",
                "min_wait": 2,
            },
            "steps": [{"name": "Test", "method": "GET", "endpoint": "/test"}],
        }

        is_valid, errors, warnings = self.validator.validate(config)

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_valid_between_config(self):
        """Test valid between wait_time locust config."""
        config = {
            "service_name": "Test API",
            "base_url": "https://api.example.com",
            "locust": {
                "wait_time": "between",
                "min_wait": 1,
                "max_wait": 3,
            },
            "steps": [{"name": "Test", "method": "GET", "endpoint": "/test"}],
        }

        is_valid, errors, warnings = self.validator.validate(config)

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_valid_constant_pacing_config(self):
        """Test valid constant_pacing wait_time locust config."""
        config = {
            "service_name": "Test API",
            "base_url": "https://api.example.com",
            "locust": {
                "wait_time": "constant_pacing",
                "pacing": 5,
            },
            "steps": [{"name": "Test", "method": "GET", "endpoint": "/test"}],
        }

        is_valid, errors, warnings = self.validator.validate(config)

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_missing_throughput_for_constant_throughput(self):
        """Test that throughput is required for constant_throughput."""
        config = {
            "service_name": "Test API",
            "base_url": "https://api.example.com",
            "locust": {
                "wait_time": "constant_throughput",
            },
            "steps": [{"name": "Test", "method": "GET", "endpoint": "/test"}],
        }

        is_valid, errors, warnings = self.validator.validate(config)

        self.assertFalse(is_valid)
        self.assertTrue(any("throughput" in error.lower() for error in errors))

    def test_invalid_throughput_value(self):
        """Test that throughput must be positive."""
        config = {
            "service_name": "Test API",
            "base_url": "https://api.example.com",
            "locust": {
                "wait_time": "constant_throughput",
                "throughput": 0,
            },
            "steps": [{"name": "Test", "method": "GET", "endpoint": "/test"}],
        }

        is_valid, errors, warnings = self.validator.validate(config)

        self.assertFalse(is_valid)
        self.assertTrue(any("greater than 0" in error.lower() for error in errors))

    def test_missing_min_wait_for_constant(self):
        """Test that min_wait is required for constant."""
        config = {
            "service_name": "Test API",
            "base_url": "https://api.example.com",
            "locust": {
                "wait_time": "constant",
            },
            "steps": [{"name": "Test", "method": "GET", "endpoint": "/test"}],
        }

        is_valid, errors, warnings = self.validator.validate(config)

        self.assertFalse(is_valid)
        self.assertTrue(any("min_wait" in error.lower() for error in errors))

    def test_missing_fields_for_between(self):
        """Test that both min_wait and max_wait are required for between."""
        config = {
            "service_name": "Test API",
            "base_url": "https://api.example.com",
            "locust": {
                "wait_time": "between",
                "min_wait": 1,
            },
            "steps": [{"name": "Test", "method": "GET", "endpoint": "/test"}],
        }

        is_valid, errors, warnings = self.validator.validate(config)

        self.assertFalse(is_valid)
        self.assertTrue(any("max_wait" in error.lower() for error in errors))

    def test_min_wait_greater_than_max_wait(self):
        """Test that min_wait cannot be greater than max_wait."""
        config = {
            "service_name": "Test API",
            "base_url": "https://api.example.com",
            "locust": {
                "wait_time": "between",
                "min_wait": 5,
                "max_wait": 2,
            },
            "steps": [{"name": "Test", "method": "GET", "endpoint": "/test"}],
        }

        is_valid, errors, warnings = self.validator.validate(config)

        self.assertFalse(is_valid)
        self.assertTrue(
            any("cannot be greater than" in error.lower() for error in errors)
        )

    def test_invalid_wait_time_type(self):
        """Test that invalid wait_time type is rejected."""
        config = {
            "service_name": "Test API",
            "base_url": "https://api.example.com",
            "locust": {
                "wait_time": "invalid_type",
                "throughput": 5,
            },
            "steps": [{"name": "Test", "method": "GET", "endpoint": "/test"}],
        }

        is_valid, errors, warnings = self.validator.validate(config)

        self.assertFalse(is_valid)
        self.assertTrue(any("invalid value" in error.lower() for error in errors))

    def test_locust_config_not_dict(self):
        """Test that locust config must be a dictionary."""
        config = {
            "service_name": "Test API",
            "base_url": "https://api.example.com",
            "locust": "invalid",
            "steps": [{"name": "Test", "method": "GET", "endpoint": "/test"}],
        }

        is_valid, errors, warnings = self.validator.validate(config)

        self.assertFalse(is_valid)
        self.assertTrue(
            any("must be a dictionary" in error.lower() for error in errors)
        )

    def test_unknown_locust_field_warning(self):
        """Test that unknown locust fields generate warnings."""
        config = {
            "service_name": "Test API",
            "base_url": "https://api.example.com",
            "locust": {
                "wait_time": "constant_throughput",
                "throughput": 5,
                "unknown_field": "value",
            },
            "steps": [{"name": "Test", "method": "GET", "endpoint": "/test"}],
        }

        is_valid, errors, warnings = self.validator.validate(config)

        self.assertTrue(is_valid)
        self.assertTrue(any("unknown_field" in warning.lower() for warning in warnings))

    def test_config_without_locust_section(self):
        """Test that locust section is optional."""
        config = {
            "service_name": "Test API",
            "base_url": "https://api.example.com",
            "steps": [{"name": "Test", "method": "GET", "endpoint": "/test"}],
        }

        is_valid, errors, warnings = self.validator.validate(config)

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_negative_min_wait(self):
        """Test that min_wait cannot be negative."""
        config = {
            "service_name": "Test API",
            "base_url": "https://api.example.com",
            "locust": {
                "wait_time": "constant",
                "min_wait": -1,
            },
            "steps": [{"name": "Test", "method": "GET", "endpoint": "/test"}],
        }

        is_valid, errors, warnings = self.validator.validate(config)

        self.assertFalse(is_valid)
        self.assertTrue(any("non-negative" in error.lower() for error in errors))

    def test_missing_pacing_for_constant_pacing(self):
        """Test that pacing is required for constant_pacing."""
        config = {
            "service_name": "Test API",
            "base_url": "https://api.example.com",
            "locust": {
                "wait_time": "constant_pacing",
            },
            "steps": [{"name": "Test", "method": "GET", "endpoint": "/test"}],
        }

        is_valid, errors, warnings = self.validator.validate(config)

        self.assertFalse(is_valid)
        self.assertTrue(any("pacing" in error.lower() for error in errors))


if __name__ == "__main__":
    unittest.main()
