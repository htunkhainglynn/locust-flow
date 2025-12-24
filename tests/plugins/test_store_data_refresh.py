import unittest

from framework.plugins.generators import StoreDataPlugin
from framework.shared_data_store import SharedDataStore


class TestStoreDataRefresh(unittest.TestCase):
    """Test cases for StoreDataPlugin refresh functionality"""

    def setUp(self):
        self.plugin = StoreDataPlugin()
        self.data_store = SharedDataStore()

    def test_store_without_refresh(self):
        """Test storing data without refresh (refresh=False)"""
        context = {
            "_data_store": self.data_store,
            "token": "abc123",
            "email": "test@example.com"
        }
        config = {
            "key": "user_102",
            "values": ["token", "email"],
            "refresh": False
        }

        result = self.plugin.execute(None, config, context)
        
        # Without refresh, should return input_data (None in this case)
        self.assertIsNone(result)
        
        # But data should be stored
        self.assertTrue(self.data_store.has_data("user_102"))
        self.assertEqual(self.data_store.get("user_102", "token"), "abc123")
        self.assertEqual(self.data_store.get("user_102", "email"), "test@example.com")

    def test_store_with_refresh_true(self):
        """Test storing data with refresh enabled"""
        # Store initial data
        self.data_store.store("user_102", {
            "email_prefix": "abc123",
            "telco_code": "12"
        })

        context = {
            "_data_store": self.data_store,
            "auth_token": "token_xyz"
        }
        config = {
            "key": "user_102",
            "values": ["auth_token"],
            "refresh": True
        }

        result = self.plugin.execute(None, config, context)
        
        # With refresh, should return all stored data
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 3)
        self.assertEqual(result["email_prefix"], "abc123")
        self.assertEqual(result["telco_code"], "12")
        self.assertEqual(result["auth_token"], "token_xyz")

    def test_store_with_refresh_false_explicit(self):
        """Test storing data with refresh explicitly disabled"""
        context = {
            "_data_store": self.data_store,
            "token": "abc123"
        }
        config = {
            "key": "user_102",
            "values": ["token"],
            "refresh": False
        }

        result = self.plugin.execute(None, config, context)
        
        # Should not refresh
        self.assertIsNone(result)

    def test_refresh_accumulates_data(self):
        """Test that refresh returns accumulated data from multiple stores"""
        context = {
            "_data_store": self.data_store,
            "email": "user@example.com",
            "phone": "1234567890"
        }
        config1 = {
            "key": "user_102",
            "values": ["email", "phone"],
            "refresh": True
        }

        # First store
        result1 = self.plugin.execute(None, config1, context)
        self.assertEqual(len(result1), 2)
        self.assertIn("email", result1)
        self.assertIn("phone", result1)

        # Add more data
        context["qr_code"] = "QR_XYZ"
        config2 = {
            "key": "user_102",
            "values": ["qr_code"],
            "refresh": True
        }

        # Second store with refresh
        result2 = self.plugin.execute(None, config2, context)
        self.assertEqual(len(result2), 3)
        self.assertIn("email", result2)
        self.assertIn("phone", result2)
        self.assertIn("qr_code", result2)

        # Add even more data
        context["session_id"] = "sess_456"
        config3 = {
            "key": "user_102",
            "values": ["session_id"],
            "refresh": True
        }

        # Third store with refresh
        result3 = self.plugin.execute(None, config3, context)
        self.assertEqual(len(result3), 4)
        self.assertIn("email", result3)
        self.assertIn("phone", result3)
        self.assertIn("qr_code", result3)
        self.assertIn("session_id", result3)

    def test_refresh_with_updated_values(self):
        """Test that refresh returns updated values"""
        # Store initial token
        context = {
            "_data_store": self.data_store,
            "token": "old_token"
        }
        config = {
            "key": "user_102",
            "values": ["token"],
            "refresh": True
        }

        result1 = self.plugin.execute(None, config, context)
        self.assertEqual(result1["token"], "old_token")

        # Update token
        context["token"] = "new_token"
        result2 = self.plugin.execute(None, config, context)
        self.assertEqual(result2["token"], "new_token")

    def test_refresh_multiple_keys_independent(self):
        """Test that refresh works independently for different keys"""
        # Store data for user_102
        context1 = {
            "_data_store": self.data_store,
            "email": "user102@example.com"
        }
        config1 = {
            "key": "user_102",
            "values": ["email"],
            "refresh": True
        }
        result1 = self.plugin.execute(None, config1, context1)
        self.assertEqual(result1["email"], "user102@example.com")

        # Store data for user_103
        context2 = {
            "_data_store": self.data_store,
            "email": "user103@example.com"
        }
        config2 = {
            "key": "user_103",
            "values": ["email"],
            "refresh": True
        }
        result2 = self.plugin.execute(None, config2, context2)
        self.assertEqual(result2["email"], "user103@example.com")

        # Verify they're independent
        self.assertNotEqual(result1["email"], result2["email"])

    def test_refresh_empty_store_returns_new_data(self):
        """Test refresh on first store returns the newly stored data"""
        context = {
            "_data_store": self.data_store,
            "username": "testuser",
            "email": "test@example.com"
        }
        config = {
            "key": "user_102",
            "values": ["username", "email"],
            "refresh": True
        }

        result = self.plugin.execute(None, config, context)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 2)
        self.assertEqual(result["username"], "testuser")
        self.assertEqual(result["email"], "test@example.com")

    def test_refresh_no_data_warning(self):
        """Test refresh when no data is found logs warning"""
        context = {
            "_data_store": self.data_store
        }
        config = {
            "key": "nonexistent_key",
            "values": [],
            "refresh": True
        }

        # This should not raise an error, but log a warning
        result = self.plugin.execute(None, config, context)
        
        # Should return None when no data found
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
