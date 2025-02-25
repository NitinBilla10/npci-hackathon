// app/api/feedback/route.js
import { NextResponse } from 'next/server';
import axios from 'axios';

export async function POST(request: { json: () => any; }) {
  try {
    // Get feedback data from request body
    const feedbackData = await request.json();
    
    // Validate required fields
    if (!feedbackData.transactionId || feedbackData.actualIsFraud === undefined) {
      return NextResponse.json(
        { error: 'Missing required fields: transactionId and actualIsFraud' },
        { status: 400 }
      );
    }
    
    // Send feedback to your service
    await axios.post(
      `${process.env.FRAUD_SERVICE_URL || 'http://localhost:8000'}/feedback`,
      {
        transaction_id: feedbackData.transactionId,
        actual_is_fraud: feedbackData.actualIsFraud
      }
    );
    
    // Return success response
    return NextResponse.json(
      { message: 'Feedback received successfully' },
      { status: 200 }
    );
    
  } catch (error) {
    console.error('Error submitting feedback:', error);
    return NextResponse.json(
      { error: 'Failed to submit feedback' },
      { status: 500 }
    );
  }
}