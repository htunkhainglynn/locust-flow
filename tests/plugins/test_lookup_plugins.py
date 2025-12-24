import unittest

from framework.plugins.lookup import LookupPlugin, LookupAllPlugin
from framework.plugins.datastore import GetStoreKeysPlugin
from framework.shared_data_store import SharedDataStore


class TestLookupPlugin(unittest.TestCase):
    """Test cases for LookupPlugin"""

    def setUp(self):
        self.plugin = LookupPlugin()
        self.data_store = SharedDataStore()

    def test_lookup_single_field(self):
        """Test looking up a single field from stored data"""
        # Store test data
        self.data_store.store("user_102", {
            "email_prefix": "abc123",
            "telco_code": "12",
            "phone_number": "12345678"
        })

        context = {"_data_store": self.data_store}
        config = {
            "store_key": "user_102",
            "field": "email_prefix"
        }

        result = self.plugin.execute(None, config, context)
        self.assertEqual(result, "abc123")

    def test_lookup_different_field(self):
        """Test looking up different fields from the same key"""
        self.data_store.store("user_102", {
            "email_prefix": "abc123",
            "telco_code": "12",
            "phone_number": "12345678"
        })

        context = {"_data_store": self.data_store}

        # Lookup telco_code
        config1 = {"store_key": "user_102", "field": "telco_code"}
        result1 = self.plugin.execute(None, config1, context)
        self.assertEqual(result1, "12")

        # Lookup phone_number
        config2 = {"store_key": "user_102", "field": "phone_number"}
        result2 = self.plugin.execute(None, config2, context)
        self.assertEqual(result2, "12345678")

    def test_lookup_missing_key(self):
        """Test lookup with non-existent key raises error"""
        context = {"_data_store": self.data_store}
        config = {
            "store_key": "user_999",
            "field": "email_prefix"
        }

        with self.assertRaises(ValueError) as cm:
            self.plugin.execute(None, config, context)
        
        self.assertIn("No data found in store for key: user_999", str(cm.exception))

    def test_lookup_missing_field(self):
        """Test lookup with non-existent field raises error"""
        self.data_store.store("user_102", {
            "email_prefix": "abc123",
            "telco_code": "12"
        })

        context = {"_data_store": self.data_store}
        config = {
            "store_key": "user_102",
            "field": "nonexistent_field"
        }

        with self.assertRaises(ValueError) as cm:
            self.plugin.execute(None, config, context)
        
        self.assertIn("Field 'nonexistent_field' not found", str(cm.exception))

    def test_lookup_missing_store_key_config(self):
        """Test lookup without store_key in config raises error"""
        context = {"_data_store": self.data_store}
        config = {"field": "email_prefix"}

        with self.assertRaises(ValueError) as cm:
            self.plugin.execute(None, config, context)
        
        self.assertIn("store_key not provided", str(cm.exception))

    def test_lookup_missing_field_config(self):
        """Test lookup without field in config raises error"""
        context = {"_data_store": self.data_store}
        config = {"store_key": "user_102"}

        with self.assertRaises(ValueError) as cm:
            self.plugin.execute(None, config, context)
        
        self.assertIn("field not provided", str(cm.exception))


class TestLookupAllPlugin(unittest.TestCase):
    """Test cases for LookupAllPlugin"""

    def setUp(self):
        self.plugin = LookupAllPlugin()
        self.data_store = SharedDataStore()

    def test_lookup_all_fields(self):
        """Test looking up all fields from stored data"""
        test_data = {
            "email_prefix": "abc123",
            "telco_code": "12",
            "phone_number": "12345678",
            "user_id": "102"
        }
        self.data_store.store("user_102", test_data)

        context = {"_data_store": self.data_store}
        config = {"store_key": "user_102"}

        result = self.plugin.execute(None, config, context)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 4)
        self.assertEqual(result["email_prefix"], "abc123")
        self.assertEqual(result["telco_code"], "12")
        self.assertEqual(result["phone_number"], "12345678")
        self.assertEqual(result["user_id"], "102")

    def test_lookup_all_missing_key(self):
        """Test lookup_all with non-existent key raises error"""
        context = {"_data_store": self.data_store}
        config = {"store_key": "user_999"}

        with self.assertRaises(ValueError) as cm:
            self.plugin.execute(None, config, context)
        
        self.assertIn("No data found in store for key: user_999", str(cm.exception))

    def test_lookup_all_multiple_keys(self):
        """Test lookup_all with multiple keys returns correct data"""
        self.data_store.store("user_102", {
            "email_prefix": "abc123",
            "telco_code": "12"
        })
        self.data_store.store("user_103", {
            "email_prefix": "xyz789",
            "telco_code": "15"
        })

        context = {"_data_store": self.data_store}

        # Lookup user_102
        config1 = {"store_key": "user_102"}
        result1 = self.plugin.execute(None, config1, context)
        self.assertEqual(result1["email_prefix"], "abc123")
        self.assertEqual(result1["telco_code"], "12")

        # Lookup user_103
        config2 = {"store_key": "user_103"}
        result2 = self.plugin.execute(None, config2, context)
        self.assertEqual(result2["email_prefix"], "xyz789")
        self.assertEqual(result2["telco_code"], "15")

    def test_lookup_all_missing_store_key_config(self):
        """Test lookup_all without store_key in config raises error"""
        context = {"_data_store": self.data_store}
        config = {}

        with self.assertRaises(ValueError) as cm:
            self.plugin.execute(None, config, context)
        
        self.assertIn("store_key not provided", str(cm.exception))


class TestGetStoreKeysPlugin(unittest.TestCase):
    """Test cases for GetStoreKeysPlugin"""

    def setUp(self):
        self.plugin = GetStoreKeysPlugin()
        self.data_store = SharedDataStore()

    def test_get_store_keys_empty(self):
        """Test getting keys from empty store"""
        context = {"_data_store": self.data_store}
        config = {}

        result = self.plugin.execute(None, config, context)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_get_store_keys_single(self):
        """Test getting keys with single stored item"""
        self.data_store.store("user_102", {"email": "test@example.com"})

        context = {"_data_store": self.data_store}
        config = {}

        result = self.plugin.execute(None, config, context)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("user_102", result)

    def test_get_store_keys_multiple(self):
        """Test getting keys with multiple stored items"""
        self.data_store.store("user_102", {"email": "user102@example.com"})
        self.data_store.store("user_103", {"email": "user103@example.com"})
        self.data_store.store("user_104", {"email": "user104@example.com"})

        context = {"_data_store": self.data_store}
        config = {}

        result = self.plugin.execute(None, config, context)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        self.assertIn("user_102", result)
        self.assertIn("user_103", result)
        self.assertIn("user_104", result)

    def test_get_store_keys_order(self):
        """Test that get_store_keys returns keys in consistent order"""
        keys = ["user_105", "user_102", "user_104", "user_103"]
        for key in keys:
            self.data_store.store(key, {"data": "test"})

        context = {"_data_store": self.data_store}
        config = {}

        result = self.plugin.execute(None, config, context)
        
        # Should return all keys
        self.assertEqual(len(result), 4)
        for key in keys:
            self.assertIn(key, result)

    def test_get_store_keys_no_data_store(self):
        """Test get_store_keys without data store in context raises error"""
        context = {}
        config = {}

        with self.assertRaises(ValueError) as cm:
            self.plugin.execute(None, config, context)
        
        self.assertIn("SharedDataStore not found in context", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
