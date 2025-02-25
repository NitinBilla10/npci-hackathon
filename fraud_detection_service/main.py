from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import pickle
import pandas as pd
import numpy as np
import os
from datetime import datetime
from catboost import CatBoostClassifier

# Initialize FastAPI app
app = FastAPI(title="Credit Card Fraud Detection API")

# Setup CORS to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the model (with error handling)
MODEL_PATH = os.getenv("MODEL_PATH", "../model/catboost_model.pkl")
try:
    with open(MODEL_PATH, 'rb') as file:
        model = pickle.load(file)
    print(f"CatBoost model loaded successfully from {MODEL_PATH}")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Define data models
class Transaction(BaseModel):
    # Match the expected features by the model
    User: str  # User ID
    Card: str  # Card number
    Year: int
    Month: int
    Day: int
    Time: str  # HH:MM format
    Amount: str  # Including $ sign like "$147.83"
    Use_Chip: str  # "Swipe Transaction" or "Chip Transaction"
    Merchant_Name: str
    Merchant_City: str
    Merchant_State: str
    Zip: Optional[float] = None
    MCC: Optional[str] = None  # Merchant Category Code
    is_fraud: Optional[bool] = None  # For the provided data, but not required for prediction

class PredictionResponse(BaseModel):
    transaction_id: str
    is_fraud: bool
    confidence: float
    timestamp: str

class BulkTransactions(BaseModel):
    transactions: List[Transaction] = Field(..., min_items=1, description="List of transactions to analyze")

class PredictionResult(BaseModel):
    transaction_id: str
    is_fraud: bool
    confidence: float

class BulkPredictionResponse(BaseModel):
    results: List[PredictionResult]
    timestamp: str
    processed_count: int

def map_use_chip(use_chip: str) -> str:
    """
    Map the Use_Chip input to the format expected by the model
    """
    # This mapping may need adjustment based on the actual training data
    if "chip" in use_chip.lower():
        return "Chip Transaction"
    elif "swipe" in use_chip.lower():
        return "Swipe Transaction"
    elif "online" in use_chip.lower():
        return "Online Transaction"
    else:
        return use_chip

# Feature engineering function
def preprocess_transaction(transaction: Dict[str, Any]) -> pd.DataFrame:
    """
    Transform a single transaction data into features expected by the CatBoost model
    """
    try:
        # Create a DataFrame with the expected columns
        features = pd.DataFrame([{
            'User': transaction['User'],
            'Card': transaction['Card'],
            'Year': int(transaction['Year']),
            'Month': int(transaction['Month']),
            'Day': int(transaction['Day']),
            'Amount': transaction['Amount'],
            'Zip': float(transaction['Zip']) if transaction['Zip'] is not None else np.nan,
            'MCC': transaction['MCC'] if transaction['MCC'] is not None else '',
            'Merchant Name': transaction['Merchant_Name'],
            'Use Chip_Online Transaction': map_use_chip(transaction['Use_Chip'])
        }])
        
        # Convert Amount from string to float (remove $ sign)
        features['Amount'] = features['Amount'].str.replace('$', '', regex=False).astype(float)
        
        # Convert string columns to appropriate data types
        features['User'] = features['User'].astype(int)
        features['Card'] = features['Card'].astype(int)
        features['MCC'] = pd.to_numeric(features['MCC'], errors='coerce').fillna(0).astype(int)
        
        # No need to convert categorical variables to numeric codes
        # CatBoost can handle categorical features directly
        
        print(f"Processed features: {features.to_dict(orient='records')}")
        print(f"Feature dtypes: {features.dtypes}")
        return features
    except Exception as e:
        print(f"Error in preprocessing: {e}")
        raise HTTPException(status_code=400, detail=f"Error processing transaction data: {str(e)}")

