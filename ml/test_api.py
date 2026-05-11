import requests
import json

url = "http://localhost:8000/predict"
payload = {
    "currentBalance": 800,
    "userId": "user123",
    "transactions": [
        {"date": "2026-05-01", "amount": 2400, "type": "income", "category": "salary"},
        {"date": "2026-05-02", "amount": 600, "type": "expense", "category": "food"},
        {"date": "2026-05-03", "amount": 1200, "type": "expense", "category": "rent"},
        {"date": "2026-05-04", "amount": 150, "type": "expense", "category": "utilities"}
    ]
}

response = requests.post(url, json=payload)
print("Response Status:", response.status_code)
print("Response Body:")
print(json.dumps(response.json(), indent=2))