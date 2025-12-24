import unittest

from framework.plugins.generators import AppendToListPlugin


class TestAppendToListPlugin(unittest.TestCase):
    """Test cases for AppendToListPlugin"""

    def setUp(self):
        self.plugin = AppendToListPlugin()

    def test_append_to_empty_list(self):
        """Test appending to a list that doesn't exist yet"""
        context = {}
        config = {
            "list_var": "my_list",
            "value": "item1"
        }

        result = self.plugin.execute(None, config, context)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "item1")
        self.assertIn("my_list", context)
        self.assertEqual(context["my_list"], ["item1"])

    def test_append_to_existing_list(self):
        """Test appending to an existing list"""
        context = {"my_list": ["item1", "item2"]}
        config = {
            "list_var": "my_list",
            "value": "item3"
        }

        result = self.plugin.execute(None, config, context)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        self.assertEqual(result, ["item1", "item2", "item3"])
        self.assertEqual(context["my_list"], ["item1", "item2", "item3"])

    def test_append_multiple_values(self):
        """Test appending multiple values sequentially"""
        context = {}
        config = {"list_var": "numbers"}

        # Append first value
        config["value"] = 1
        self.plugin.execute(None, config, context)
        self.assertEqual(context["numbers"], [1])

        # Append second value
        config["value"] = 2
        self.plugin.execute(None, config, context)
        self.assertEqual(context["numbers"], [1, 2])

        # Append third value
        config["value"] = 3
        self.plugin.execute(None, config, context)
        self.assertEqual(context["numbers"], [1, 2, 3])

    def test_append_different_types(self):
        """Test appending different data types"""
        context = {"mixed_list": []}
        
        # Append string
        config1 = {"list_var": "mixed_list", "value": "string"}
        self.plugin.execute(None, config1, context)
        
        # Append number
        config2 = {"list_var": "mixed_list", "value": 123}
        self.plugin.execute(None, config2, context)
        
        # Append dict
        config3 = {"list_var": "mixed_list", "value": {"key": "value"}}
        self.plugin.execute(None, config3, context)
        
        self.assertEqual(len(context["mixed_list"]), 3)
        self.assertEqual(context["mixed_list"][0], "string")
        self.assertEqual(context["mixed_list"][1], 123)
        self.assertEqual(context["mixed_list"][2], {"key": "value"})

    def test_append_to_multiple_lists(self):
        """Test appending to different lists independently"""
        context = {}
        
        # Append to list1
        config1 = {"list_var": "list1", "value": "a"}
        self.plugin.execute(None, config1, context)
        
        # Append to list2
        config2 = {"list_var": "list2", "value": "x"}
        self.plugin.execute(None, config2, context)
        
        # Append to list1 again
        config3 = {"list_var": "list1", "value": "b"}
        self.plugin.execute(None, config3, context)
        
        self.assertEqual(context["list1"], ["a", "b"])
        self.assertEqual(context["list2"], ["x"])

    def test_append_user_ids(self):
        """Test appending user IDs (real-world use case)"""
        context = {"registered_user_ids": []}
        
        # Simulate registering 5 users
        for i in range(102, 107):
            config = {
                "list_var": "registered_user_ids",
                "value": f"user_{i}"
            }
            self.plugin.execute(None, config, context)
        
        self.assertEqual(len(context["registered_user_ids"]), 5)
        self.assertEqual(context["registered_user_ids"], [
            "user_102", "user_103", "user_104", "user_105", "user_106"
        ])

    def test_missing_list_var(self):
        """Test error when list_var is not provided"""
        context = {}
        config = {"value": "item1"}

        with self.assertRaises(ValueError) as cm:
            self.plugin.execute(None, config, context)
        
        self.assertIn("'list_var' is required", str(cm.exception))

    def test_missing_value(self):
        """Test error when value is not provided"""
        context = {}
        config = {"list_var": "my_list"}

        with self.assertRaises(ValueError) as cm:
            self.plugin.execute(None, config, context)
        
        self.assertIn("'value' is required", str(cm.exception))

    def test_value_none_explicit(self):
        """Test error when value is explicitly None"""
        context = {}
        config = {
            "list_var": "my_list",
            "value": None
        }

        with self.assertRaises(ValueError) as cm:
            self.plugin.execute(None, config, context)
        
        self.assertIn("'value' is required", str(cm.exception))

    def test_append_to_non_list_variable(self):
        """Test error when trying to append to a non-list variable"""
        context = {"my_var": "not_a_list"}
        config = {
            "list_var": "my_var",
            "value": "item1"
        }

        with self.assertRaises(ValueError) as cm:
            self.plugin.execute(None, config, context)
        
        self.assertIn("is not a list", str(cm.exception))

    def test_append_duplicate_values(self):
        """Test that duplicate values are allowed"""
        context = {"my_list": ["item1"]}
        config = {
            "list_var": "my_list",
            "value": "item1"
        }

        result = self.plugin.execute(None, config, context)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result, ["item1", "item1"])


if __name__ == "__main__":
    unittest.main()
