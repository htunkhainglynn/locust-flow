"""Unit tests for encryption plugins (SHA256, Base64, RSA, etc.)"""

import unittest

from framework.plugins.encryption import (Base64DecodePlugin,
                                          Base64EncodePlugin, SHA256Plugin)


class TestSHA256Plugin(unittest.TestCase):
    """Test cases for SHA256Plugin"""

    def setUp(self):
        self.plugin = SHA256Plugin()

    def test_sha256_hash(self):
        """Test SHA256 hashing"""
        result = self.plugin.execute("test_data", {}, {})

        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 64)

    def test_sha256_consistency(self):
        """Test that same input produces same hash"""
        input_data = "consistent_data"

        result1 = self.plugin.execute(input_data, {}, {})
        result2 = self.plugin.execute(input_data, {}, {})

        self.assertEqual(result1, result2)

    def test_sha256_different_inputs(self):
        """Test that different inputs produce different hashes"""
        result1 = self.plugin.execute("data1", {}, {})
        result2 = self.plugin.execute("data2", {}, {})

        self.assertNotEqual(result1, result2)

    def test_sha256_empty_string(self):
        """Test hashing empty string"""
        result = self.plugin.execute("", {}, {})

        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 64)


class TestBase64Plugins(unittest.TestCase):
    """Test cases for Base64 encode/decode plugins"""

    def setUp(self):
        self.encode_plugin = Base64EncodePlugin()
        self.decode_plugin = Base64DecodePlugin()

    def test_encode_decode(self):
        """Test Base64 encoding and decoding"""
        original = "test_data_123"

        encoded = self.encode_plugin.execute(original, {}, {})
        self.assertIsInstance(encoded, str)

        decoded = self.decode_plugin.execute(encoded, {}, {})
        self.assertEqual(decoded, original)

    def test_encode_special_characters(self):
        """Test encoding special characters"""
        original = "test@#$%^&*()_+-={}[]|\\:;\"'<>,.?/"

        encoded = self.encode_plugin.execute(original, {}, {})
        decoded = self.decode_plugin.execute(encoded, {}, {})

        self.assertEqual(decoded, original)

    def test_encode_unicode(self):
        """Test encoding unicode characters"""
        original = "Hello 世界 🌍"

        encoded = self.encode_plugin.execute(original, {}, {})
        decoded = self.decode_plugin.execute(encoded, {}, {})

        self.assertEqual(decoded, original)

    def test_encode_empty_string(self):
        """Test encoding empty string"""
        original = ""

        encoded = self.encode_plugin.execute(original, {}, {})
        decoded = self.decode_plugin.execute(encoded, {}, {})

        self.assertEqual(decoded, original)

    def test_encode_long_string(self):
        """Test encoding long string"""
        original = "a" * 10000

        encoded = self.encode_plugin.execute(original, {}, {})
        decoded = self.decode_plugin.execute(encoded, {}, {})

        self.assertEqual(decoded, original)
        self.assertEqual(len(decoded), 10000)


if __name__ == "__main__":
    unittest.main()
