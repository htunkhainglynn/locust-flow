import unittest
from unittest.mock import Mock
from framework.flow_executor import FlowExecutor


class TestValidation(unittest.TestCase):
    """Test cases for response validation"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'service_name': 'Test Service',
            'base_url': 'https://api.test.com',
            'steps': []
        }
        self.executor = FlowExecutor(self.config)

    def test_validate_status_code_success(self):
        """Test validation passes with correct status code"""
        step = {
            'name': 'Test Step',
            'validate': {
                'status_code': 200
            }
        }
        
        response = Mock()
        response.status_code = 200
        
        # Should not raise any exception
        self.executor._validate_response(step, response)

    def test_validate_status_code_failure(self):
        """Test validation fails with incorrect status code"""
        step = {
            'name': 'Test Step',
            'validate': {
                'status_code': 200
            }
        }
        
        response = Mock()
        response.status_code = 404
        
        with self.assertRaises(AssertionError) as context:
            self.executor._validate_response(step, response)
        
        self.assertIn('Expected status 200, got 404', str(context.exception))

    def test_validate_status_code_list_success(self):
        """Test validation passes with status code in list"""
        step = {
            'name': 'Test Step',
            'validate': {
                'status_code': [200, 201, 204]
            }
        }
        
        response = Mock()
        response.status_code = 201
        
        # Should not raise any exception
        self.executor._validate_response(step, response)

    def test_validate_status_code_list_failure(self):
        """Test validation fails with status code not in list"""
        step = {
            'name': 'Test Step',
            'validate': {
                'status_code': [200, 201, 204]
            }
        }
        
        response = Mock()
        response.status_code = 404
        
        with self.assertRaises(AssertionError) as context:
            self.executor._validate_response(step, response)
        
        self.assertIn('Expected status in [200, 201, 204], got 404', str(context.exception))

    def test_validate_max_response_time_success(self):
        """Test validation passes when response time is within limit"""
        step = {
            'name': 'Test Step',
            'validate': {
                'max_response_time': 1000  # 1000ms
            }
        }
        
        response = Mock()
        response.elapsed.total_seconds.return_value = 0.5  # 500ms
        
        # Should not raise any exception
        self.executor._validate_response(step, response)

    def test_validate_max_response_time_failure(self):
        """Test validation fails when response time exceeds limit"""
        step = {
            'name': 'Test Step',
            'validate': {
                'max_response_time': 500  # 500ms
            }
        }
        
        response = Mock()
        response.elapsed.total_seconds.return_value = 1.5  # 1500ms
        
        with self.assertRaises(AssertionError) as context:
            self.executor._validate_response(step, response)
        
        self.assertIn('Response time 1500', str(context.exception))
        self.assertIn('exceeded limit 500', str(context.exception))

    def test_validate_json_field_success(self):
        """Test JSON field validation passes with correct value"""
        step = {
            'name': 'Test Step',
            'validate': {
                'json': {
                    'status': 'success',
                    'code': 200
                }
            }
        }
        
        response = Mock()
        response.json.return_value = {
            'status': 'success',
            'code': 200
        }
        
        # Should not raise any exception
        self.executor._validate_response(step, response)

    def test_validate_json_field_failure(self):
        """Test JSON field validation fails with incorrect value"""
        step = {
            'name': 'Test Step',
            'validate': {
                'json': {
                    'status': 'success'
                }
            }
        }
        
        response = Mock()
        response.json.return_value = {
            'status': 'error'
        }
        
        with self.assertRaises(AssertionError) as context:
            self.executor._validate_response(step, response)
        
        self.assertIn("JSON validation failed for 'status'", str(context.exception))
        self.assertIn('expected success, got error', str(context.exception))

    def test_validate_json_invalid_json(self):
        """Test validation fails when response is not valid JSON"""
        step = {
            'name': 'Test Step',
            'validate': {
                'json': {
                    'status': 'success'
                }
            }
        }
        
        response = Mock()
        response.json.side_effect = ValueError("Invalid JSON")
        
        with self.assertRaises(AssertionError) as context:
            self.executor._validate_response(step, response)
        
        self.assertIn('Response is not valid JSON', str(context.exception))

    def test_validate_multiple_conditions_success(self):
        """Test validation with multiple conditions all passing"""
        step = {
            'name': 'Test Step',
            'validate': {
                'status_code': 200,
                'max_response_time': 1000,
                'json': {
                    'status': 'success'
                }
            }
        }
        
        response = Mock()
        response.status_code = 200
        response.elapsed.total_seconds.return_value = 0.5
        response.json.return_value = {'status': 'success'}
        
        # Should not raise any exception
        self.executor._validate_response(step, response)

    def test_validate_list_format(self):
        """Test validation with list format (new format)"""
        step = {
            'name': 'Test Step',
            'validate': [
                {'status_code': 200},
                {'max_response_time': 1000}
            ]
        }
        
        response = Mock()
        response.status_code = 200
        response.elapsed.total_seconds.return_value = 0.5
        
        # Should not raise any exception
        self.executor._validate_response(step, response)

    def test_validate_no_validation(self):
        """Test step without validation passes"""
        step = {
            'name': 'Test Step'
        }
        
        response = Mock()
        response.status_code = 404
        
        # Should not raise any exception when no validation is specified
        self.executor._validate_response(step, response)

    def test_validate_empty_validation(self):
        """Test step with empty validation list passes"""
        step = {
            'name': 'Test Step',
            'validate': []
        }
        
        response = Mock()
        response.status_code = 404
        
        # Should not raise any exception
        self.executor._validate_response(step, response)

    # Field-based validation tests (new format)
    def test_validate_field_status_code_equals(self):
        """Test field-based validation for status code with equals condition"""
        step = {
            'name': 'Test Step',
            'validate': [
                {
                    'field': 'response.status_code',
                    'condition': 'equals',
                    'expected': '200'
                },
                {
                    'field': 'response.text',
                    'condition': 'equals',
                    'expected': 'OK'
                }
            ]
        }
        
        response = Mock()
        response.status_code = 200
        response.text = 'OK'
        response.headers = {}
        
        # Should not raise any exception
        self.executor._validate_response(step, response)

    def test_validate_field_status_code_equals_failure(self):
        """Test field-based validation fails when status code doesn't match"""
        step = {
            'name': 'Test Step',
            'validate': [
                {
                    'field': 'response.status_code',
                    'condition': 'equals',
                    'expected': '200'
                }
            ]
        }
        
        response = Mock()
        response.status_code = 404
        response.text = 'Not Found'
        response.headers = {}
        
        with self.assertRaises(AssertionError) as context:
            self.executor._validate_response(step, response)
        
        self.assertIn("Validation failed for field 'response.status_code'", str(context.exception))

    def test_validate_field_json_nested_value(self):
        """Test field-based validation for nested JSON value"""
        step = {
            'name': 'Test Step',
            'validate': [
                {
                    'field': 'response.responseMap.status',
                    'condition': 'equals',
                    'expected': 'SUCCESS'
                }
            ]
        }
        
        response = Mock()
        response.status_code = 200
        response.text = '{"responseMap": {"status": "SUCCESS"}}'
        response.headers = {}
        response.json.return_value = {
            'responseMap': {
                'status': 'SUCCESS'
            }
        }
        
        # Should not raise any exception
        self.executor._validate_response(step, response)

    def test_validate_field_json_nested_value_failure(self):
        """Test field-based validation fails for incorrect nested JSON value"""
        step = {
            'name': 'Test Step',
            'validate': [
                {
                    'field': 'response.responseMap.status',
                    'condition': 'equals',
                    'expected': 'SUCCESS'
                }
            ]
        }
        
        response = Mock()
        response.status_code = 200
        response.text = '{"responseMap": {"status": "FAILED"}}'
        response.headers = {}
        response.json.return_value = {
            'responseMap': {
                'status': 'FAILED'
            }
        }
        
        with self.assertRaises(AssertionError) as context:
            self.executor._validate_response(step, response)
        
        self.assertIn("Validation failed for field 'response.responseMap.status'", str(context.exception))

    def test_validate_field_is_not_empty(self):
        """Test field-based validation with is_not_empty condition"""
        step = {
            'name': 'Test Step',
            'validate': [
                {
                    'field': 'response.responseMap.transactionId',
                    'condition': 'is_not_empty',
                    'expected': ''
                }
            ]
        }
        
        response = Mock()
        response.status_code = 200
        response.headers = {}
        response.json.return_value = {
            'responseMap': {
                'transactionId': 'TXN123456'
            }
        }
        
        # Should not raise any exception
        self.executor._validate_response(step, response)

    def test_validate_field_contains(self):
        """Test field-based validation with contains condition"""
        step = {
            'name': 'Test Step',
            'validate': [
                {
                    'field': 'response.text',
                    'condition': 'contains',
                    'expected': 'success'
                }
            ]
        }
        
        response = Mock()
        response.status_code = 200
        response.text = 'Operation completed successfully'
        response.headers = {}
        
        # Should not raise any exception
        self.executor._validate_response(step, response)

    def test_validate_field_greater_than(self):
        """Test field-based validation with greater_than condition"""
        step = {
            'name': 'Test Step',
            'validate': [
                {
                    'field': 'response.responseMap.balance',
                    'condition': 'greater_than',
                    'expected': '0'
                }
            ]
        }
        
        response = Mock()
        response.status_code = 200
        response.headers = {}
        response.json.return_value = {
            'responseMap': {
                'balance': '1000'
            }
        }
        
        # Should not raise any exception
        self.executor._validate_response(step, response)

    def test_validate_field_with_template_variable(self):
        """Test field-based validation with template variable in expected value"""
        step = {
            'name': 'Test Step',
            'validate': [
                {
                    'field': 'response.responseMap.amount',
                    'condition': 'equals',
                    'expected': '{{ amount }}'
                }
            ]
        }
        
        # Set context variable
        self.executor.context['amount'] = '5000'
        
        response = Mock()
        response.status_code = 200
        response.headers = {}
        response.json.return_value = {
            'responseMap': {
                'amount': '5000'
            }
        }
        
        # Should not raise any exception
        self.executor._validate_response(step, response)

    def test_validate_multiple_fields(self):
        """Test multiple field-based validations"""
        step = {
            'name': 'Test Step',
            'validate': [
                {
                    'field': 'response.status_code',
                    'condition': 'equals',
                    'expected': '200'
                },
                {
                    'field': 'response.responseMap.status',
                    'condition': 'equals',
                    'expected': 'SUCCESS'
                },
                {
                    'field': 'response.responseMap.transactionId',
                    'condition': 'is_not_empty',
                    'expected': ''
                }
            ]
        }
        
        response = Mock()
        response.status_code = 200
        response.headers = {}
        response.json.return_value = {
            'responseMap': {
                'status': 'SUCCESS',
                'transactionId': 'TXN123'
            }
        }
        
        # Should not raise any exception
        self.executor._validate_response(step, response)

    def test_validate_mixed_old_and_new_format(self):
        """Test mixing old and new validation formats"""
        step = {
            'name': 'Test Step',
            'validate': [
                {'status_code': 200},  # Old format
                {  # New format
                    'field': 'response.responseMap.status',
                    'condition': 'equals',
                    'expected': 'SUCCESS'
                }
            ]
        }
        
        response = Mock()
        response.status_code = 200
        response.elapsed.total_seconds.return_value = 0.5
        response.headers = {}
        response.json.return_value = {
            'responseMap': {
                'status': 'SUCCESS'
            }
        }
        
        # Should not raise any exception
        self.executor._validate_response(step, response)


if __name__ == '__main__':
    unittest.main()
