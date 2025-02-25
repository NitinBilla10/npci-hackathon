# retrain_model.py
import os
import pickle
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import shutil

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://youruser:yourpassword@postgres:5432/yourdb")
MODEL_PATH = os.getenv("MODEL_PATH", "./model/fraud_detection_model.pkl")
BACKUP_DIR = os.getenv("BACKUP_DIR", "./model/backups")
DAYS_OF_DATA = int(os.getenv("DAYS_OF_DATA", 30))

# Ensure backup directory exists
os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_current_model():
    """Create a backup of the current model"""
    if not os.path.exists(MODEL_PATH):
        logger.warning(f"No existing model found at {MODEL_PATH}")
        return False
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"model_backup_{timestamp}.pkl")
    
    try:
        shutil.copy2(MODEL_PATH, backup_path)
        logger.info(f"Model backed up to {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to backup model: {e}")
        return False

def get_training_data():
    """Fetch labeled transaction data from the database"""
    try:
        # Connect to database
        engine = create_engine(DATABASE_URL)
        
        # Query to get transactions with feedback
        query = text(f"""
            SELECT t.*, f.actual_is_fraud
            FROM transactions t
            JOIN feedback f ON t.transaction_id = f.transaction_id
            WHERE f.feedback_time > NOW() - INTERVAL '{DAYS_OF_DATA} days'
            AND f.used_for_training = FALSE
        """)
        
        # Execute query and load into DataFrame
        with engine.connect() as connection:
            df = pd.read_sql(query, connection)
            
            # Mark feedback as used for training
            if not df.empty:
                update_query = text("""
                    UPDATE feedback
                    SET used_for_training = TRUE
                    WHERE transaction_id IN :transaction_ids
                """)
                connection.execute(update_query, {"transaction_ids": tuple(df['transaction_id'].tolist())})
                connection.commit()
                
        logger.info(f"Fetched {len(df)} transactions with feedback for retraining")
        return df
    
    except Exception as e:
        logger.error(f"Error fetching training data: {e}")
        return pd.DataFrame()

def preprocess_data(df):
    """Prepare data for model training"""
    if df.empty:
        return None, None
    
    try:
        # Feature engineering - adapt to your specific model needs
        features = pd.DataFrame({
            'amount': df['amount'],
            'fraud_probability': df['fraud_probability'],
            # Add other features as needed based on your model
        })
        
        # Target variable
        target = df['actual_is_fraud']
        
        logger.info(f"Preprocessed {len(features)} samples for training")
        return features, target
    
    except Exception as e:
        logger.error(f"Error preprocessing data: {e}")
        return None, None

def retrain_model():
    """Retrain the model with new feedback data"""
    # Backup existing model
    backup_current_model()
    
    # Get training data
    training_data = get_training_data()
    
    if training_data.empty:
        logger.info("No new training data available, skipping retraining")
        return False
    
    # Preprocess data
    X, y = preprocess_data(training_data)
    if X is None or y is None:
        logger.error("Failed to preprocess data, skipping retraining")
        return False
    
    try:
        # Load existing model
        with open(MODEL_PATH, 'rb') as file:
            model = pickle.load(file)
        
        # Update model with new data
        # This depends on your specific RL algorithm
        # For a scikit-learn model, you might do:
        # model.fit(X, y)
        
        # For a custom RL model, you might have a specific update method:
        model.update(X, y)  # Adjust according to your model's API
        
        # Save updated model
        with open(MODEL_PATH, 'wb') as file:
            pickle.dump(model, file)
        
        logger.info(f"Model successfully retrained and saved to {MODEL_PATH}")
        return True
    
    except Exception as e:
        logger.error(f"Error retraining model: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting model retraining process")
    success = retrain_model()
    if success:
        logger.info("Model retraining completed successfully")
    else:
        logger.warning("Model retraining process completed with warnings or errors")