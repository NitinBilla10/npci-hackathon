import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Shield, ArrowLeft } from "lucide-react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"

export default function CheckFraud() {
  return (
    <div className="flex flex-col bg-black min-h-screen text-white">

      {/* Main Content */}
      <main className="flex-1 py-12">
        <div className="container px-4 md:px-6 max-w-2xl mx-auto">
          <div className="mb-8">
            <Link href="/" className="inline-flex items-center text-sm font-medium text-primary hover:underline">
              <ArrowLeft className="mr-1 h-4 w-4" />
              Back to Home
            </Link>
          </div>

          <Card className="bg-black text-white">
            <CardHeader>
              <CardTitle className="text-2xl">Check for UPI Fraud</CardTitle>
              <CardDescription>
                Enter the transaction details below to verify if it's potentially fraudulent
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="transactionId">Transaction ID</Label>
                    <Input id="transactionId" placeholder="Enter transaction ID" required />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="receiverUpi">Receiver UPI ID</Label>
                    <Input id="receiverUpi" placeholder="example@upi" required />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="amount">Amount (₹)</Label>
                    <Input id="amount" type="number" placeholder="0.00" required />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="transactionTime">Time of Transaction</Label>
                    <Input id="transactionTime" type="datetime-local" required />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="accountNo">Account Number</Label>
                    <Input id="accountNo" placeholder="Enter account number" required />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="senderUpi">Sender UPI ID</Label>
                    <Input id="senderUpi" placeholder="example@upi" required />
                  </div>
                </div>
              </form>
            </CardContent>
            <CardFooter>
              <Button className="w-full">Verify Transaction</Button>
            </CardFooter>
          </Card>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t py-6 bg-black">
        <div className="container px-4 md:px-6 text-center text-sm text-muted-foreground">
          &copy; {new Date().getFullYear()} UPIShield. All rights reserved.
        </div>
      </footer>
    </div>
  )
}

