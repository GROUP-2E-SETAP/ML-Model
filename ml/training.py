import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pickle

# Load generated training data
df = pd.read_csv('runway_training.csv')

X = df[['starting_balance', 'total_income', 'total_expenses', 'avg_daily_burn', 'transaction_count']]
y = df['runway_days']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42)
model.fit(X_train, y_train)

score = model.score(X_test, y_test)
print(f"Model R² Score: {score:.2f}")

# Save model
with open('runway_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("✓ Model saved to runway_model.pkl")