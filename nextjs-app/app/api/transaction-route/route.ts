// app/api/transaction-status/route.js
import { NextResponse } from 'next/server';
import axios from 'axios';

export async function POST(request: { json: () => any; }) {
  try {
    // Get transaction data from request body
    const transactionData = await request.json();
    
    // Send to your fraud detection service
    const response = await axios.post(
      process.env.FRAUD_SERVICE_URL || 'http://localhost:8000/predict', 
      transactionData
    );
    
    // Return the prediction to the client
    return NextResponse.json({
      transactionId: transactionData.id,
      isFraud: response.data.fraud_prediction,
      timestamp: new Date().toISOString()
    }, { status: 200 });
    
  } catch (error) {
    console.error('Error processing transaction:', error);
    return NextResponse.json(
      { error: 'Failed to process transaction' }, 
      { status: 500 }
    );
  }
}