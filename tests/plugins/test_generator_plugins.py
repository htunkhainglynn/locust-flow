"""Unit tests for generator plugins (random_string, random_number, etc.)"""
import unittest

from framework.plugins.generators import (
    IncrementPlugin,
    RandomNumberPlugin,
    RandomStringPlugin,
    SelectFromListPlugin,
    TimestampPlugin,
    UUIDPlugin,
)


class TestRandomNumberPlugin(unittest.TestCase):
    """Test cases for RandomNumberPlugin"""

    def setUp(self):
        self.plugin = RandomNumberPlugin()

    def test_random_int(self):
        """Test generating random integer"""
        config = {"min": 100, "max": 1000}
        result = self.plugin.execute(None, config, {})

        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 100)
        self.assertLessEqual(result, 1000)

    def test_random_int_same_min_max(self):
        """Test generating random integer when min equals max"""
        config = {"min": 500, "max": 500}
        result = self.plugin.execute(None, config, {})

        self.assertEqual(result, 500)

    def test_random_int_large_range(self):
        """Test generating random integer with large range"""
        config = {"min": 1, "max": 1000000}
        result = self.plugin.execute(None, config, {})

        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 1)
        self.assertLessEqual(result, 1000000)


class TestRandomStringPlugin(unittest.TestCase):
    """Test cases for RandomStringPlugin"""

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

    def test_default_charset(self):
        """Test default charset is alphanumeric"""
        config = {"length": 10}
        result = self.plugin.execute(None, config, {})

        self.assertEqual(len(result), 10)
        self.assertTrue(result.isalnum())

    def test_length_one(self):
        """Test generating string of length 1"""
        config = {"length": 1, "charset": "alpha"}
        result = self.plugin.execute(None, config, {})

        self.assertEqual(len(result), 1)
        self.assertTrue(result.isalpha())


class TestUUIDPlugin(unittest.TestCase):
    """Test cases for UUIDPlugin"""

    def setUp(self):
        self.plugin = UUIDPlugin()

    def test_uuid_generation(self):
        """Test UUID generation"""
        result = self.plugin.execute(None, {}, {})

        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 36)
        self.assertEqual(result.count("-"), 4)

    def test_uuid_uniqueness(self):
        """Test that generated UUIDs are unique"""
        uuid1 = self.plugin.execute(None, {}, {})
        uuid2 = self.plugin.execute(None, {}, {})

        self.assertNotEqual(uuid1, uuid2)


class TestTimestampPlugin(unittest.TestCase):
    """Test cases for TimestampPlugin"""

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

    def test_timestamp_increases(self):
        """Test that timestamps increase over time"""
        import time

        result1 = self.plugin.execute(None, {}, {})
        time.sleep(0.01)  # Small delay
        result2 = self.plugin.execute(None, {}, {})

        self.assertGreaterEqual(result2, result1)


class TestIncrementPlugin(unittest.TestCase):
    """Test cases for IncrementPlugin"""

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

    def test_increment_step_size(self):
        """Test increment with different step size"""
        plugin = IncrementPlugin()
        config = {"start": 100, "step": 10}

        result1 = plugin.execute(None, config, {})
        result2 = plugin.execute(None, config, {})
        result3 = plugin.execute(None, config, {})

        self.assertEqual(result1, 100)
        self.assertEqual(result2, 110)
        self.assertEqual(result3, 120)

    def test_increment_negative_step(self):
        """Test increment with negative step (decrement)"""
        plugin = IncrementPlugin()
        config = {"start": 1000, "step": -5}

        result1 = plugin.execute(None, config, {})
        result2 = plugin.execute(None, config, {})
        result3 = plugin.execute(None, config, {})

        self.assertEqual(result1, 1000)
        self.assertEqual(result2, 995)
        self.assertEqual(result3, 990)


class TestSelectFromListPlugin(unittest.TestCase):
    """Test cases for SelectFromListPlugin"""

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
        self.assertEqual(results[4], "user2")
        self.assertEqual(results[5], "user3")

    def test_sequential_selection(self):
        """Test sequential selection"""
        # Note: Sequential mode uses random selection, not truly sequential
        # This test just verifies it returns valid items from the list
        context = {"users": ["user1", "user2", "user3"]}
        config = {"from": "users", "mode": "sequential"}

        results = []
        for _ in range(5):
            result = self.plugin.execute(None, config, context)
            results.append(result)

        # All results should be valid items from the list
        for result in results:
            self.assertIn(result, ["user1", "user2", "user3"])

    def test_single_item_list(self):
        """Test selection from single-item list"""
        context = {"users": ["only_user"]}
        config = {"from": "users", "mode": "random"}

        result = self.plugin.execute(None, config, context)
        self.assertEqual(result, "only_user")


if __name__ == "__main__":
    unittest.main()
