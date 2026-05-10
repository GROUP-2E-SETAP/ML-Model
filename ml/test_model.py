from predictor import predict_runway
import json

test_transactions = [
    {'date': '2026-05-01', 'amount': 2400, 'type': 'income', 'category': 'salary'},
    {'date': '2026-05-02', 'amount': 600, 'type': 'expense', 'category': 'food'},
    {'date': '2026-05-03', 'amount': 200, 'type': 'expense', 'category': 'transport'},
    {'date': '2026-05-04', 'amount': 800, 'type': 'expense', 'category': 'rent'},
    {'date': '2026-05-05', 'amount': 400, 'type': 'expense', 'category': 'utilities'},
    {'date': '2026-05-06', 'amount': 500, 'type': 'expense', 'category': 'food'},
    {'date': '2026-05-07', 'amount': 1000, 'type': 'expense', 'category': 'emergency'},
]

for balance in [300, 800, 1500, 3000]:
    result = predict_runway(test_transactions, balance)
    print(f"\n{'='*60}")
    print(f"Balance: ${balance}")
    print(f"{'='*60}")
    print(json.dumps(result, indent=2))