import unittest

from framework.template_engine import TemplateEngine


class TestTemplateEngine(unittest.TestCase):

    def setUp(self):
        self.engine = TemplateEngine()

    def test_simple_variable_substitution(self):
        """Test simple variable substitution"""
        template = "Hello {{ name }}"
        context = {"name": "World"}

        result = self.engine.render(template, context)
        self.assertEqual(result, "Hello World")

    def test_multiple_variables(self):
        """Test multiple variable substitutions"""
        template = "{{ greeting }} {{ name }}, you have {{ count }} messages"
        context = {"greeting": "Hello", "name": "Alice", "count": 5}

        result = self.engine.render(template, context)
        self.assertEqual(result, "Hello Alice, you have 5 messages")

    def test_missing_variable(self):
        """Test missing variable returns template with spaces removed"""
        template = "Hello {{ name }}"
        context = {}

        result = self.engine.render(template, context)
        # Template engine removes spaces around variable names
        self.assertIn("{{name}}", result)

    def test_nested_dict_access(self):
        """Test nested dictionary access"""
        template = "User: {{ user.name }}, Age: {{ user.age }}"
        context = {"user": {"name": "Bob", "age": 30}}

        result = self.engine.render(template, context)
        self.assertEqual(result, "User: Bob, Age: 30")

    def test_no_template_variables(self):
        """Test template without variables"""
        template = "This is a plain string"
        context = {"name": "Test"}

        result = self.engine.render(template, context)
        self.assertEqual(result, "This is a plain string")

    def test_numeric_values(self):
        """Test numeric value substitution"""
        template = "Amount: {{ amount }}"
        context = {"amount": 1000}

        result = self.engine.render(template, context)
        self.assertEqual(result, "Amount: 1000")


if __name__ == "__main__":
    unittest.main()
