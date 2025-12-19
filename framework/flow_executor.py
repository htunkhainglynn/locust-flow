import json
import logging
import requests
from typing import Dict, Any, List, Optional
from .template_engine import TemplateEngine
from .plugins.registry import plugin_registry

try:
    from locust import events

    LOCUST_AVAILABLE = True
except ImportError:
    LOCUST_AVAILABLE = False


class FlowExecutor:

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.template_engine = TemplateEngine()
        self.context = {}
        self.session = requests.Session()
        self.base_url = config.get('base_url', '')
        self.default_headers = config.get('headers', {})
        self.context.update(config.get('variables', {}))

        if self.default_headers:
            self.session.headers.update(self.default_headers)

    def execute_flow(self) -> Dict[str, Any]:
        """Execute the complete test flow."""
        results = {
            'service_name': self.config.get('service_name'),
            'steps': [],
            'success': True,
            'error': None
        }

        try:
            steps = self.config.get('steps', [])
            for i, step in enumerate(steps):
                step_result = self._execute_step(step, step_index=i)
                results['steps'].append(step_result)

                if not step_result.get('success', True):
                    results['success'] = False
                    if step.get('fail_fast', True):
                        break

        except Exception as e:
            results['success'] = False
            results['error'] = str(e)
            logging.error(f"Flow execution failed: {e}")

        return results

    def _execute_step(self, step: Dict[str, Any], step_index: int = 0, is_init: bool = False) -> Dict[str, Any]:
        """

        :rtype: Dict[str, Any]
        """
        step_result = {
            'name': step.get('name', f'Step {step_index + 1}'),
            'success': True,
            'response_time': 0,
            'status_code': None,
            'error': None,
            'skipped': False
        }

        try:
            self._execute_pre_requests(step.get('pre_request', []))
            self._apply_transforms(step.get('pre_transforms', []))

            if self._should_skip_step(step):
                step_result['skipped'] = True
                logging.info(f"Step '{step_result['name']}' skipped due to skip_if condition")
                return step_result

            self._execute_http_step(step, step_result, is_init=is_init)

            self._apply_transforms(step.get('post_transforms', []))

        except Exception as e:
            step_result['success'] = False
            step_result['error'] = str(e)
            logging.error(f"Step '{step_result['name']}' failed: {e}")

        return step_result

    def _execute_http_step(self, step: Dict[str, Any], step_result: Dict[str, Any], is_init: bool) -> None:
        retry_config = step.get('retry_on', {})
        max_retries = retry_config.get('max_retries', 3) if retry_config else 1
        retry_count = 0
        
        while retry_count < max_retries:
            response = self._make_request(step)
            step_result['status_code'] = response.status_code
            step_result['response_time'] = response.elapsed.total_seconds() * 1000

            if is_init:
                logging.info(
                    f"Init step '{step_result['name']}' - Status: {response.status_code}, Response Time: {step_result['response_time']:.0f}ms")
                if response.status_code >= 400:
                    logging.error(f"Init step '{step_result['name']}' failed!")
                    logging.error(f"Request URL: {response.request.url}")
                    logging.error(f"Request Headers: {dict(response.request.headers)}")
                    if response.request.body:
                        logging.error(f"Request Body: {response.request.body[:500]}")
                    logging.error(f"Response Body: {response.text[:500]}")
                else:
                    logging.debug(f"Init response body: {response.text[:500]}...")
            else:
                logging.info(
                    f"Step '{step_result['name']}' - Status: {response.status_code}, Response Time: {step_result['response_time']:.0f}ms")
                logging.debug(f"Response body: {response.text[:500]}...")

            self._extract_variables(step, response)
            
            # Check if we should retry this step
            if self._should_retry_step(step, response):
                retry_count += 1
                if retry_count < max_retries:
                    retry_config = step.get('retry_on', {})
                    action_step = retry_config.get('action')
                    if action_step:
                        logging.info(f"Retry condition met, executing action: '{action_step}' (attempt {retry_count + 1}/{max_retries})")
                        referenced_step = self._find_step_by_name(action_step)
                        if referenced_step:
                            action_response = self._make_request(referenced_step)
                            self._extract_variables(referenced_step, action_response)
                            self._validate_response(referenced_step, action_response)
                        else:
                            logging.warning(f"Action step '{action_step}' not found")
                    continue
                else:
                    logging.warning(f"Max retries ({max_retries}) reached for step '{step_result['name']}'")
                    break
            else:
                break
        
        self._validate_response(step, response)

    def _make_request(self, step: Dict[str, Any]) -> requests.Response:
        method = step['method'].upper()
        url = self._build_url(step['endpoint'])

        headers: Dict[str, Any] = {}
        headers.update(self.default_headers)
        if 'headers' in step:
            rendered_headers = self.template_engine.render(step['headers'], self.context)
            headers.update(rendered_headers)

        request_kwargs = self._build_request_kwargs(step, headers)
        clean_kwargs = {k: v for k, v in request_kwargs.items() if not k.startswith('_')}
        response = self.session.request(method, url, **clean_kwargs)

        self.context['last_response'] = {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'text': response.text
        }

        try:
            self.context['last_response']['json'] = response.json()
        except Exception:
            pass

        self._fire_locust_event(step, response, method, url)

        return response

    def _build_url(self, endpoint: str) -> str:
        if endpoint.startswith('http://') or endpoint.startswith('https://'):
            return self.template_engine.render(endpoint, self.context)
        return self.template_engine.render(f"{self.base_url}{endpoint}", self.context)

    def _build_request_kwargs(self, step: Dict[str, Any], headers: Dict[str, Any]) -> Dict[str, Any]:
        request_kwargs: Dict[str, Any] = {
            'headers': headers,
            'timeout': step.get('timeout', 30)
        }

        if 'data' in step:
            rendered_data = self.template_engine.render(step['data'], self.context)
            content_type = headers.get('Content-Type', '')

            if 'application/json' in content_type:
                request_kwargs['json'] = rendered_data
                request_kwargs['_data_format'] = 'json'
            elif 'application/x-www-form-urlencoded' in content_type:
                request_kwargs['data'] = rendered_data
                request_kwargs['_data_format'] = 'form'
            else:
                request_kwargs['data'] = rendered_data
                request_kwargs['_data_format'] = 'form'

        if 'params' in step:
            rendered_params = self.template_engine.render(step['params'], self.context)
            request_kwargs['params'] = rendered_params

        return request_kwargs

    @staticmethod
    def _fire_locust_event(step: Dict[str, Any], response, method: str, url: str):
        if not LOCUST_AVAILABLE:
            return

        step_name = step.get('name', 'Unknown Step')
        response_time = getattr(response, 'elapsed', None)
        if response_time:
            response_time_ms = int(response_time.total_seconds() * 1000)
        else:
            response_time_ms = 0

        expected_status = step.get('validate', {}).get('status_code', 200)
        if isinstance(expected_status, list):
            success = response.status_code in expected_status
        else:
            success = response.status_code == expected_status

        if success:
            events.request.fire(
                request_type=method,
                name=step_name,
                response_time=response_time_ms,
                response_length=len(response.text) if hasattr(response, 'text') else 0,
            )
        else:
            events.request.fire(
                request_type=method,
                name=step_name,
                response_time=response_time_ms,
                response_length=len(response.text) if hasattr(response, 'text') else 0,
                exception=f"Status {response.status_code} != {expected_status}"
            )

    def _apply_transforms(self, transforms: List[Dict[str, Any]]):
        for transform in transforms:
            transform_type = transform.get('type')
            if not transform_type:
                continue

            input_data = self.template_engine.render(transform.get('input', ''), self.context)
            config = transform.get('config', {})
            rendered_config = self.template_engine.render(config, self.context)

            try:
                result = plugin_registry.execute_plugin(transform_type, input_data, rendered_config, self.context)
                output_var = transform.get('output')
                if output_var:
                    self.context[output_var] = result

            except Exception as e:
                logging.error(f"Transform '{transform_type}' failed: {e}")

    def _extract_variables(self, step: Dict[str, Any], response: requests.Response):
        extracts = step.get('extract', {})

        for var_name, extract_config in extracts.items():
            try:
                path = None

                if isinstance(extract_config, str):
                    path = extract_config
                    value = self._extract_value(response, extract_config)
                elif isinstance(extract_config, dict):
                    extract_type = extract_config.get('type', 'json')
                    path = extract_config.get('path', '')

                    if extract_type == 'json':
                        value = self._extract_json_value(response, path)
                    elif extract_type == 'header':
                        value = response.headers.get(path)
                    elif extract_type == 'regex':
                        import re
                        pattern = extract_config.get('pattern', '')
                        match = re.search(pattern, response.text)
                        value = match.group(1) if match else None
                    else:
                        value = None
                else:
                    value = None

                if value is not None:
                    self.context[var_name] = value
                    logging.debug(f"Extracted variable '{var_name}' = '{str(value)[:100]}...' from path '{path}'")
                else:
                    logging.debug(f"Failed to extract variable '{var_name}' from path '{path}' - value is None")

            except Exception as e:
                logging.error(f"Variable extraction for '{var_name}' failed: {e}")

    @staticmethod
    def _extract_value(response: requests.Response, path: str):
        if path.startswith('json.'):
            json_path = path[5:]
            return FlowExecutor._extract_json_value(response, json_path)
        elif path.startswith('header.'):
            header_name = path[7:]
            return response.headers.get(header_name)
        elif path.startswith('headers.'):
            header_name = path[8:]
            logging.debug(f"Looking for header '{header_name}' in response headers: {dict(response.headers)}")
            return response.headers.get(header_name)
        elif path == 'status_code':
            return response.status_code
        elif path == 'text':
            return response.text
        else:
            return None

    @staticmethod
    def _extract_json_value(response: requests.Response, path: str):
        try:
            data = response.json()
            if not path:
                return data

            parts = path.split('.')
            for part in parts:
                if isinstance(data, dict):
                    data = data.get(part)
                elif isinstance(data, list) and part.isdigit():
                    index = int(part)
                    data = data[index] if 0 <= index < len(data) else None
                else:
                    return None

            return data
        except Exception:
            return None

    @staticmethod
    def _validate_response(step: Dict[str, Any], response: requests.Response):
        validations = step.get('validate', [])

        if isinstance(validations, list):
            validation_dict = {}
            for validation in validations:
                if isinstance(validation, dict):
                    validation_dict.update(validation)
            validations = validation_dict

        fail_on_error = validations.get('fail_on_error', False)
        expected_status = validations.get('status_code')
        if expected_status:
            if isinstance(expected_status, list):
                if response.status_code not in expected_status:
                    raise AssertionError(f"Expected status in {expected_status}, got {response.status_code}")
            elif response.status_code != expected_status:
                raise AssertionError(f"Expected status {expected_status}, got {response.status_code}")

        max_response_time = validations.get('max_response_time')
        if max_response_time:
            response_time_ms = response.elapsed.total_seconds() * 1000
            if response_time_ms > max_response_time:
                raise AssertionError(f"Response time {response_time_ms}ms exceeded limit {max_response_time}ms")

        json_validations = validations.get('json', {})
        if json_validations:
            try:
                json_data = response.json()
                for path, expected_value in json_validations.items():
                    actual_value = FlowExecutor._extract_json_value(response, path)
                    if actual_value != expected_value:
                        raise AssertionError(
                            f"JSON validation failed for '{path}': expected {expected_value}, got {actual_value}")
            except json.JSONDecodeError:
                raise AssertionError("Response is not valid JSON")

    def get_context(self) -> Dict[str, Any]:
        """Get current execution context."""
        return self.context.copy()

    def set_variable(self, name: str, value: Any):
        """Set a variable in the execution context."""
        self.context[name] = value

    def _execute_pre_requests(self, pre_requests: List[Any]):
        if not pre_requests:
            return

        for pre_request in pre_requests:
            if isinstance(pre_request, str):
                referenced_step = self._find_step_by_name(pre_request)
                if referenced_step:
                    logging.debug(f"Executing pre-request: '{pre_request}' (referenced step)")
                    response = self._make_request(referenced_step)
                    self._extract_variables(referenced_step, response)
                    self._validate_response(referenced_step, response)
                else:
                    logging.warning(f"Pre-request step '{pre_request}' not found")
            elif isinstance(pre_request, dict):
                step_name = pre_request.get('name', 'Inline Pre-request')
                logging.debug(f"Executing pre-request: '{step_name}' (inline)")
                response = self._make_request(pre_request)
                self._extract_variables(pre_request, response)
                if 'validate' in pre_request:
                    self._validate_response(pre_request, response)

    def _find_step_by_name(self, step_name: str) -> Optional[Any]:
        init_steps = self.config.get('init', [])
        for step in init_steps:
            if step.get('name') == step_name:
                return step

        # Search in main steps
        main_steps = self.config.get('steps', [])
        for step in main_steps:
            if step.get('name') == step_name:
                return step

        return None

    def _should_skip_step(self, step: Dict[str, Any]) -> bool:
        skip_if = step.get('skip_if')
        if not skip_if:
            return False

        condition_type = skip_if.get('condition')
        left_value = self.template_engine.render(skip_if.get('left', ''), self.context)
        right_value = self.template_engine.render(skip_if.get('right', ''), self.context)

        if condition_type == 'equals':
            return left_value == right_value
        elif condition_type == 'not_equals':
            return left_value != right_value
        elif condition_type == 'contains':
            return str(right_value) in str(left_value)
        elif condition_type == 'not_contains':
            return str(right_value) not in str(left_value)
        elif condition_type == 'greater_than':
            try:
                return float(left_value) > float(right_value)
            except (ValueError, TypeError):
                return False
        elif condition_type == 'less_than':
            try:
                return float(left_value) < float(right_value)
            except (ValueError, TypeError):
                return False
        elif condition_type == 'is_empty':
            return not left_value or left_value == '' or left_value == [] or left_value == {}
        elif condition_type == 'is_not_empty':
            return bool(left_value) and left_value != '' and left_value != [] and left_value != {}

        return False

    def _should_retry_step(self, step: Dict[str, Any], response: requests.Response) -> bool:
        """Check if a step should be retried based on retry_on condition."""
        retry_on = step.get('retry_on')
        if not retry_on:
            return False

        condition_type = retry_on.get('condition')
        left_value = retry_on.get('left', '')
        right_value = retry_on.get('right', '')
        
        # Store response in context for template rendering
        self.context['response'] = {
            'status_code': response.status_code,
            'text': response.text,
            'headers': dict(response.headers)
        }
        
        # Render template variables
        left_value = self.template_engine.render(str(left_value), self.context)
        right_value = self.template_engine.render(str(right_value), self.context)

        # Check for logical operators in right value
        if '||' in str(right_value):
            # OR logic: check if left matches any of the right values
            right_values = [v.strip() for v in str(right_value).split('||')]
            return self._evaluate_condition_with_or(condition_type, left_value, right_values)
        elif '&&' in str(right_value):
            # AND logic: check if left matches all right values
            right_values = [v.strip() for v in str(right_value).split('&&')]
            return self._evaluate_condition_with_and(condition_type, left_value, right_values)
        else:
            # Single condition
            return self._evaluate_single_condition(condition_type, left_value, right_value)

    @staticmethod
    def _evaluate_single_condition(condition_type: str, left_value: Any, right_value: Any) -> bool:
        """Evaluate a single condition."""
        if condition_type == 'equals':
            return str(left_value) == str(right_value)
        elif condition_type == 'not_equals':
            return str(left_value) != str(right_value)
        elif condition_type == 'contains':
            return str(right_value) in str(left_value)
        elif condition_type == 'not_contains':
            return str(right_value) not in str(left_value)
        elif condition_type == 'greater_than':
            try:
                return float(left_value) > float(right_value)
            except (ValueError, TypeError):
                return False
        elif condition_type == 'less_than':
            try:
                return float(left_value) < float(right_value)
            except (ValueError, TypeError):
                return False

        return False

    def _evaluate_condition_with_or(self, condition_type: str, left_value: Any, right_values: list) -> bool:
        """Evaluate condition with OR logic - returns True if ANY condition matches."""
        for right_val in right_values:
            if self._evaluate_single_condition(condition_type, left_value, right_val):
                return True
        return False
    
    def _evaluate_condition_with_and(self, condition_type: str, left_value: Any, right_values: list) -> bool:
        """Evaluate condition with AND logic - returns True if ALL conditions match."""
        for right_val in right_values:
            if not self._evaluate_single_condition(condition_type, left_value, right_val):
                return False
        return True
