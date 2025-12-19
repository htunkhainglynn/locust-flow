import unittest
import threading
from framework.shared_data_store import SharedDataStore


class TestSharedDataStore(unittest.TestCase):
    
    def setUp(self):
        self.store = SharedDataStore()
    
    def test_store_and_get_data(self):
        """Test storing and retrieving data"""
        self.store.store("user001", {"token": "abc123", "device_id": "device001"})
        
        token = self.store.get("user001", "token")
        self.assertEqual(token, "abc123")
        
        device_id = self.store.get("user001", "device_id")
        self.assertEqual(device_id, "device001")
    
    def test_get_all_data_for_identifier(self):
        """Test retrieving all data for an identifier"""
        data = {"token": "abc123", "device_id": "device001", "session": "xyz789"}
        self.store.store("user001", data)
        
        all_data = self.store.get("user001")
        self.assertEqual(all_data, data)
    
    def test_has_data(self):
        """Test checking if data exists"""
        self.assertFalse(self.store.has_data("user001"))
        
        self.store.store("user001", {"token": "abc123"})
        self.assertTrue(self.store.has_data("user001"))
    
    def test_remove_data(self):
        """Test removing data"""
        self.store.store("user001", {"token": "abc123"})
        self.assertTrue(self.store.has_data("user001"))
        
        self.store.remove("user001")
        self.assertFalse(self.store.has_data("user001"))
    
    def test_clear_all(self):
        """Test clearing all data"""
        self.store.store("user001", {"token": "abc123"})
        self.store.store("user002", {"token": "def456"})
        
        self.store.clear_all()
        
        self.assertFalse(self.store.has_data("user001"))
        self.assertFalse(self.store.has_data("user002"))
        self.assertEqual(self.store.get_count(), 0)
    
    def test_get_all_identifiers(self):
        """Test getting all identifiers"""
        self.store.store("user001", {"token": "abc123"})
        self.store.store("user002", {"token": "def456"})
        self.store.store("user003", {"token": "ghi789"})
        
        identifiers = self.store.get_all_identifiers()
        self.assertEqual(len(identifiers), 3)
        self.assertIn("user001", identifiers)
        self.assertIn("user002", identifiers)
        self.assertIn("user003", identifiers)
    
    def test_get_count(self):
        """Test getting count of stored identifiers"""
        self.assertEqual(self.store.get_count(), 0)
        
        self.store.store("user001", {"token": "abc123"})
        self.assertEqual(self.store.get_count(), 1)
        
        self.store.store("user002", {"token": "def456"})
        self.assertEqual(self.store.get_count(), 2)
    
    def test_update_existing_data(self):
        """Test updating existing data"""
        self.store.store("user001", {"token": "abc123"})
        self.store.store("user001", {"device_id": "device001"})
        
        token = self.store.get("user001", "token")
        device_id = self.store.get("user001", "device_id")
        
        self.assertEqual(token, "abc123")
        self.assertEqual(device_id, "device001")
    
    def test_get_nonexistent_identifier(self):
        """Test getting data for non-existent identifier"""
        result = self.store.get("nonexistent")
        self.assertIsNone(result)
    
    def test_get_nonexistent_key(self):
        """Test getting non-existent key for existing identifier"""
        self.store.store("user001", {"token": "abc123"})
        result = self.store.get("user001", "nonexistent_key")
        self.assertIsNone(result)
    
    def test_thread_safety(self):
        """Test thread-safe operations"""
        def store_data(identifier, data):
            for i in range(100):
                self.store.store(identifier, {f"key_{i}": f"value_{i}"})
        
        threads = []
        for i in range(10):
            thread = threading.Thread(target=store_data, args=(f"user{i:03d}", {}))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        self.assertEqual(self.store.get_count(), 10)
    
    def test_backward_compatibility_alias(self):
        """Test TokenManager alias for backward compatibility"""
        from framework.shared_data_store import TokenManager
        
        token_manager = TokenManager()
        token_manager.store("user001", {"token": "abc123"})
        
        self.assertTrue(token_manager.has_data("user001"))
        self.assertEqual(token_manager.get("user001", "token"), "abc123")


if __name__ == '__main__':
    unittest.main()
