import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Shield, ArrowLeft, Upload } from "lucide-react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"

export default function BatchUpload() {
  return (
    <div className="flex flex-col min-h-screen bg-black text-white">

      {/* Main Content */}
      <main className="flex-1 py-12 text-white">
        <div className="container px-4 md:px-6 max-w-2xl mx-auto">
          <div className="mb-8">
            <Link href="/" className="inline-flex items-center text-sm font-medium text-primary hover:underline">
              <ArrowLeft className="mr-1 h-4 w-4" />
              Back to Home
            </Link>
          </div>

          <Card className="bg-black text-white">
            <CardHeader>
              <CardTitle className="text-2xl">Batch Upload</CardTitle>
              <CardDescription>
                Upload a CSV file with multiple transactions to check for potential fraud
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center justify-center border-2 border-dashed rounded-lg p-12 text-center">
                <Upload className="h-10 w-10 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">Upload your CSV file</h3>
                <p className="text-sm text-muted-foreground mb-4">Drag and drop your file here, or click to browse</p>
                <Button>Select File</Button>
                <p className="text-xs text-muted-foreground mt-4">
                  Supported format: CSV with columns for Transaction ID, UPI IDs, Amount, Time, and Account Number
                </p>
              </div>
            </CardContent>
            <CardFooter>
              <Button className="w-full" disabled>
                Process Batch
              </Button>
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

