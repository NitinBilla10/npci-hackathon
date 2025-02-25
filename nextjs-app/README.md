# UPI Fraud Detection System

This project deploys a reinforcement learning-based fraud detection system for UPI transactions, with a Next.js 15 frontend.

## System Architecture

![System Architecture](./architecture-diagram.png)

The system consists of the following components:

1. **Kafka** - Message broker for transaction streaming
2. **PostgreSQL** - Database for storing transactions and model predictions
3. **Fraud Detection Service** - FastAPI service for fraud predictions
4. **Kafka Consumer** - Service that reads transactions from Kafka and sends to the prediction service
5. **Model Retraining Service** - Weekly scheduled service to retrain the model with user feedback
6. **Next.js 15 Frontend** - User interface for transaction status and feedback

## Prerequisites

- Docker and Docker Compose
- Your trained model in pickle (.pkl) format

## Directory Structure

```
├── docker-compose.yml
├── init.sql
├── model/
│   └── fraud_detection_model.pkl  # Place your .pkl file here
├── fraud_detection_service/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── kafka_consumer/
│   ├── Dockerfile
│   ├── kafka_consumer.py
│   └── requirements.txt
├── model_retraining/
│   ├── Dockerfile
│   ├── retrain_model.py
│   ├── crontab
│   └── requirements.txt
└── nextjs-app/
    ├── Dockerfile
    ├── package.json
    ├── app/
    │   ├── layout.js
    │   ├── globals.css
    │   ├── fraud-detection/
    │   │   └── page.js
    │   └── api/
    │       ├── transaction-status/
    │       │   └── route.js
    │       └── feedback/
    │           └── route.js
    └── components/
        └── TransactionStatus.jsx
```

## Deployment Steps

### 1. Prepare your model

Place your trained model pickle file in the `model/` directory with the name `fraud_detection_model.pkl`.

### 2. Set up environment

Create the necessary directories and files as per the structure above. Copy all the provided code files to their respective locations.

### 3. Build and start the containers

```bash
docker-compose build
docker-compose up -d
```

### 4. Check if all services are running

```bash
docker-compose ps
```

### 5. Test the system

The Next.js frontend will be available at http://localhost:3000.
The FastAPI service will be available at http://localhost:8000.

## Sending Transactions to Kafka

To send a new transaction to the system, publish a message to the `transactions` Kafka topic:

```bash
# Example using kafkacat
docker exec -it upi-fraud-detection-kafka kafkacat -b localhost:9092 -t transactions -P <<EOF
{
  "id": "txn123456",
  "user_id": "user789",
  "amount": 5000.0,
  "timestamp": "2023-10-25T10:15:30Z",
  "receiver_id": "merchant456"
}
EOF
```

## Monitoring

You can monitor the logs of each service using:

```bash
docker-compose logs -f fraud-detection-service
docker-compose logs -f kafka-consumer
docker-compose logs -f nextjs-app
```

## Scaling

For production use, consider:

1. Setting up proper Kafka partitioning
2. Adding more Kafka consumers
3. Deploying multiple instances of the fraud detection service behind a load balancer
4. Using Kubernetes for orchestration

## Troubleshooting

### Model doesn't load

- Check if the model file exists in the correct location
- Verify the model format is compatible with the code

### Kafka connection issues

- Ensure Zookeeper is running properly
- Check network connectivity between services

### Database connection errors

- Verify PostgreSQL is running
- Check credentials and connection strings

## Production Considerations

For production deployment:

1. Use environment variables for sensitive information
2. Set up proper authentication and authorization
3. Implement SSL/TLS for all communications
4. Configure proper backup strategies
5. Add monitoring and alerting
6. Consider using managed services (AWS, Azure, GCP) for Kafka and database