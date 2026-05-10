import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime, timedelta

# Load trained model
MODEL_PATH = 'runway_model.pkl'
if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, 'rb') as f:
        MODEL = pickle.load(f)
else:
    MODEL = None

def extract_features(transactions, current_balance):
    #Extract features from transaction history.
    df = pd.DataFrame(transactions)
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
    
    income = float(df[df['type'] == 'income']['amount'].sum())
    expenses = float(df[df['type'] == 'expense']['amount'].sum())
    daily_burn = expenses / max(len(df.groupby('date')), 1)
    
    return {
        'starting_balance': float(current_balance),
        'total_income': income,
        'total_expenses': expenses,
        'avg_daily_burn': daily_burn,
        'transaction_count': int(len(df))
    }

def predict_runway(transactions, current_balance):
    #Predict runway and return digestible results 
    if not transactions or current_balance <= 0:
        return {
            "status": "insufficient_data",
            "runway_days": None,
            "depletion_date": None,
            "current_balance": current_balance,
            "message": "Invalid input"
        }
    
    features = extract_features(transactions, current_balance)
    
    # Calculate simple runway: balance / daily burn
    daily_burn = features['avg_daily_burn']
    
    if daily_burn <= 0:
        return {
            "status": "sustainable",
            "runway_days": None,
            "depletion_date": None,
            "current_balance": current_balance,
            "daily_burn": 0.0,
            "message": "Positive cash flow — no depletion risk"
        }
    
    # Simple calculation: days until depleted
    simple_runway = int(current_balance / daily_burn) if daily_burn > 0 else 999
    
    # Cap at reasonable max (e.g., 365 days)
    runway_days = min(simple_runway, 365)
    
    # Calculate depletion date
    depletion_date = (datetime.now() + timedelta(days=runway_days)).strftime('%Y-%m-%d')
    
    # Determine status
    if runway_days <= 7:
        status = "critical"
        message = f"CRITICAL: {runway_days} days until cash depleted"
    elif runway_days <= 30:
        status = "warning"
        message = f" WARNING: {runway_days} days until cash depleted"
    elif runway_days <= 90:
        status = "caution"
        message = f"CAUTION: {runway_days} days of runway remaining"
    else:
        status = "healthy"
        message = f"HEALTHY: {runway_days}+ days of runway"
    
    
    #Determine where to cut money on the basis of the highest burn categories
    message_2 = ""
    if status in ["critical", "warning"]:
        df = pd.DataFrame(transactions)
        df['date'] = pd.to_datetime(df['date'])
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
        if 'category' in df.columns:
            expenses_df = df[df['type'] == 'expense']
            top_categories = expenses_df.groupby('category')['amount'].sum().sort_values(ascending=False).head(3)
            
            serious_categories = ['rent', 'mortgage', 'loan', 'insurance']
            serious = [cat for cat in top_categories.index if cat.lower() in serious_categories]
            other = [cat for cat in top_categories.index if cat.lower() not in serious_categories]
            
            if serious:
                message_2 = f"{message}. Review fixed costs: {', '.join(serious)}. "
            else:
                message_2 = f"{message}. "
            
            if other:
                message_2 += f"Reduce discretionary spending in: {', '.join(other)}"
    return {
        "status": status,
        "runway_days": runway_days,
        "depletion_date": depletion_date,
        "current_balance": float(current_balance),
        "daily_burn": float(daily_burn),
        "total_income": features['total_income'],
        "total_expenses": features['total_expenses'],
        "message": message,
        "message_2": message_2,
        "recommendation": get_recommendation(status, runway_days)
    }

def get_recommendation(status, runway_days):
    # Return action items based on status.
    if status == "critical":
        return "Take immediate action: reduce expenses or increase income"
    elif status == "warning":
        return "Create a budget plan to extend runway"
    elif status == "caution":
        return "Monitor spending trends"
    else:
        return "Maintain current spending patterns"