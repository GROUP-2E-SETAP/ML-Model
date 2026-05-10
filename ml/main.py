from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os
from predictor import predict_runway

app = FastAPI()

EXPRESS_API = os.getenv("EXPRESS_API_URL", "http://localhost:3000/api/runway")

class Transaction(BaseModel):
    date: str
    amount: float
    type: str
    category: str

class PredictRequest(BaseModel):
    currentBalance: float
    transactions: list[Transaction]

@app.post("/predict")
async def predict(data: PredictRequest):
    
    # Receive transactions and current balance Return runway prediction + recommendations.
    
    try:
        # Convert Pydantic objects to dicts
        transactions = [t.dict() for t in data.transactions]
        
        # Get prediction from ML model
        result = predict_runway(transactions, data.currentBalance)
        
        # Forward to Express backend (async, non-blocking)
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                await client.post(EXPRESS_API, json=result)
            except Exception as e:
                print(f"Warning: Failed to forward to Express: {e}")
                # Continue anyway — still return result to client
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "ml-predictor"}