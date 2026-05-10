
import pandas as pd
import numpy as np

def calculate_runway(daily_net_flows, starting_balance):
    """Calculate days until balance hits zero."""
    balance = starting_balance
    for day_idx, net in enumerate(daily_net_flows):
        balance += net
        if balance <= 0:
            return day_idx
    return 999

# Load real transaction data
df = pd.read_csv('train.csv', skiprows=1)
df.columns = ['date', 'amount', 'type', 'category']
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.dropna(subset=['date'])
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
df = df.dropna(subset=['amount'])
df['net'] = np.where(df['type'] == 'income', df['amount'], -df['amount'])

# Split by month to get different user profiles
training_data = []
for month in df['date'].dt.to_period('M').unique():
    month_data = df[df['date'].dt.to_period('M') == month]
    daily_flows = month_data.groupby('date')['net'].sum().values.astype(float)
    
    income = daily_flows[daily_flows > 0].sum()
    expenses = abs(daily_flows[daily_flows < 0].sum())
    
    # Generate samples for each user profile with different starting balances
    for start_bal in [100, 300, 500, 800, 1200, 1500, 2000, 3000, 5000]:
        runway = calculate_runway(daily_flows, start_bal)
        
        training_data.append({
            'starting_balance': start_bal,
            'total_income': income,
            'total_expenses': expenses,
            'avg_daily_burn': abs(daily_flows[daily_flows < 0].mean()),
            'transaction_count': len(daily_flows),
            'runway_days': runway
        })

train_df = pd.DataFrame(training_data)
train_df.to_csv('runway_training.csv', index=False)
print(f"Generated {len(train_df)} training samples from realistic user profiles")
print(train_df)
print(f"\nRunway distribution: min={train_df['runway_days'].min()}, max={train_df['runway_days'].max()}")
print(f"Depletion cases: {(train_df['runway_days'] < 999).sum()}")