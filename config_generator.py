import yaml
import sys
from pathlib import Path


def generate_minimal_config():

    config = {
        'service_name': 'My API Service',
        'description': 'Load test configuration',
        'base_url': 'https://api.example.com',
        'headers': {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        
        'variables': {
            'username': 'test_user',
            'password': 'test_password'
        },
        
        'init': [
            {
                'name': 'Login',
                'method': 'POST',
                'endpoint': '/auth/login',
                'data': {
                    'username': '{{ username }}',
                    'password': '{{ password }}'
                },
                'extract': {
                    'auth_token': 'json.token'
                }
            }
        ],

        'steps': [
            {
                'name': 'Example GET Request',
                'method': 'GET',
                'endpoint': '/api/resource',
                'validate': {
                    'status_code': 200
                }
            },
            {
                'name': 'Example POST Request',
                'method': 'POST',
                'endpoint': '/api/resource',
                'data': {
                    'key': 'value'
                },
                'validate': {
                    'status_code': 201
                }
            }
        ]
    }
    
    return config


def save_config(config, filename=None):
    if not filename:
        default_name = config.get('service_name', 'my_service').lower().replace(' ', '_')
        filename = f"{default_name}.yaml"
    
    script_dir = Path(__file__).parent
    output_path = script_dir / "configs" / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"\nConfiguration saved to: {output_path}")
    print(f"\nEdit the file to customize:")
    print(f"   - Update endpoints and methods")
    print(f"   - Add authentication (init section)")
    print(f"   - Add variables and headers")
    print(f"   - Add plugins (encryption, random data, etc.)")
    print(f"\nRun your load test:")
    print(f"   locust -f main.py")
    print(f"\nSee README.md for full documentation")


def main():
    try:
        print("\n=== Locust Flow Config Generator ===\n")
        
        filename = input("Enter filename (without .yaml extension): ").strip()
        if not filename:
            filename = "my_api_service"
        
        if not filename.endswith('.yaml'):
            filename = f"{filename}.yaml"
        
        print(f"\nCreating config: {filename}\n")
        
        config = generate_minimal_config()
        save_config(config, filename)
        
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
