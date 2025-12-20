import unittest
from framework.config_validator import ConfigValidator, validate_config_file


class TestConfigValidator(unittest.TestCase):
    """Test cases for config validation"""

    def setUp(self):
        """Set up test fixtures"""
        self.validator = ConfigValidator()

    def test_valid_minimal_config(self):
        """Test validation passes for minimal valid config"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test Step',
                    'method': 'GET',
                    'endpoint': '/test'
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_missing_service_name(self):
        """Test validation fails when service_name is missing"""
        config = {
            'base_url': 'https://api.test.com',
            'steps': []
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('service_name' in err for err in errors))

    def test_missing_base_url(self):
        """Test validation fails when base_url is missing"""
        config = {
            'service_name': 'Test API',
            'steps': []
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('base_url' in err for err in errors))

    def test_missing_steps_and_init(self):
        """Test validation fails when both steps and init are missing"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com'
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('steps' in err or 'init' in err for err in errors))

    def test_run_init_once_without_init_list_var(self):
        """Test validation fails when run_init_once is true but init_list_var is missing"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'run_init_once': True,
            'steps': [
                {'name': 'Test', 'method': 'GET', 'endpoint': '/test'}
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('init_list_var' in err for err in errors))

    def test_run_init_once_with_nonexistent_variable(self):
        """Test validation fails when init_list_var references non-existent variable"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'run_init_once': True,
            'init_list_var': 'msisdns',
            'variables': {
                'other_var': 'value'
            },
            'steps': [
                {'name': 'Test', 'method': 'GET', 'endpoint': '/test'}
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('msisdns' in err and "doesn't exist" in err for err in errors))

    def test_run_init_once_with_non_list_variable(self):
        """Test validation fails when init_list_var is not a list"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'run_init_once': True,
            'init_list_var': 'msisdns',
            'variables': {
                'msisdns': 'not_a_list'
            },
            'steps': [
                {'name': 'Test', 'method': 'GET', 'endpoint': '/test'}
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('must be a list' in err for err in errors))

    def test_run_init_once_with_empty_list(self):
        """Test validation warns when init_list_var is empty list"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'run_init_once': True,
            'init_list_var': 'msisdns',
            'variables': {
                'msisdns': []
            },
            'steps': [
                {'name': 'Test', 'method': 'GET', 'endpoint': '/test'}
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertTrue(is_valid)
        self.assertTrue(any('empty list' in warn for warn in warnings))

    def test_run_init_once_valid_config(self):
        """Test validation passes for correct run_init_once config"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'run_init_once': True,
            'init_list_var': 'msisdns',
            'variables': {
                'msisdns': ['9765443983', '9752772627']
            },
            'init': [
                {'name': 'Login', 'method': 'POST', 'endpoint': '/login'}
            ],
            'steps': [
                {'name': 'Test', 'method': 'GET', 'endpoint': '/test'}
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_step_missing_name(self):
        """Test validation fails when step is missing name"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'method': 'GET',
                    'endpoint': '/test'
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('name' in err for err in errors))

    def test_step_missing_method(self):
        """Test validation fails when step is missing method"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test Step',
                    'endpoint': '/test'
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('method' in err for err in errors))

    def test_step_missing_endpoint(self):
        """Test validation fails when step is missing endpoint"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test Step',
                    'method': 'GET'
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('endpoint' in err for err in errors))

    def test_step_invalid_http_method(self):
        """Test validation fails for invalid HTTP method"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test Step',
                    'method': 'INVALID',
                    'endpoint': '/test'
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('Invalid HTTP method' in err for err in errors))

    def test_retry_on_missing_condition(self):
        """Test validation fails when retry_on is missing condition"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test Step',
                    'method': 'GET',
                    'endpoint': '/test',
                    'retry_on': {
                        'left': '{{ response.status_code }}',
                        'right': '401'
                    }
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('condition' in err for err in errors))

    def test_retry_on_invalid_condition(self):
        """Test validation fails for invalid retry_on condition"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test Step',
                    'method': 'GET',
                    'endpoint': '/test',
                    'retry_on': {
                        'condition': 'invalid_condition',
                        'left': '{{ response.status_code }}',
                        'right': '401'
                    }
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('Invalid condition' in err for err in errors))

    def test_retry_on_invalid_max_retries(self):
        """Test validation fails for invalid max_retries"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test Step',
                    'method': 'GET',
                    'endpoint': '/test',
                    'retry_on': {
                        'condition': 'equals',
                        'left': '{{ response.status_code }}',
                        'right': '401',
                        'max_retries': -1
                    }
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('max_retries' in err and 'positive integer' in err for err in errors))

    def test_retry_on_high_max_retries_warning(self):
        """Test validation warns for very high max_retries"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test Step',
                    'method': 'GET',
                    'endpoint': '/test',
                    'retry_on': {
                        'condition': 'equals',
                        'left': '{{ response.status_code }}',
                        'right': '401',
                        'max_retries': 20
                    }
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertTrue(is_valid)
        self.assertTrue(any('very high' in warn for warn in warnings))

    def test_validate_field_based_validation(self):
        """Test validation passes for field-based validation format"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test Step',
                    'method': 'GET',
                    'endpoint': '/test',
                    'validate': [
                        {
                            'field': 'response.status_code',
                            'condition': 'equals',
                            'expected': '200'
                        }
                    ]
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertTrue(is_valid)

    def test_validate_field_missing_condition(self):
        """Test validation fails when field validation is missing condition"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test Step',
                    'method': 'GET',
                    'endpoint': '/test',
                    'validate': [
                        {
                            'field': 'response.status_code',
                            'expected': '200'
                        }
                    ]
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('condition' in err for err in errors))

    def test_validate_field_invalid_condition(self):
        """Test validation fails for invalid validation condition"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test Step',
                    'method': 'GET',
                    'endpoint': '/test',
                    'validate': [
                        {
                            'field': 'response.status_code',
                            'condition': 'invalid_condition',
                            'expected': '200'
                        }
                    ]
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('Invalid condition' in err for err in errors))

    def test_validate_convenience_function(self):
        """Test convenience function validate_config_file"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {'name': 'Test', 'method': 'GET', 'endpoint': '/test'}
            ]
        }
        
        is_valid = validate_config_file(config)
        self.assertTrue(is_valid)

    def test_no_steps_warning(self):
        """Test validation warns when no steps are defined"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'init': [
                {'name': 'Init', 'method': 'POST', 'endpoint': '/init'}
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertTrue(is_valid)
        self.assertTrue(any('No' in warn and 'steps' in warn for warn in warnings))

    # Transform validation tests
    def test_invalid_transform_type(self):
        """Test validation fails for invalid transform type"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test',
                    'method': 'GET',
                    'endpoint': '/test',
                    'pre_transforms': [
                        {
                            'type': 'select_from_lis',  # Typo
                            'config': {'from': 'list', 'mode': 'random'},
                            'output': 'value'
                        }
                    ]
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('Invalid transform type' in err and 'select_from_lis' in err for err in errors))

    def test_select_from_list_missing_config(self):
        """Test validation fails when select_from_list is missing config"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test',
                    'method': 'GET',
                    'endpoint': '/test',
                    'pre_transforms': [
                        {
                            'type': 'select_from_list',
                            'output': 'value'
                        }
                    ]
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('requires' in err and 'config' in err for err in errors))

    def test_select_from_list_invalid_mode(self):
        """Test validation fails for invalid mode in select_from_list"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test',
                    'method': 'GET',
                    'endpoint': '/test',
                    'pre_transforms': [
                        {
                            'type': 'select_from_list',
                            'config': {
                                'from': 'list',
                                'mode': 'invalid_mode'  # Invalid
                            },
                            'output': 'value'
                        }
                    ]
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('Invalid mode' in err and 'invalid_mode' in err for err in errors))

    def test_select_from_list_missing_from(self):
        """Test validation fails when select_from_list is missing 'from' field"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test',
                    'method': 'GET',
                    'endpoint': '/test',
                    'pre_transforms': [
                        {
                            'type': 'select_from_list',
                            'config': {
                                'mode': 'random'
                            },
                            'output': 'value'
                        }
                    ]
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('from' in err for err in errors))

    def test_random_number_invalid_config(self):
        """Test validation fails for invalid random_number config"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test',
                    'method': 'GET',
                    'endpoint': '/test',
                    'pre_transforms': [
                        {
                            'type': 'random_number',
                            'config': {
                                'min': 100,
                                'max': 50  # min > max
                            },
                            'output': 'num'
                        }
                    ]
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('min' in err and 'max' in err for err in errors))

    def test_random_string_invalid_charset(self):
        """Test validation fails for invalid charset in random_string"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test',
                    'method': 'GET',
                    'endpoint': '/test',
                    'pre_transforms': [
                        {
                            'type': 'random_string',
                            'config': {
                                'length': 10,
                                'charset': 'invalid_charset'
                            },
                            'output': 'str'
                        }
                    ]
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('Invalid charset' in err for err in errors))

    def test_store_data_missing_values(self):
        """Test validation fails when store_data is missing values"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'init': [
                {
                    'name': 'Login',
                    'method': 'POST',
                    'endpoint': '/login',
                    'post_transforms': [
                        {
                            'type': 'store_data',
                            'config': {
                                'key': 'user_data'
                            }
                        }
                    ]
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('values' in err for err in errors))

    def test_rsa_encrypt_missing_fields(self):
        """Test validation fails when rsa_encrypt is missing required fields"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'init': [
                {
                    'name': 'Login',
                    'method': 'POST',
                    'endpoint': '/login',
                    'pre_transforms': [
                        {
                            'type': 'rsa_encrypt'
                        }
                    ]
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('input' in err for err in errors))
        self.assertTrue(any('output' in err for err in errors))

    def test_valid_transforms(self):
        """Test validation passes for valid transforms"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'variables': {
                'users': ['user1', 'user2']
            },
            'steps': [
                {
                    'name': 'Test',
                    'method': 'GET',
                    'endpoint': '/test',
                    'pre_transforms': [
                        {
                            'type': 'select_from_list',
                            'config': {
                                'from': 'users',
                                'mode': 'round_robin'
                            },
                            'output': 'user'
                        },
                        {
                            'type': 'random_number',
                            'config': {
                                'min': 1,
                                'max': 100
                            },
                            'output': 'amount'
                        }
                    ]
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertTrue(is_valid)

    def test_select_from_list_nonexistent_variable(self):
        """Test validation fails when 'from' references non-existent variable"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'variables': {
                'msisdns': ['123', '456']
            },
            'steps': [
                {
                    'name': 'Test',
                    'method': 'GET',
                    'endpoint': '/test',
                    'pre_transforms': [
                        {
                            'type': 'select_from_list',
                            'config': {
                                'from': 'msisdn',  # Typo - should be 'msisdns'
                                'mode': 'random'
                            },
                            'output': 'value'
                        }
                    ]
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('msisdn' in err and 'does not exist' in err for err in errors))

    def test_select_from_list_variable_not_list(self):
        """Test validation fails when 'from' references non-list variable"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'variables': {
                'msisdns': 'single_value'  # Should be a list
            },
            'steps': [
                {
                    'name': 'Test',
                    'method': 'GET',
                    'endpoint': '/test',
                    'pre_transforms': [
                        {
                            'type': 'select_from_list',
                            'config': {
                                'from': 'msisdns',
                                'mode': 'random'
                            },
                            'output': 'value'
                        }
                    ]
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('must be a list' in err for err in errors))

    # Key validation tests (typo detection)
    def test_unknown_step_key(self):
        """Test validation warns about unknown keys in step"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test',
                    'method': 'GET',
                    'endpoint': '/test',
                    'header': {'X-Test': 'value'}  # Typo - should be 'headers'
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertTrue(is_valid)  # Warning, not error
        self.assertTrue(any('Unknown field' in warn and 'header' in warn for warn in warnings))

    def test_unknown_retry_on_key(self):
        """Test validation warns about unknown keys in retry_on"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test',
                    'method': 'GET',
                    'endpoint': '/test',
                    'retry_on': {
                        'condition': 'equals',
                        'left': '{{ response.status_code }}',
                        'right': '401',
                        'max_retry': 3  # Typo - should be 'max_retries'
                    }
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertTrue(is_valid)  # Warning, not error
        self.assertTrue(any('Unknown field' in warn and 'max_retry' in warn for warn in warnings))

    def test_unknown_transform_key(self):
        """Test validation warns about unknown keys in transform"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'variables': {
                'users': ['user1', 'user2']
            },
            'steps': [
                {
                    'name': 'Test',
                    'method': 'GET',
                    'endpoint': '/test',
                    'pre_transforms': [
                        {
                            'type': 'select_from_list',
                            'conf': {  # Typo - should be 'config'
                                'from': 'users',
                                'mode': 'random'
                            },
                            'output': 'user'
                        }
                    ]
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        # Will have errors because 'config' is missing, but also warning about 'conf'
        self.assertTrue(any('Unknown field' in warn and 'conf' in warn for warn in warnings))

    def test_unknown_validation_key(self):
        """Test validation warns about unknown keys in field-based validation"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test',
                    'method': 'GET',
                    'endpoint': '/test',
                    'validate': [
                        {
                            'field': 'response.status_code',
                            'condition': 'equals',
                            'expect': '200'  # Typo - should be 'expected'
                        }
                    ]
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertTrue(is_valid)  # Warning, not error
        self.assertTrue(any('Unknown field' in warn and 'expect' in warn for warn in warnings))

    def test_unknown_top_level_key(self):
        """Test validation fails for unknown top-level keys"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'run_init_onc': True,  # Typo - should be 'run_init_once'
            'init_list_var': 'msisdns',
            'variables': {
                'msisdns': ['123', '456']
            },
            'steps': [
                {'name': 'Test', 'method': 'GET', 'endpoint': '/test'}
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)  # ERROR, not warning
        self.assertTrue(any('Invalid top-level field' in err and 'run_init_onc' in err for err in errors))

    def test_pre_request_and_pre_transforms_allowed_together(self):
        """Test validation allows both pre_request and pre_transforms together"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test',
                    'method': 'GET',
                    'endpoint': '/test',
                    'pre_request': 'some_step',
                    'pre_transforms': [
                        {'type': 'uuid', 'output': 'id'}
                    ]
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertTrue(is_valid)  # Should be valid - they can coexist

    def test_empty_pre_request(self):
        """Test validation fails when pre_request is empty"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test',
                    'method': 'GET',
                    'endpoint': '/test',
                    'pre_request': None  # Empty value
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('cannot be empty' in err and 'pre_request' in err for err in errors))

    def test_validation_typo_fiel_instead_of_field(self):
        """Test validation fails when 'fiel' is used instead of 'field'"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test',
                    'method': 'GET',
                    'endpoint': '/test',
                    'validate': [
                        {
                            'fiel': 'response.status_code',  # Typo - should be 'field'
                            'condition': 'equals',
                            'expected': 200
                        }
                    ]
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        # Should error for missing 'field' and warn about unknown 'fiel'
        self.assertTrue(any("Missing required field 'field'" in err for err in errors))
        self.assertTrue(any('Unknown field' in warn and 'fiel' in warn for warn in warnings))

    def test_weight_out_of_range(self):
        """Test validation fails when weight is out of range"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test',
                    'method': 'GET',
                    'endpoint': '/test',
                    'weight': 1.5  # Invalid - must be between 0 and 1
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('weight' in err and 'between 0 and 1' in err for err in errors))

    def test_weight_negative(self):
        """Test validation fails when weight is negative"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test',
                    'method': 'GET',
                    'endpoint': '/test',
                    'weight': -0.5  # Invalid - must be between 0 and 1
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('weight' in err and 'between 0 and 1' in err for err in errors))

    def test_weight_valid_range(self):
        """Test validation passes when weight is in valid range"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test 1',
                    'method': 'GET',
                    'endpoint': '/test1',
                    'weight': 0.5  # Valid
                },
                {
                    'name': 'Test 2',
                    'method': 'GET',
                    'endpoint': '/test2',
                    'weight': 0  # Valid - edge case
                },
                {
                    'name': 'Test 3',
                    'method': 'GET',
                    'endpoint': '/test3',
                    'weight': 1  # Valid - edge case
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertTrue(is_valid)

    def test_weight_string_number_accepted(self):
        """Test validation accepts string numbers for weight"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test 1',
                    'method': 'GET',
                    'endpoint': '/test1',
                    'weight': "0.5"  # String number - should be accepted
                },
                {
                    'name': 'Test 2',
                    'method': 'GET',
                    'endpoint': '/test2',
                    'weight': "1"  # String number - should be accepted
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertTrue(is_valid)

    def test_weight_invalid_string(self):
        """Test validation fails when weight is an invalid string"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test',
                    'method': 'GET',
                    'endpoint': '/test',
                    'weight': "invalid"  # Invalid string
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertFalse(is_valid)
        self.assertTrue(any('weight' in err and 'invalid string' in err for err in errors))

    def test_weight_template_variable_allowed(self):
        """Test validation allows template variables for weight"""
        config = {
            'service_name': 'Test API',
            'base_url': 'https://api.test.com',
            'steps': [
                {
                    'name': 'Test',
                    'method': 'GET',
                    'endpoint': '/test',
                    'weight': "{{ weight }}"  # Template variable - should be allowed
                }
            ]
        }
        
        is_valid, errors, warnings = self.validator.validate(config)
        self.assertTrue(is_valid)


if __name__ == '__main__':
    unittest.main()
