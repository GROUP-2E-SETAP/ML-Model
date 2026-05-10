import requests
import json

url = "http://localhost:8000/predict"
payload = {
    "currentBalance": 800,
    "transactions": [
        {"date": "2026-05-01", "amount": 2400, "type": "income", "category": "salary"},
        {"date": "2026-05-02", "amount": 600, "type": "expense", "category": "food"}
    ]
}

response = requests.post(url, json=payload)
print(json.dumps(response.json(), indent=2))