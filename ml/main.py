from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import httpx
import os
import logging
from predictor import predict_runway

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ML Runway Predictor", version="1.0.0")

EXPRESS_API = os.getenv("EXPRESS_API_URL", "http://localhost:3000/api/runway")

class Transaction(BaseModel):
    date: str
    amount: float
    type: str
    category: str

class PredictRequest(BaseModel):
    currentBalance: float
    transactions: list[Transaction]
    userId: str = None  # Optional: to identify the user making the request

class PredictionResponse(BaseModel):
    success: bool
    data: dict = None
    error: str = None

async def send_to_express_backend(result: dict, user_id: str = None):
    """Send prediction result to Express backend asynchronously."""
    try:
        payload = {
            "prediction": result,
            "userId": user_id,
            "timestamp": result.get("depletion_date")
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(EXPRESS_API, json=payload)
            response.raise_for_status()
            logger.info(f"Successfully sent prediction to Express backend for user: {user_id}")
    except Exception as e:
        logger.warning(f"Failed to forward prediction to Express backend: {e}")
        # Don't raise - this is non-blocking

@app.post("/predict", response_model=PredictionResponse)
async def predict(data: PredictRequest, background_tasks: BackgroundTasks):
    """
    Receive transaction data and current balance, return runway prediction.
    
    Request body:
    - currentBalance: float - current cash balance
    - transactions: list[Transaction] - array of transactions with date, amount, type, category
    - userId: optional string - user identifier
    
    Response:
    - success: bool - whether prediction was successful
    - data: dict - prediction results including runway_days, status, depletion_date, etc.
    - error: str - error message if unsuccessful
    """
    
    try:
        # Validate input
        if data.currentBalance < 0:
            raise ValueError("Current balance cannot be negative")
        
        if not data.transactions:
            raise ValueError("At least one transaction is required")
        
        logger.info(f"Processing prediction request for user: {data.userId}")
        
        # Convert Pydantic objects to dicts
        transactions = [t.dict() for t in data.transactions]
        
        # Get prediction from ML model
        result = predict_runway(transactions, data.currentBalance)
        
        # Send to Express backend asynchronously (non-blocking)
        background_tasks.add_task(
            send_to_express_backend,
            result=result,
            user_id=data.userId
        )
        
        return PredictionResponse(
            success=True,
            data=result
        )
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return PredictionResponse(
            success=False,
            error=str(e)
        )

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ml-runway-predictor",
        "version": "1.0.0",
        "express_backend": EXPRESS_API
    }