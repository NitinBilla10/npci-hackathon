# kafka_consumer.py
import json
import os
import time
import logging
from kafka import KafkaConsumer
import requests
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'transactions')
FRAUD_SERVICE_URL = os.getenv('FRAUD_SERVICE_URL', 'http://fraud-detection-service:8000')
GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'fraud-detection-consumer')
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 5))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', 5))  # seconds

def create_consumer():
    """Create and return a Kafka consumer"""
    retry_count = 0
    while retry_count < MAX_RETRIES:
        try:
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                auto_offset_reset='earliest',
                enable_auto_commit=False,
                group_id=GROUP_ID,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                max_poll_interval_ms=300000,  # 5 minutes
                session_timeout_ms=30000,  # 30 seconds
                request_timeout_ms=45000,  # 45 seconds
            )
            logger.info(f"Successfully connected to Kafka topic {KAFKA_TOPIC}")
            return consumer
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            retry_count += 1
            if retry_count < MAX_RETRIES:
                logger.info(f"Retrying in {RETRY_DELAY} seconds... (Attempt {retry_count}/{MAX_RETRIES})")
                time.sleep(RETRY_DELAY)
            else:
                logger.error(f"Failed to connect to Kafka after {MAX_RETRIES} attempts")
                raise

def process_transaction(transaction):
    """Send transaction to fraud detection service for processing"""
    try:
        # Add timestamp if not present
        if 'timestamp' not in transaction:
            transaction['timestamp'] = datetime.now().isoformat()
            
        # Send to fraud detection service
        response = requests.post(
            f"{FRAUD_SERVICE_URL}/predict",
            json=transaction,
            timeout=10  # 10 second timeout
        )
        
        # Check if request was successful
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Transaction {transaction['id']} processed: {'FRAUD' if result['is_fraud'] else 'LEGITIMATE'}")
            return result
        else:
            logger.error(f"Error from fraud service: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending transaction to fraud service: {e}")
        return None

def main():
    """Main consumer loop"""
    try:
        consumer = create_consumer()
        
        logger.info("Starting to consume messages...")
        for message in consumer:
            transaction = message.value
            logger.info(f"Received transaction: {transaction['id']}")
            
            result = process_transaction(transaction)
            
            if result:
                # Commit offset only if processing was successful
                consumer.commit()
                logger.info(f"Committed offset for transaction {transaction['id']}")
            else:
                logger.warning(f"Skipping offset commit due to processing failure for transaction {transaction['id']}")
                # You might implement retry logic here
                
    except KeyboardInterrupt:
        logger.info("Consumer stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        # Close consumer if it was created
        if 'consumer' in locals() and consumer:
            consumer.close()
            logger.info("Consumer closed")

if __name__ == "__main__":
    # Add a startup delay to ensure Kafka is ready
    startup_delay = int(os.getenv('STARTUP_DELAY', 10))
    logger.info(f"Waiting {startup_delay} seconds for Kafka to be ready...")
    time.sleep(startup_delay)
    
    main()