# UPI Fraud Detection System Setup

This guide will help you set up and run the UPI Fraud Detection system using Docker Compose and Jupyter notebooks.

## Prerequisites

- Docker and Docker Compose installed
- Your pre-trained reinforcement learning model (.pkl file)
- Git (optional)

## Directory Structure

Create the following directory structure:

```
upi-fraud-detection/
├── data/                  # Directory for data files
├── model/                 # Directory for ML models
│   └── backups/           # Directory for model backups
├── notebooks/             # Directory for Jupyter notebooks
├── nextjs-app/            # Next.js 15 application
├── docker-compose.yml     # Docker Compose configuration
├── init.sql               # Database initialization
└── requirements.txt       # Python dependencies
```

## Setup Instructions

1. **Create the directory structure**:
   ```bash
   mkdir -p upi-fraud-detection/{data,model/backups,notebooks,nextjs-app}
   cd upi-fraud-detection
   ```

2. **Save the provided Docker Compose file**:
   - Save the `docker-compose.yml` file to the root directory

3. **Save the initialization SQL file**:
   - Save the `init.sql` file to the root directory

4. **Save the requirements file**:
   - Save the `requirements.txt` file to the root directory

5. **Copy your model file**:
   - Copy your `.pkl` model file to the `model/` directory
   - Rename it to `fraud_detection_model.pkl`

6. **Copy Jupyter notebooks**:
   - Save the provided Jupyter notebooks to the `notebooks/` directory

7. **Start the Docker Compose environment**:
   ```bash
   docker-compose up -d
   ```

8. **Access Jupyter Notebooks**:
   - Open your browser and go to: http://localhost:8888
   - You should see the Jupyter Lab interface with access to your notebooks

9. **Access FastAPI Documentation**:
   - Once running, you can access the API docs at: http://localhost:8000/docs

10. **Access Next.js Frontend**:
    - The web interface will be available at: http://localhost:3000

## Using the System

### 1. Running the Notebooks

Open and run the following notebooks in order:

1. `fraud-detection-notebook.ipynb` - Load and serve your model
2. `kafka-consumer-notebook.ipynb` - Process transactions from Kafka
3. `model-retraining-notebook.ipynb` - Retrain your model with feedback

### 2. Testing the API

You can test the API using cURL or Postman:

```bash
# Example: Check a transaction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-txn-001",
    "user_id": "user-test",
    "amount": 5000.0,
    "receiver_id": "merchant-test"
  }'
```

### 3. Using the Web Interface

Navigate to http://localhost:3000 to use the web interface for:
- Submitting transactions for fraud detection
- Viewing fraud detection results
- Providing feedback on predictions

## Shutting Down

To stop all services:

```bash
docker-compose down
```

To stop all services and remove volumes (deletes database data):

```bash
docker-compose down -v
```

## Troubleshooting

- **Jupyter not accessible**: 
  - Check logs: `docker-compose logs jupyter-fraud-detection`
  - Ensure port 8888 is not in use by another application

- **Kafka connection issues**:
  - Check logs: `docker-compose logs kafka`
  - Verify topic creation: `docker-compose logs kafka-setup`

- **Database connection issues**:
  - Check logs: `docker-compose logs postgres`
  - Verify database initialization: `docker-compose exec postgres psql -U jupyteruser -d fraud_detection -c "SELECT count(*) FROM transactions;"`

- **FastAPI service not responding**:
  - Check logs: `docker-compose logs fastapi-service`
  - Restart the service: `docker-compose restart fastapi-service`