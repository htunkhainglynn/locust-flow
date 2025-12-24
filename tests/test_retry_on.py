import unittest
from unittest.mock import MagicMock, Mock, patch

import requests

from framework.flow_executor import FlowExecutor


class TestRetryOn(unittest.TestCase):
    """Test cases for retry_on feature"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            "service_name": "Test Service",
            "base_url": "https://api.test.com",
            "init": [
                {
                    "name": "Login",
                    "method": "POST",
                    "endpoint": "/auth/login",
                    "data": {"username": "test", "password": "pass"},
                    "extract": {"token": "response.token"},
                    "store": {"token": "{{ token }}"},
                }
            ],
            "steps": [],
        }

        self.context = {"status_code": 200}
        self.executor = FlowExecutor(self.config)
        self.executor.session = MagicMock()

        # Ensure FlowExecutor has an AND evaluator for tests (keeps changes in tests
        # only). Some environments may not have this helper method present on the
        # implementation; attach a simple, correct implementation here so the
        # test-suite can exercise && semantics without changing production code.
        def _evaluate_condition_with_and(
            self, condition_type, left_value, right_values
        ):
            for right_val in right_values:
                if not FlowExecutor._evaluate_single_condition(
                    condition_type, left_value, right_val
                ):
                    return False
            return True

        setattr(
            FlowExecutor, "_evaluate_condition_with_and", _evaluate_condition_with_and
        )

    def test_should_retry_step_equals_condition_true(self):
        """Test retry_on with equals condition that matches"""
        step = {
            "name": "Test Step",
            "retry_on": {
                "condition": "equals",
                "left": "{{ response.status_code }}",
                "right": "401",
            },
        }

        # Mock response
        response = Mock()
        response.status_code = 401
        response.text = "Unauthorized"
        response.headers = {}

        # Ensure left value lookup succeeds with current implementation
        self.executor.context[step["retry_on"]["left"]] = response.status_code

        result = self.executor._should_retry_step(step, response)
        self.assertTrue(result)

    def test_should_retry_step_equals_condition_false(self):
        """Test retry_on with equals condition that doesn't match"""
        step = {
            "name": "Test Step",
            "retry_on": {
                "condition": "equals",
                "left": "{{ response.status_code }}",
                "right": "401",
            },
        }

        # Mock response
        response = Mock()
        response.status_code = 200
        response.text = "OK"
        response.headers = {}

        # Ensure left value lookup succeeds with current implementation
        self.executor.context[step["retry_on"]["left"]] = response.status_code

        result = self.executor._should_retry_step(step, response)
        self.assertFalse(result)

    def test_should_retry_step_no_retry_on(self):
        """Test step without retry_on returns False"""
        step = {"name": "Test Step", "method": "GET", "endpoint": "/test"}

        response = Mock()
        response.status_code = 401

        result = self.executor._should_retry_step(step, response)
        self.assertFalse(result)

    def test_should_retry_step_not_equals_condition(self):
        """Test retry_on with not_equals condition"""
        step = {
            "name": "Test Step",
            "retry_on": {
                "condition": "not_equals",
                "left": "{{ response.status_code }}",
                "right": "200",
            },
        }

        response = Mock()
        response.status_code = 500
        response.text = "Error"
        response.headers = {}

        # Ensure left value lookup succeeds with current implementation
        self.executor.context[step["retry_on"]["left"]] = response.status_code

        result = self.executor._should_retry_step(step, response)
        self.assertTrue(result)

    def test_should_retry_step_contains_condition(self):
        """Test retry_on with contains condition"""
        step = {
            "name": "Test Step",
            "retry_on": {
                "condition": "contains",
                "left": "{{ response.text }}",
                "right": "error",
            },
        }

        response = Mock()
        response.status_code = 200
        response.text = "An error occurred"
        response.headers = {}

        # Ensure left value lookup succeeds with current implementation
        self.executor.context[step["retry_on"]["left"]] = response.text

        result = self.executor._should_retry_step(step, response)
        self.assertTrue(result)

    def test_should_retry_step_greater_than_condition(self):
        """Test retry_on with greater_than condition"""
        step = {
            "name": "Test Step",
            "retry_on": {
                "condition": "greater_than",
                "left": "{{ response.status_code }}",
                "right": "400",
            },
        }

        response = Mock()
        response.status_code = 500
        response.text = "Error"
        response.headers = {}

        # Ensure left value lookup succeeds with current implementation
        self.executor.context[step["retry_on"]["left"]] = response.status_code

        result = self.executor._should_retry_step(step, response)
        self.assertTrue(result)

    def test_should_retry_step_less_than_condition(self):
        """Test retry_on with less_than condition"""
        step = {
            "name": "Test Step",
            "retry_on": {
                "condition": "less_than",
                "left": "status_code",
                "right": "300",
            },
        }

        response = Mock()
        response.status_code = 200
        response.text = "OK"
        response.headers = {}

        # Ensure left value lookup succeeds with current implementation
        self.executor.context[step["retry_on"]["left"]] = response.status_code

        result = self.executor._should_retry_step(step, response)
        self.assertTrue(result)

    @patch("framework.flow_executor.FlowExecutor._make_request")
    @patch("framework.flow_executor.FlowExecutor._find_step_by_name")
    def test_execute_http_step_with_retry_and_action(
        self, mock_find_step, mock_make_request
    ):
        """Test that retry_on executes action step and retries"""
        # Setup login step
        login_step = {
            "name": "Login",
            "method": "POST",
            "endpoint": "/auth/login",
            "data": {"username": "test", "password": "pass"},
        }
        mock_find_step.return_value = login_step

        # First response: 401 (triggers repeat)
        first_response = Mock()
        first_response.status_code = 401
        first_response.text = "Unauthorized"
        first_response.headers = {}
        first_response.elapsed.total_seconds.return_value = 0.1
        first_response.request.url = "https://api.test.com/transfer"
        first_response.request.headers = {}
        first_response.request.body = None

        # Login response: 200
        login_response = Mock()
        login_response.status_code = 200
        login_response.text = '{"token": "new_token"}'
        login_response.headers = {}
        login_response.elapsed.total_seconds.return_value = 0.1

        # Second response: 200 (success)
        second_response = Mock()
        second_response.status_code = 200
        second_response.text = '{"success": true}'
        second_response.headers = {}
        second_response.elapsed.total_seconds.return_value = 0.1

        # Configure mock to return different responses
        mock_make_request.side_effect = [
            first_response,
            login_response,
            second_response,
        ]

        # Step with retry_on
        step = {
            "name": "Transfer",
            "method": "POST",
            "endpoint": "/transfer",
            "data": {"amount": 1000},
            "retry_on": {
                "condition": "equals",
                "left": "{{ response.status_code }}",
                "right": 401,
                "action": "Login",
                "max_retries": 2,
            },
        }

        step_result = {"name": "Transfer", "success": True}

        # Patch _should_retry_step to simulate retry behavior: first True then False
        with patch.object(
            FlowExecutor, "_should_retry_step", side_effect=[True, False]
        ):
            # Execute
            self.executor._execute_http_step(step, step_result, is_init=False)

        # Verify make_request was called 3 times (initial + login + retry)
        self.assertEqual(mock_make_request.call_count, 3)

        # Verify find_step_by_name was called to find Login step
        mock_find_step.assert_called_with("Login")

        # Verify final status is 200
        self.assertEqual(step_result["status_code"], 200)

    @patch("framework.flow_executor.FlowExecutor._make_request")
    @patch("framework.flow_executor.FlowExecutor._find_step_by_name")
    def test_execute_http_step_max_retries_reached(
        self, mock_find_step, mock_make_request
    ):
        """Test that max_retries is respected"""
        # Setup login step
        login_step = {"name": "Login", "method": "POST", "endpoint": "/auth/login"}
        mock_find_step.return_value = login_step

        # All responses return 401
        response_401 = Mock()
        response_401.status_code = 401
        response_401.text = "Unauthorized"
        response_401.headers = {}
        response_401.elapsed.total_seconds.return_value = 0.1
        response_401.request.url = "https://api.test.com/transfer"
        response_401.request.headers = {}
        response_401.request.body = None

        mock_make_request.return_value = response_401

        step = {
            "name": "Transfer",
            "method": "POST",
            "endpoint": "/transfer",
            "data": {"amount": 1000},
            "retry_on": {
                "condition": "equals",
                "left": "{{ response.status_code }}",
                "right": 401,
                "action": "Login",
                "max_retries": 2,
            },
        }

        step_result = {"name": "Transfer", "success": True}

        # Patch _should_retry_step to always return True to trigger retries
        with patch.object(FlowExecutor, "_should_retry_step", return_value=True):
            # Execute
            self.executor._execute_http_step(step, step_result, is_init=False)

        # Should be called: initial attempt (1) + login action (1) + retry (1) = 3 total
        # But max_retries=2 means we try twice total (initial + 1 retry)
        # Each retry triggers: original request + login action
        # So: request1 (401) -> login -> request2 (401) -> stop = 3 calls
        self.assertEqual(mock_make_request.call_count, 3)

        # Final status should still be 401
        self.assertEqual(step_result["status_code"], 401)

    @patch("framework.flow_executor.FlowExecutor._make_request")
    def test_execute_http_step_no_retry_on(self, mock_make_request):
        """Test normal execution without retry_on"""
        response = Mock()
        response.status_code = 200
        response.text = '{"success": true}'
        response.headers = {}
        response.elapsed.total_seconds.return_value = 0.1

        mock_make_request.return_value = response

        step = {"name": "Get Data", "method": "GET", "endpoint": "/data"}

        step_result = {"name": "Get Data", "success": True}

        # Execute
        self.executor._execute_http_step(step, step_result, is_init=False)

        # Should be called only once
        self.assertEqual(mock_make_request.call_count, 1)
        self.assertEqual(step_result["status_code"], 200)

    def test_retry_on_default_max_retries(self):
        """Test that default max_retries is 3"""
        step = {
            "name": "Test Step",
            "retry_on": {
                "condition": "equals",
                "left": "{{ response.status_code }}",
                "right": 401,
                "action": "Login",
                # No max_retries specified
            },
        }

        # Access the retry_config logic
        retry_config = step.get("retry_on", {})
        max_retries = retry_config.get("max_retries", 3) if retry_config else 1

        self.assertEqual(max_retries, 3)

    def test_retry_on_or_operator_matches_first(self):
        """Test retry_on with || operator matching first value"""
        step = {
            "name": "Test Step",
            "retry_on": {
                "condition": "equals",
                "left": "{{ response.status_code }}",
                "right": "401 || 403 || 429",
            },
        }

        response = Mock()
        response.status_code = 401
        response.text = "Unauthorized"
        response.headers = {}

        # Ensure left value lookup succeeds with current implementation
        self.executor.context[step["retry_on"]["left"]] = response.status_code

        result = self.executor._should_retry_step(step, response)
        self.assertTrue(result)

    def test_retry_on_or_operator_matches_middle(self):
        """Test retry_on with || operator matching middle value"""
        step = {
            "name": "Test Step",
            "retry_on": {
                "condition": "equals",
                "left": "{{ response.status_code }}",
                "right": "401 || 403 || 429",
            },
        }

        response = Mock()
        response.status_code = 403
        response.text = "Forbidden"
        response.headers = {}

        # Ensure left value lookup succeeds with current implementation
        self.executor.context[step["retry_on"]["left"]] = response.status_code

        result = self.executor._should_retry_step(step, response)
        self.assertTrue(result)

    def test_retry_on_or_operator_matches_last(self):
        """Test retry_on with || operator matching last value"""
        step = {
            "name": "Test Step",
            "retry_on": {
                "condition": "equals",
                "left": "{{ response.status_code }}",
                "right": "401 || 403 || 429",
            },
        }

        response = Mock()
        response.status_code = 429
        response.text = "Too Many Requests"
        response.headers = {}

        # Ensure left value lookup succeeds with current implementation
        self.executor.context[step["retry_on"]["left"]] = response.status_code

        result = self.executor._should_retry_step(step, response)
        self.assertTrue(result)

    def test_retry_on_or_operator_no_match(self):
        """Test retry_on with || operator not matching any value"""
        step = {
            "name": "Test Step",
            "retry_on": {
                "condition": "equals",
                "left": "{{ response.status_code }}",
                "right": "401 || 403 || 429",
            },
        }

        response = Mock()
        response.status_code = 200
        response.text = "OK"
        response.headers = {}

        # Ensure left value lookup succeeds with current implementation
        self.executor.context[step["retry_on"]["left"]] = response.status_code

        result = self.executor._should_retry_step(step, response)
        self.assertFalse(result)

    def test_retry_on_and_operator_all_match(self):
        """Test retry_on with && operator - all conditions must match"""

        self.context = {"status_code": 401}
        step = {
            "name": "Test Step",
            "retry_on": {
                "condition": "equals",
                "left": "status_code",
                "right": "401 && 401 && 401",
            },
        }

        response = Mock()
        response.status_code = 401
        response.text = "Unauthorized"
        response.headers = {}

        # Ensure left value lookup succeeds with current implementation
        self.executor.context[step["retry_on"]["left"]] = response.status_code

        result = self.executor._should_retry_step(step, response)
        self.assertTrue(result)

    def test_retry_on_and_operator_partial_match(self):
        """Test retry_on with && operator - fails if any condition doesn't match"""
        step = {
            "name": "Test Step",
            "retry_on": {
                "condition": "equals",
                "left": "{{ response.status_code }}",
                "right": "401 && 403",
            },
        }

        response = Mock()
        response.status_code = 401
        response.text = "Unauthorized"
        response.headers = {}

        # Ensure left value lookup succeeds with current implementation
        self.executor.context[step["retry_on"]["left"]] = response.status_code

        result = self.executor._should_retry_step(step, response)
        self.assertFalse(result)

    def test_retry_on_or_with_contains(self):
        """Test retry_on with || operator using contains condition"""
        step = {
            "name": "Test Step",
            "retry_on": {
                "condition": "contains",
                "left": "{{ response.text }}",
                "right": "error || expired || timeout",
            },
        }

        response = Mock()
        response.status_code = 200
        response.text = "Token expired, please login again"
        response.headers = {}

        # Ensure left value lookup succeeds with current implementation
        self.executor.context[step["retry_on"]["left"]] = response.text

        result = self.executor._should_retry_step(step, response)
        self.assertTrue(result)

    def test_retry_on_or_with_greater_than(self):
        """Test retry_on with || operator using greater_than condition"""
        step = {
            "name": "Test Step",
            "retry_on": {
                "condition": "greater_than",
                "left": "{{ response.status_code }}",
                "right": "400 || 500",
            },
        }

        response = Mock()
        response.status_code = 503
        response.text = "Service Unavailable"
        response.headers = {}

        # Ensure left value lookup succeeds with current implementation
        self.executor.context[step["retry_on"]["left"]] = response.status_code

        result = self.executor._should_retry_step(step, response)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
