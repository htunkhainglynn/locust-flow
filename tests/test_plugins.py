import unittest
from unittest.mock import MagicMock
from framework.plugins.generators import (
    RandomNumberPlugin,
    RandomStringPlugin,
    UUIDPlugin,
    TimestampPlugin,
    IncrementPlugin,
    SelectFromListPlugin,
    StoreDataPlugin
)
from framework.plugins.encryption import (
    RSAEncryptPlugin,
    SHA256Plugin,
    Base64EncodePlugin,
    Base64DecodePlugin
)


class TestRandomNumberPlugin(unittest.TestCase):
    
    def setUp(self):
        self.plugin = RandomNumberPlugin()
    
    def test_random_int(self):
        """Test generating random integer"""
        config = {"min": 100, "max": 1000}
        result = self.plugin.execute(None, config, {})
        
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 100)
        self.assertLessEqual(result, 1000)


class TestRandomStringPlugin(unittest.TestCase):
    
    def setUp(self):
        self.plugin = RandomStringPlugin()
    
    def test_alphanumeric_string(self):
        """Test generating alphanumeric string"""
        config = {"length": 10, "charset": "alphanumeric"}
        result = self.plugin.execute(None, config, {})
        
        self.assertEqual(len(result), 10)
        self.assertTrue(result.isalnum())
    
    def test_alpha_string(self):
        """Test generating alphabetic string"""
        config = {"length": 8, "charset": "alpha"}
        result = self.plugin.execute(None, config, {})
        
        self.assertEqual(len(result), 8)
        self.assertTrue(result.isalpha())
    
    def test_numeric_string(self):
        """Test generating numeric string"""
        config = {"length": 6, "charset": "numeric"}
        result = self.plugin.execute(None, config, {})
        
        self.assertEqual(len(result), 6)
        self.assertTrue(result.isdigit())


class TestUUIDPlugin(unittest.TestCase):
    
    def setUp(self):
        self.plugin = UUIDPlugin()
    
    def test_uuid_generation(self):
        """Test UUID generation"""
        result = self.plugin.execute(None, {}, {})
        
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 36)
        self.assertEqual(result.count('-'), 4)


class TestTimestampPlugin(unittest.TestCase):
    
    def setUp(self):
        self.plugin = TimestampPlugin()
    
    def test_unix_timestamp(self):
        """Test Unix timestamp generation"""
        config = {"format": "unix"}
        result = self.plugin.execute(None, config, {})
        
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)
    
    def test_default_timestamp(self):
        """Test default timestamp generation (unix)"""
        result = self.plugin.execute(None, {}, {})
        
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)


class TestIncrementPlugin(unittest.TestCase):
    
    def test_increment_basic(self):
        """Test basic increment"""
        plugin = IncrementPlugin()
        config = {"start": 1000, "step": 1}
        
        result1 = plugin.execute(None, config, {})
        result2 = plugin.execute(None, config, {})
        result3 = plugin.execute(None, config, {})
        
        self.assertEqual(result1, 1000)
        self.assertEqual(result2, 1001)
        self.assertEqual(result3, 1002)


class TestSelectFromListPlugin(unittest.TestCase):
    
    def setUp(self):
        self.plugin = SelectFromListPlugin()
    
    def test_random_selection(self):
        """Test random selection from list"""
        context = {"users": ["user1", "user2", "user3"]}
        config = {"from": "users", "mode": "random"}
        
        result = self.plugin.execute(None, config, context)
        self.assertIn(result, ["user1", "user2", "user3"])
    
    def test_round_robin_selection(self):
        """Test round-robin selection"""
        context = {"users": ["user1", "user2", "user3"]}
        config = {"from": "users", "mode": "round_robin"}
        
        results = []
        for _ in range(6):
            result = self.plugin.execute(None, config, context)
            results.append(result)
        
        self.assertEqual(results[0], "user1")
        self.assertEqual(results[1], "user2")
        self.assertEqual(results[2], "user3")
        self.assertEqual(results[3], "user1")


class TestStoreDataPlugin(unittest.TestCase):
    
    def setUp(self):
        self.plugin = StoreDataPlugin()
    
    def test_store_data(self):
        """Test storing data"""
        from framework.shared_data_store import SharedDataStore
        
        data_store = SharedDataStore()
        context = {
            "_data_store": data_store,
            "username": "user001",
            "token": "abc123",
            "device_id": "device001"
        }
        config = {
            "key": "user001",
            "values": ["token", "device_id"]
        }
        
        self.plugin.execute(None, config, context)
        
        self.assertTrue(data_store.has_data("user001"))
        self.assertEqual(data_store.get("user001", "token"), "abc123")
        self.assertEqual(data_store.get("user001", "device_id"), "device001")


class TestSHA256Plugin(unittest.TestCase):
    
    def setUp(self):
        self.plugin = SHA256Plugin()
    
    def test_sha256_hash(self):
        """Test SHA256 hashing"""
        result = self.plugin.execute("test_data", {}, {})
        
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 64)


class TestBase64Plugins(unittest.TestCase):
    
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


if __name__ == '__main__':
    unittest.main()
