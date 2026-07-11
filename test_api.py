import requests
import json

try:
    response = requests.get('http://localhost:5001/algorithm-info')
    print("Status Code:", response.status_code)
    print("\nResponse JSON:")
    data = response.json()
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")
