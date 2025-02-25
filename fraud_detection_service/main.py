# main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
import os
import logging
import json
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, DateTime, MetaData, Table, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="UPI Fraud Detection API")

# Setup CORS to allow requests from your Next.js app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set this to your Next.js app's URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the model (with error handling)
MODEL_PATH = os.getenv("MODEL_PATH", "./model/fraud_detection_model.pkl")
logger.info(f"Attempting to load model from {MODEL_PATH}")

try:
    with open(MODEL_PATH, 'rb') as file:
        model = pickle.load(file)
    logger.info(f"Model loaded successfully from {MODEL_PATH}")
    
    # Log model details for debugging
    model_type = type(model).__name__
    logger.info(f"Model type: {model_type}")
    
    # Attempt to get model features
    if hasattr(model, 'feature_names_in_'):
        feature_names = model.feature_names_in_
        logger.info(f"Model features: {feature_names}")
    else:
        logger.warning("Model doesn't have feature_names_in_ attribute")
        
    # Check if model has predict_proba method
    if hasattr(model, 'predict_proba'):
        logger.info("Model has predict_proba method")
    else:
        logger.error("Model doesn't have predict_proba method - this will cause errors")
        
except Exception as e:
    logger.error(f"Error loading model: {e}")
    model = None

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://youruser:yourpassword@postgres:5432/yourdb")
logger.info(f"Attempting to connect to database at {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    
    # Verify database connection
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        logger.info("Database connection test successful")
    
    logger.info("Database connection established")
except Exception as e:
    logger.error(f"Error connecting to database: {e}")
    engine = None
    SessionLocal = None


# Define data models
class Transaction(BaseModel):
    id: str
    user_id: str
    amount: float
    timestamp: Optional[str] = None
    receiver_id: Optional[str] = None
    device_id: Optional[str] = None
    location: Optional[str] = None
    # Add other relevant fields


class PredictionResponse(BaseModel):
    transaction_id: str
    is_fraud: bool
    confidence: float
    timestamp: str


class FeedbackRequest(BaseModel):
    transaction_id: str
    actual_is_fraud: bool


# Database dependency
def get_db():
    if SessionLocal is None:
        logger.error("Database connection not available")
        raise HTTPException(status_code=500, detail="Database connection not available")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Feature engineering function
def preprocess_transaction(transaction: Dict[str, Any]) -> pd.DataFrame:
    """
    Transform raw transaction data into features expected by the model
    """
    logger.info(f"Preprocessing transaction: {json.dumps(transaction, default=str)}")
    
    try:
        # Extract timestamp if present
        if 'timestamp' in transaction and transaction['timestamp']:
            try:
                timestamp = datetime.fromisoformat(transaction['timestamp'].replace('Z', '+00:00'))
                hour = timestamp.hour
                day_of_week = timestamp.weekday()
                logger.info(f"Extracted timestamp info: hour={hour}, day_of_week={day_of_week}")
            except Exception as e:
                logger.warning(f"Error parsing timestamp: {e}, using current time")
                timestamp = datetime.now()
                hour = timestamp.hour
                day_of_week = timestamp.weekday()
        else:
            logger.info("No timestamp provided, using current time")
            timestamp = datetime.now()
            hour = timestamp.hour
            day_of_week = timestamp.weekday()
        
        # Create features dictionary with all potential model features
        features = {
            'amount': float(transaction['amount']),
            'hour': hour,
            'day_of_week': day_of_week,
            # User frequency - in production would be calculated from historical data
            'user_id_freq': 0.01,
            # Merchant frequency - in production would be calculated from historical data
            'merchant_id_freq': 0.01,
            # Device frequency - in production would be calculated from historical data
            'device_id_freq': 0.01 if 'device_id' not in transaction else 0.005,
            # Is active hour - in production would be based on user behavior patterns
            'is_active_hour': True if 8 <= hour <= 20 else False,
            # Is preferred merchant - in production would be based on user-merchant history
            'is_preferred_merchant': False,
            # Location distance - in production would be calculated from user's usual locations
            'location_distance': 10.0 if 'location' not in transaction else float(hash(transaction['location']) % 100),
            # Transaction type flags - in production would be from the actual transaction type
            'txn_payment': 1,  # Default to payment
            'txn_transfer': 0,
            'txn_request': 0,
            'txn_bill_payment': 0
        }
        
        # Create DataFrame from features
        features_df = pd.DataFrame([features])
        logger.info(f"Created features DataFrame with columns: {features_df.columns.tolist()}")
        
        # If the model has feature_names_in_ attribute, ensure we only use those features
        if model is not None and hasattr(model, 'feature_names_in_'):
            logger.info("Aligning features with model's expected features")
            
            # Add any missing features that the model expects
            for feature in model.feature_names_in_:
                if feature not in features_df.columns:
                    logger.warning(f"Adding missing feature: {feature}")
                    features_df[feature] = 0
            
            # Only keep the features the model expects
            features_df = features_df[model.feature_names_in_]
            logger.info(f"Final features after alignment: {features_df.columns.tolist()}")
        
        # Log the actual feature values for debugging
        logger.info(f"Feature values: {features_df.to_dict(orient='records')[0]}")
        
        return features_df
        
    except Exception as e:
        logger.error(f"Error in preprocessing: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Error processing transaction data: {str(e)}")


@app.post("/predict", response_model=PredictionResponse)
async def predict_fraud(transaction: Transaction, db=Depends(get_db)):
    """
    Predict if a transaction is fraudulent
    """
    transaction_dict = transaction.dict()
    logger.info(f"Received prediction request for transaction ID: {transaction_dict['id']}")
    
    if model is None:
        logger.error("Model not loaded, cannot make prediction")
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Preprocess the transaction
        logger.info("Starting transaction preprocessing")
        features = preprocess_transaction(transaction_dict)
        logger.info("Preprocessing completed successfully")
        
        # Make prediction
        logger.info("Making prediction")
        try:
            # Get prediction probabilities
            pred_proba = model.predict_proba(features)
            logger.info(f"Raw prediction probabilities shape: {pred_proba.shape}")
            logger.info(f"Raw prediction probabilities: {pred_proba}")
            
            # Extract fraud probability (assuming binary classification where index 1 is fraud)
            # Handle the case where the shape might be different
            if pred_proba.shape[1] >= 2:
                fraud_probability = pred_proba[0][1]  # Standard scikit-learn format
            else:
                fraud_probability = pred_proba[0][0]  # Alternative format
                
            logger.info(f"Fraud probability: {fraud_probability}")
            
            # Determine if fraud based on threshold
            is_fraud = fraud_probability > 0.5
            logger.info(f"Is fraud: {is_fraud} (threshold = 0.5)")
            
        except Exception as pred_error:
            logger.error(f"Error during prediction: {pred_error}", exc_info=True)
            # Try alternative prediction method if the first fails
            logger.info("Attempting alternative prediction method")
            try:
                # For some models, predict returns the class directly
                is_fraud_raw = model.predict(features)[0]
                is_fraud = bool(is_fraud_raw)
                # Assign a dummy probability since we couldn't get the actual one
                fraud_probability = 0.9 if is_fraud else 0.1
                logger.info(f"Alternative prediction result: {is_fraud}")
            except Exception as alt_error:
                logger.error(f"Alternative prediction also failed: {alt_error}", exc_info=True)
                raise
        
        # Store prediction in database
        logger.info("Storing prediction in database")
        try:
            insert_query = """
            INSERT INTO transactions (
                transaction_id, user_id, amount, is_fraud, fraud_probability, 
                receiver_id, created_at
            ) VALUES (
                :transaction_id, :user_id, :amount, :is_fraud, :fraud_probability,
                :receiver_id, :created_at
            )
            """
            
            # Prepare parameters
            params = {
                "transaction_id": transaction.id,
                "user_id": transaction.user_id,
                "amount": transaction.amount,
                "is_fraud": is_fraud,
                "fraud_probability": float(fraud_probability),
                "receiver_id": transaction.receiver_id,
                "created_at": datetime.now()
            }
            
            logger.info(f"Database insert parameters: {json.dumps(params, default=str)}")
            
            # Execute the query
            db.execute(text(insert_query), params)
            db.commit()
            logger.info("Successfully stored prediction in database")
            
        except Exception as db_error:
            logger.error(f"Database error: {db_error}", exc_info=True)
            db.rollback()
            # Continue with response even if DB storage fails
            logger.warning("Continuing with response despite database error")
        
        # Return prediction
        response = PredictionResponse(
            transaction_id=transaction.id,
            is_fraud=bool(is_fraud),
            confidence=float(fraud_probability),
            timestamp=datetime.now().isoformat()
        )
        logger.info(f"Returning prediction response: {json.dumps(response.dict(), default=str)}")
        return response
        
    except Exception as e:
        if 'db' in locals():
            db.rollback()
        logger.error(f"Error during prediction process: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error during prediction: {str(e)}")


@app.post("/feedback")
async def record_feedback(feedback: FeedbackRequest, db=Depends(get_db)):
    """
    Record user feedback on a prediction
    """
    logger.info(f"Received feedback for transaction ID: {feedback.transaction_id}, actual_is_fraud: {feedback.actual_is_fraud}")
    
    try:
        # Store feedback
        logger.info("Storing feedback in database")
        insert_query = """
        INSERT INTO feedback (
            transaction_id, actual_is_fraud, feedback_time
        ) VALUES (
            :transaction_id, :actual_is_fraud, :feedback_time
        )
        """
        
        # Prepare parameters
        feedback_params = {
            "transaction_id": feedback.transaction_id,
            "actual_is_fraud": feedback.actual_is_fraud,
            "feedback_time": datetime.now()
        }
        
        logger.info(f"Feedback insert parameters: {json.dumps(feedback_params, default=str)}")
        
        # Execute the query
        db.execute(text(insert_query), feedback_params)
        logger.info("Successfully stored feedback")
        
        # Update the transaction record
        logger.info("Updating transaction record with feedback")
        update_query = """
        UPDATE transactions 
        SET feedback = :feedback
        WHERE transaction_id = :transaction_id
        """
        
        # Prepare parameters
        update_params = {
            "feedback": feedback.actual_is_fraud,
            "transaction_id": feedback.transaction_id
        }
        
        logger.info(f"Transaction update parameters: {json.dumps(update_params, default=str)}")
        
        # Execute the query
        result = db.execute(text(update_query), update_params)
        rows_affected = result.rowcount
        logger.info(f"Updated {rows_affected} transaction records")
        
        # Commit changes
        db.commit()
        logger.info("Successfully committed feedback changes to database")
        
        return {
            "status": "success", 
            "message": "Feedback recorded successfully",
            "rows_affected": rows_affected
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error recording feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error recording feedback: {str(e)}")


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    logger.info("Health check requested")
    
    # Check model
    model_status = model is not None
    logger.info(f"Model loaded: {model_status}")
    
    # Check database
    db_status = engine is not None
    if db_status:
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("Database connection is healthy")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            db_status = False
    
    health_response = {
        "status": "healthy" if model_status and db_status else "unhealthy",
        "model_loaded": model_status,
        "database_connected": db_status,
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"Health check response: {json.dumps(health_response, default=str)}")
    return health_response


@app.get("/model-info")
async def model_info():
    """
    Get information about the loaded model
    """
    logger.info("Model info requested")
    
    if model is None:
        logger.warning("Model not loaded, cannot provide info")
        return {"status": "error", "message": "Model not loaded"}
    
    model_info = {
        "model_type": type(model).__name__,
        "timestamp": datetime.now().isoformat()
    }
    
    # Get feature names if available
    if hasattr(model, 'feature_names_in_'):
        model_info["features"] = model.feature_names_in_.tolist()
    
    # Get feature importances if available
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        if hasattr(model, 'feature_names_in_'):
            feature_importance = {
                name: float(importance) 
                for name, importance in zip(model.feature_names_in_, importances)
            }
            model_info["feature_importances"] = feature_importance
        else:
            model_info["feature_importances"] = importances.tolist()
    
    logger.info(f"Model info response: {json.dumps(model_info, default=str)}")
    return model_info


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting fraud detection API server")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
