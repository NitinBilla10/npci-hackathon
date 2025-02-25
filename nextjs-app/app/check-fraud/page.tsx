'use client'

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ArrowLeft } from "lucide-react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

interface FormData {
  User: string;
  Card: string;
  Year: string;
  Month: string;
  Day: string;
  Time: string;
  Amount: string;
  Use_Chip: string;
  Merchant_Name: string;
  Merchant_City: string;
  Merchant_State: string;
  Zip: string;
  MCC: string;
}

export default function CheckFraud() {
  const [formData, setFormData] = useState<FormData>({
    User: "",
    Card: "",
    Year: new Date().getFullYear().toString(),
    Month: (new Date().getMonth() + 1).toString(),
    Day: new Date().getDate().toString(),
    Time: `${new Date().getHours()}:${String(new Date().getMinutes()).padStart(2, '0')}`,
    Amount: "",
    Use_Chip: "Chip Transaction",
    Merchant_Name: "",
    Merchant_City: "",
    Merchant_State: "",
    Zip: "",
    MCC: "",
  });
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const formatAmount = (value: string) => {
    // Ensure the amount has a dollar sign
    if (!value.startsWith('$') && value.trim() !== '') {
      return `$${value}`;
    }
    return value;
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setError(null);
    
    // Format amount to ensure it has $ sign
    const processedFormData = {
      ...formData,
      Amount: formatAmount(formData.Amount)
    };
    
    try {
      const response = await fetch("http://64.227.156.131:8000/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(processedFormData),
      });
      
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Something went wrong");
      }
      
      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-black">
      <main className="bg-black">
        <div className="bg-black">
          <div>
            <Link href="/">
              <ArrowLeft /> Back to Home
            </Link>
          </div>

          <Card className="max-w-[60%] mx-auto text-white bg-black">
            <CardHeader>
              <CardTitle>Check for Fraud</CardTitle>
              <CardDescription>
                Enter the transaction details below to verify if it's potentially fraudulent.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '16px' }}>
                  <div>
                    <Label htmlFor="User">User ID</Label>
                    <Input
                      id="User"
                      name="User"
                      value={formData.User}
                      onChange={handleChange}
                      placeholder="Enter User ID"
                      required
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="Card">Card Number</Label>
                    <Input
                      id="Card"
                      name="Card"
                      value={formData.Card}
                      onChange={handleChange}
                      placeholder="Enter Card Number"
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="Year">Year</Label>
                    <Input
                      id="Year"
                      name="Year"
                      type="number"
                      value={formData.Year}
                      onChange={handleChange}
                      placeholder="YYYY"
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="Month">Month</Label>
                    <Input
                      id="Month"
                      name="Month"
                      type="number"
                      min="1"
                      max="12"
                      value={formData.Month}
                      onChange={handleChange}
                      placeholder="MM"
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="Day">Day</Label>
                    <Input
                      id="Day"
                      name="Day"
                      type="number"
                      min="1"
                      max="31"
                      value={formData.Day}
                      onChange={handleChange}
                      placeholder="DD"
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="Time">Time (HH:MM)</Label>
                    <Input
                      id="Time"
                      name="Time"
                      value={formData.Time}
                      onChange={handleChange}
                      placeholder="HH:MM"
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="Amount">Amount</Label>
                    <Input
                      id="Amount"
                      name="Amount"
                      value={formData.Amount}
                      onChange={handleChange}
                      placeholder="Enter amount (e.g., 147.83)"
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="Use_Chip" className="bg-black">Payment Method</Label>
                    <select
                      id="Use_Chip"
                      name="Use_Chip"
                      className="bg-black"
                      value={formData.Use_Chip}
                      onChange={handleChange}
                      style={{ width: '100%', padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
                      required
                    >
                      <option value="Chip Transaction">Chip Transaction</option>
                      <option value="Swipe Transaction">Swipe Transaction</option>
                      <option value="Online Transaction">Online Transaction</option>
                    </select>
                  </div>

                  <div>
                    <Label htmlFor="Merchant_Name">Merchant Name</Label>
                    <Input
                      id="Merchant_Name"
                      name="Merchant_Name"
                      value={formData.Merchant_Name}
                      onChange={handleChange}
                      placeholder="Enter Merchant Name"
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="Merchant_City">Merchant City</Label>
                    <Input
                      id="Merchant_City"
                      name="Merchant_City"
                      value={formData.Merchant_City}
                      onChange={handleChange}
                      placeholder="Enter Merchant City"
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="Merchant_State">Merchant State</Label>
                    <Input
                      id="Merchant_State"
                      name="Merchant_State"
                      value={formData.Merchant_State}
                      onChange={handleChange}
                      placeholder="Enter State (e.g., CA)"
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="Zip">ZIP Code</Label>
                    <Input
                      id="Zip"
                      name="Zip"
                      value={formData.Zip}
                      onChange={handleChange}
                      placeholder="Enter ZIP Code"
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="MCC">Merchant Category Code</Label>
                    <Input
                      id="MCC"
                      name="MCC"
                      value={formData.MCC}
                      onChange={handleChange}
                      placeholder="Enter MCC"
                      required
                    />
                  </div>
                </div>
                <CardFooter style={{ marginTop: '20px', padding: '0' }}>
                  <Button type="submit" disabled={loading} style={{ width: '100%' }}>
                    {loading ? "Verifying..." : "Verify Transaction"}
                  </Button>
                </CardFooter>
              </form>
            </CardContent>
          </Card>

          {result && (
            <Card style={{ marginTop: '20px', borderLeft: result.is_fraud ? '4px solid #ef4444' : '4px solid #22c55e' }}>
              <CardHeader>
                <CardTitle>
                  {result.is_fraud ? "Fraud Detected" : "Transaction Safe"}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '16px' }}>
                  <div>
                    <p style={{ fontSize: '14px', fontWeight: 500, color: '#6b7280' }}>Transaction ID</p>
                    <p>{result.transaction_id}</p>
                  </div>
                  <div>
                  </div>
                  <div>
                    <p style={{ fontSize: '14px', fontWeight: 500, color: '#6b7280' }}>Status</p>
                    <p style={{ color: result.is_fraud ? '#dc2626' : '#16a34a', fontWeight: 'bold' }}>
                      {result.is_fraud ? "Fraudulent" : "Legitimate"}
                    </p>
                  </div>
                  <div>
                    <p style={{ fontSize: '14px', fontWeight: 500, color: '#6b7280' }}>Timestamp</p>
                    <p>{new Date(result.timestamp).toLocaleString()}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
          
          {error && (
            <div style={{ marginTop: '20px', padding: '16px', backgroundColor: '#fee2e2', border: '1px solid #fecaca', borderRadius: '4px' }}>
              <p style={{ fontWeight: 'bold', color: '#dc2626' }}>Error</p>
              <p>{error}</p>
            </div>
          )}
        </div>
      </main>
      <footer style={{ marginTop: '40px', padding: '20px 0', backgroundColor: '#1f2937', color: 'white', textAlign: 'center' }}>
        <div>
          &copy; {new Date().getFullYear()} UPIShield. All rights reserved.
        </div>
      </footer>
    </div>
  );
}