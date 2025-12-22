"""
Tests for headers validation when using data field.
"""

import unittest

from framework.config_validator import ConfigValidator


class TestHeadersValidation(unittest.TestCase):
    """Test headers requirement when data field is present."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = ConfigValidator()

    def test_data_without_headers_fails(self):
        """Test that using 'data' without 'headers' fails validation."""
        config = {
            "service_name": "Test API",
            "base_url": "https://api.example.com",
            "steps": [
                {
                    "name": "Test Step",
                    "method": "POST",
                    "endpoint": "/test",
                    "data": {"key": "value"},
                }
            ],
        }

        is_valid, errors, warnings = self.validator.validate(config)

        self.assertFalse(is_valid)
        self.assertTrue(any("headers" in error.lower() for error in errors))
        self.assertTrue(any("data" in error.lower() for error in errors))

    def test_data_with_content_type_passes(self):
        """Test that using 'data' with Content-Type header passes validation."""
        config = {
            "service_name": "Test API",
            "base_url": "https://api.example.com",
            "steps": [
                {
                    "name": "Test Step",
                    "method": "POST",
                    "endpoint": "/test",
                    "headers": {"Content-Type": "application/x-www-form-urlencoded"},
                    "data": {"key": "value"},
                }
            ],
        }

        is_valid, errors, warnings = self.validator.validate(config)

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_data_with_headers_but_no_content_type_fails(self):
        """Test that using 'data' with headers but no Content-Type fails validation."""
        config = {
            "service_name": "Test API",
            "base_url": "https://api.example.com",
            "steps": [
                {
                    "name": "Test Step",
                    "method": "POST",
                    "endpoint": "/test",
                    "headers": {"Authorization": "Bearer token"},
                    "data": {"key": "value"},
                }
            ],
        }

        is_valid, errors, warnings = self.validator.validate(config)

        self.assertFalse(is_valid)
        self.assertTrue(any("content-type" in error.lower() for error in errors))

    def test_data_with_case_insensitive_content_type_passes(self):
        """Test that Content-Type header is case-insensitive."""
        config = {
            "service_name": "Test API",
            "base_url": "https://api.example.com",
            "steps": [
                {
                    "name": "Test Step",
                    "method": "POST",
                    "endpoint": "/test",
                    "headers": {"content-type": "application/x-www-form-urlencoded"},
                    "data": {"key": "value"},
                }
            ],
        }

        is_valid, errors, warnings = self.validator.validate(config)

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_json_without_headers_passes(self):
        """Test that using 'json' without 'headers' passes (headers not required for json)."""
        config = {
            "service_name": "Test API",
            "base_url": "https://api.example.com",
            "steps": [
                {
                    "name": "Test Step",
                    "method": "POST",
                    "endpoint": "/test",
                    "json": {"key": "value"},
                }
            ],
        }

        is_valid, errors, warnings = self.validator.validate(config)

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_init_step_data_without_headers_fails(self):
        """Test that init steps also require headers when using data."""
        config = {
            "service_name": "Test API",
            "base_url": "https://api.example.com",
            "init": [
                {
                    "name": "Init Step",
                    "method": "POST",
                    "endpoint": "/init",
                    "data": {"key": "value"},
                }
            ],
            "steps": [{"name": "Test Step", "method": "GET", "endpoint": "/test"}],
        }

        is_valid, errors, warnings = self.validator.validate(config)

        self.assertFalse(is_valid)
        self.assertTrue(any("headers" in error.lower() for error in errors))

    def test_multiple_steps_some_without_headers(self):
        """Test validation catches all steps missing headers when using data."""
        config = {
            "service_name": "Test API",
            "base_url": "https://api.example.com",
            "steps": [
                {
                    "name": "Step 1",
                    "method": "POST",
                    "endpoint": "/test1",
                    "headers": {"Content-Type": "application/x-www-form-urlencoded"},
                    "data": {"key": "value"},
                },
                {
                    "name": "Step 2",
                    "method": "POST",
                    "endpoint": "/test2",
                    "data": {"key": "value"},
                },
                {
                    "name": "Step 3",
                    "method": "POST",
                    "endpoint": "/test3",
                    "data": {"key": "value"},
                },
            ],
        }

        is_valid, errors, warnings = self.validator.validate(config)

        self.assertFalse(is_valid)
        # Should have 2 errors (Step 2 and Step 3)
        headers_errors = [
            e for e in errors if "headers" in e.lower() and "data" in e.lower()
        ]
        self.assertEqual(len(headers_errors), 2)


if __name__ == "__main__":
    unittest.main()
