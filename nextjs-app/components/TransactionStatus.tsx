// components/TransactionStatus.jsx
'use client';

import { useState } from 'react';

export default function TransactionStatus() {
  const [transaction, setTransaction] = useState({
    id: '',
    amount: '',
    user_id: '',
    // Add other fields as needed
  });
  interface TransactionResult {
    transactionId: string;
    isFraud: boolean;
    timestamp: string;
  }

  const [result, setResult] = useState<TransactionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [feedback, setFeedback] = useState('');

  const handleSubmit = async (e: { preventDefault: () => void; }) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('/api/transaction-route', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(transaction),
      });
      
      if (!response.ok) {
        throw new Error('Failed to process transaction');
      }
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
      setError((error as any).message || 'An error occurred while processing the transaction');
    } finally {
      setLoading(false);
    }
  };

  const submitFeedback = async (isFraud: boolean) => {
    try {
      const response = await fetch('/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          transactionId: result?.transactionId,
          actualIsFraud: isFraud
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to submit feedback');
      }
      
      setFeedback('Thank you for your feedback!');
    } catch (error) {
      console.error('Error submitting feedback:', error);
      setFeedback('Failed to submit feedback. Please try again.');
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-black rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-6">Transaction Fraud Check</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Transaction ID</label>
          <input
            type="text"
            value={transaction.id}
            onChange={(e) => setTransaction({...transaction, id: e.target.value})}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700">Amount</label>
          <input
            type="number"
            value={transaction.amount}
            onChange={(e) => setTransaction({...transaction, amount: e.target.value})}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700">User ID</label>
          <input
            type="text"
            value={transaction.user_id}
            onChange={(e) => setTransaction({...transaction, user_id: e.target.value})}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
            required
          />
        </div>
        
        <button
          type="submit"
          className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          disabled={loading}
        >
          {loading ? 'Checking...' : 'Check Transaction'}
        </button>
      </form>
      
      {result && (
        <div className="mt-6 p-4 border rounded-md">
          <h3 className="font-semibold text-lg">Result:</h3>
          <p className="mt-2">
            Transaction ID: {result.transactionId}
          </p>
          <p className={`mt-1 font-bold ${result.isFraud ? 'text-red-600' : 'text-green-600'}`}>
            Status: {result.isFraud ? 'Potential Fraud Detected' : 'Transaction Appears Safe'}
          </p>
          <p className="mt-1 text-sm text-gray-500">
            Checked at: {new Date(result.timestamp).toLocaleString()}
          </p>
          
          <div className="mt-4">
            <p className="text-sm font-medium">Was this assessment correct?</p>
            <div className="mt-2 flex space-x-2">
              <button
                onClick={() => submitFeedback(true)}
                className="px-3 py-1 bg-red-100 text-red-800 rounded-md hover:bg-red-200"
              >
                This was fraud
              </button>
              <button
                onClick={() => submitFeedback(false)}
                className="px-3 py-1 bg-green-100 text-green-800 rounded-md hover:bg-green-200"
              >
                This was legitimate
              </button>
            </div>
            {feedback && <p className="mt-2 text-sm text-gray-600">{feedback}</p>}
          </div>
        </div>
      )}
    </div>
  );
}