def preprocess_transactions_batch(transactions: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Transform multiple transactions into features expected by the CatBoost model
    """
    try:
        # Create a list to hold all transaction data
        all_features = []
        
        # Process each transaction
        for transaction in transactions:
            features_dict = {
                'User': transaction['User'],
                'Card': transaction['Card'],
                'Year': int(transaction['Year']),
                'Month': int(transaction['Month']),
                'Day': int(transaction['Day']),
                'Amount': transaction['Amount'].replace('$', '', 1) if isinstance(transaction['Amount'], str) else str(transaction['Amount']),
                'Zip': float(transaction['Zip']) if transaction['Zip'] is not None else np.nan,
                'MCC': transaction['MCC'] if transaction['MCC'] is not None else '',
                'Merchant Name': transaction['Merchant_Name'],
                'Use Chip_Online Transaction': map_use_chip(transaction['Use_Chip'])
            }
            all_features.append(features_dict)
        
        # Convert to DataFrame
        features_df = pd.DataFrame(all_features)
        
        # Convert columns to appropriate data types
        features_df['Amount'] = pd.to_numeric(features_df['Amount'], errors='coerce')
        features_df['User'] = pd.to_numeric(features_df['User'], errors='coerce').fillna(0).astype(int)
        features_df['Card'] = pd.to_numeric(features_df['Card'], errors='coerce').fillna(0).astype(int)
        features_df['MCC'] = pd.to_numeric(features_df['MCC'], errors='coerce').fillna(0).astype(int)
        
        print(f"Processed batch with {len(all_features)} transactions")
        print(f"Feature dtypes: {features_df.dtypes}")
        return features_df
    except Exception as e:
        print(f"Error in batch preprocessing: {e}")
        raise HTTPException(status_code=400, detail=f"Error processing transaction batch: {str(e)}")

@app.post("/predict", response_model=PredictionResponse)
async def predict_fraud(transaction: Transaction):
    """
    Predict if a transaction is fraudulent
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Generate a transaction ID if not provided
        transaction_id = f"tx_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Preprocess the transaction
        features = preprocess_transaction(transaction.dict())
        
        # Make prediction
        # CatBoost uses predict_proba similar to XGBoost
        prediction_result = model.predict_proba(features)
        
        # Check if prediction_result has more than one column (binary classification)
        if prediction_result.shape[1] > 1:
            fraud_probability = prediction_result[0, 1]  # Probability of class 1 (fraud)
        else:
            # If output is a single column, interpret directly
            fraud_probability = prediction_result[0, 0]
            
        is_fraud = fraud_probability > 0.5  # Threshold can be adjusted
        print(f"Fraud probability: {fraud_probability}, is_fraud: {is_fraud}")
        
        # Return prediction
        return PredictionResponse(
            transaction_id=transaction_id,
            is_fraud=bool(is_fraud),
            confidence=float(fraud_probability),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        print(f"Error during prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Error during prediction: {str(e)}")

@app.post("/predict-batch", response_model=BulkPredictionResponse)
async def predict_fraud_batch(bulk_data: BulkTransactions):
    """
    Predict if multiple transactions are fraudulent
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        start_time = datetime.now()
        
        # Extract transactions
        transactions = [tx.dict() for tx in bulk_data.transactions]
        
        # Generate transaction IDs
        for i, tx in enumerate(transactions):
            tx['transaction_id'] = f"batch_tx_{start_time.strftime('%Y%m%d%H%M%S')}_{i+1}"
        
        # Preprocess all transactions at once
        features = preprocess_transactions_batch(transactions)
        
        # Make predictions
        batch_prediction_result = model.predict_proba(features)
        
        # Process results
        results = []
        for i, tx in enumerate(transactions):
            # Get probability of fraud (class 1)
            if batch_prediction_result.shape[1] > 1:
                fraud_probability = batch_prediction_result[i, 1]
            else:
                fraud_probability = batch_prediction_result[i, 0]
                
            is_fraud = fraud_probability > 0.5  # Threshold can be adjusted
            
            results.append(PredictionResult(
                transaction_id=tx['transaction_id'],
                is_fraud=bool(is_fraud),
                confidence=float(fraud_probability)
            ))
        
        # Return prediction results
        return BulkPredictionResponse(
            results=results,
            timestamp=datetime.now().isoformat(),
            processed_count=len(results)
        )
    except Exception as e:
        print(f"Error during batch prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Error during batch prediction: {str(e)}")

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_type": "CatBoost" if model is not None else None,
        "endpoints": ["predict", "predict-batch", "health"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)