import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Shield, Upload, CheckCircle, AlertTriangle, BarChart3, Clock } from "lucide-react"
import ColourfulText from "@/components/ui/colourful-text"
import Aurora from "@/components/ui/Aurora/Aurora"

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-black text-white">
      {/* Hero Section */}
      <Aurora
        colorStops={["#E0F7FA", "#B3E5FC", "#81D4FA"]}
        blend={0.8}
        amplitude={1.2}
        speed={0.5}
      />
      <section className="flex-1 flex items-center justify-center py-12 md:py-24 lg:py-32 bg-gradient-to-b from-black via-black/90 to-black/80">
        <div className="container px-4 md:px-6">
          <div className="flex flex-col items-center text-center space-y-4 mb-12">
            <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl text-white">
              Secure Your <ColourfulText text="UPI" /> Transactions
            </h1>
            <p className="mx-auto max-w-[700px] text-gray-300 md:text-xl">
              Advanced fraud detection to protect your digital payments
            </p>
          </div>

          <div className="mx-auto max-w-md p-6 border border-gray-800 rounded-lg shadow-lg bg-black/80">
            <div className="grid gap-4">
              <Link href="/check-fraud" className="group">
                <div className="flex items-center p-4 border border-gray-800 rounded-md hover:bg-gray-900 transition-colors">
                  <div className="mr-4 p-2 rounded-full bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                    <CheckCircle className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-medium text-white">Check for Fraud</h3>
                    <p className="text-sm text-gray-400">Verify a single UPI transaction</p>
                  </div>
                </div>
              </Link>
              <Link href="/batch-upload" className="group">
                <div className="flex items-center p-4 border border-gray-800 rounded-md hover:bg-gray-900 transition-colors">
                  <div className="mr-4 p-2 rounded-full bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                    <Upload className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-medium text-white">Batch Upload</h3>
                    <p className="text-sm text-gray-400">Check multiple transactions at once</p>
                  </div>
                </div>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-12 md:py-24 bg-black">
        <div className="container px-4 md:px-6">
          <div className="flex flex-col items-center text-center space-y-4 mb-12">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl text-white">Key Features</h2>
            <p className="mx-auto max-w-[700px] text-gray-300">
              Our advanced technology helps you stay protected from UPI fraud
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="flex flex-col items-center p-6 bg-gray-900 rounded-lg shadow-sm border border-gray-800">
              <div className="p-3 rounded-full bg-primary/10 text-primary mb-4">
                <AlertTriangle className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-medium mb-2 text-white">Real-time Detection</h3>
              <p className="text-center text-gray-400">Instant verification of suspicious transactions</p>
            </div>
            <div className="flex flex-col items-center p-6 bg-gray-900 rounded-lg shadow-sm border border-gray-800">
              <div className="p-3 rounded-full bg-primary/10 text-primary mb-4">
                <BarChart3 className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-medium mb-2 text-white">Advanced Analytics</h3>
              <p className="text-center text-gray-400">Pattern recognition to identify potential fraud</p>
            </div>
            <div className="flex flex-col items-center p-6 bg-gray-900 rounded-lg shadow-sm border border-gray-800">
              <div className="p-3 rounded-full bg-primary/10 text-primary mb-4">
                <Clock className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-medium mb-2 text-white">24/7 Monitoring</h3>
              <p className="text-center text-gray-400">Continuous protection for all your transactions</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-8 bg-black">
        <div className="container px-4 md:px-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Shield className="h-5 w-5 text-primary" />
                <span className="text-lg font-bold text-white">UPIShield</span>
              </div>
              <p className="text-sm text-gray-400">
                Protecting your digital payments with advanced fraud detection technology.
              </p>
            </div>
            <div>
              <h3 className="font-medium mb-4 text-white">Quick Links</h3>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link href="/about" className="text-gray-400 hover:text-white">
                    About Us
                  </Link>
                </li>
                <li>
                  <Link href="/contact" className="text-gray-400 hover:text-white">
                    Contact
                  </Link>
                </li>
                <li>
                  <Link href="/faq" className="text-gray-400 hover:text-white">
                    FAQ
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-medium mb-4 text-white">Legal</h3>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link href="/privacy" className="text-gray-400 hover:text-white">
                    Privacy Policy
                  </Link>
                </li>
                <li>
                  <Link href="/terms" className="text-gray-400 hover:text-white">
                    Terms of Service
                  </Link>
                </li>
              </ul>
            </div>
          </div>
          <div className="mt-8 pt-6 border-t border-gray-800 text-center text-sm text-gray-400">
            &copy; {new Date().getFullYear()} UPIShield. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  )
}