-- init.sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    is_fraud BOOLEAN NOT NULL,
    feedback BOOLEAN NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transaction_id ON transactions(transaction_id);
CREATE INDEX idx_user_id ON transactions(user_id);
CREATE INDEX idx_created_at ON transactions(created_at);

-- Table for storing feedback for retraining
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(255) NOT NULL,
    actual_is_fraud BOOLEAN NOT NULL,
    feedback_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_for_training BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_feedback_transaction_id ON feedback(transaction_id);
CREATE INDEX idx_feedback_time ON feedback(feedback_time);
CREATE INDEX idx_used_for_training ON feedback(used_for_training);