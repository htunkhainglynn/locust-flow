import re
from typing import Any, Dict


class TemplateEngine:
    def __init__(self):
        self.variable_pattern = re.compile(r'\{\{\s*([^}]+)\s*\}\}')
    
    def render(self, template: Any, context: Dict[str, Any]) -> Any:
        """
        Render a template with variable substitution.
        
        Args:
            template: The template to render (can be string, dict, list, etc.)
            context: Dictionary of variables for substitution
            
        Returns:
            Rendered template with variables substituted
        """
        if isinstance(template, str):
            return self._render_string(template, context)
        elif isinstance(template, dict):
            return {key: self.render(value, context) for key, value in template.items()}
        elif isinstance(template, list):
            return [self.render(item, context) for item in template]
        else:
            return template
    
    def _render_string(self, template: str, context: Dict[str, Any]) -> str:
        """Render a string template with variable substitution."""
        def replace_var(match):
            var_expr = match.group(1).strip()
            return str(self._resolve_variable(var_expr, context))
        
        return self.variable_pattern.sub(replace_var, template)
    
    def _resolve_variable(self, var_expr: str, context: Dict[str, Any]) -> Any:
        """
        Resolve a variable expression from context.
        
        Supports:
        - Simple variables: {{ var_name }}
        - Nested access: {{ response.data.id }}
        - Array access: {{ items[0] }}
        """
        try:
            # Handle simple variable names
            if '.' not in var_expr and '[' not in var_expr:
                return context.get(var_expr, f"{{{{{var_expr}}}}}")
            
            # Handle nested access
            parts = self._parse_variable_path(var_expr)
            value = context
            
            for part in parts:
                if isinstance(part, int):
                    # Array index
                    if isinstance(value, (list, tuple)) and 0 <= part < len(value):
                        value = value[part]
                    else:
                        return f"{{{{{var_expr}}}}}"
                else:
                    # Object property
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        return f"{{{{{var_expr}}}}}"
            
            return value
            
        except Exception:
            # Return original template if resolution fails
            return f"{{{{{var_expr}}}}}"
    
    @staticmethod
    def _parse_variable_path(var_expr: str) -> list:
        """Parse a variable path into components."""
        parts = []
        current = ""
        i = 0
        
        while i < len(var_expr):
            char = var_expr[i]
            
            if char == '.':
                if current:
                    parts.append(current)
                    current = ""
            elif char == '[':
                if current:
                    parts.append(current)
                    current = ""
                # Find the closing bracket
                j = i + 1
                while j < len(var_expr) and var_expr[j] != ']':
                    j += 1
                if j < len(var_expr):
                    index_str = var_expr[i+1:j]
                    try:
                        parts.append(int(index_str))
                    except ValueError:
                        parts.append(index_str.strip('"\''))
                    i = j
            else:
                current += char
            
            i += 1
        
        if current:
            parts.append(current)
        
        return parts
    
    def extract_variables(self, template: str) -> list:
        """Extract all variable names from a template string."""
        matches = self.variable_pattern.findall(template)
        return [match.strip() for match in matches]
