"use client"

import { useState } from "react"
import type { CarInput } from "@/lib/types"
import { CarSearchForm } from "@/components/car-search-form"
import CircularDemandMeter from "@/components/circular-demand-meter"

type Step = "intro" | "form" | "result"

// Add interfaces for the advanced API response
interface DemandBreakdown {
  [key: string]: number
}

interface DemandAnalysis {
  [key: string]: any
}

interface AdvancedDemandResponse {
  demandIndex: number
  breakdown: DemandBreakdown
  analysis: DemandAnalysis
  message: string
}

export default function Demand() {
  const [step, setStep] = useState<Step>("intro")
  const [input, setInput] = useState<CarInput | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [score, setScore] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  
  // Add new state for advanced data
  const [demandBreakdown, setDemandBreakdown] = useState<DemandBreakdown | null>(null)
  const [demandAnalysis, setDemandAnalysis] = useState<DemandAnalysis | null>(null)
  const [demandMessage, setDemandMessage] = useState<string | null>(null)

  // Map ownership values to match backend expectations
  const mapOwnership = (ownership: string): string => {
    const ownershipMap: Record<string, string> = {
      "First": "1",
      "Second": "2", 
      "Third+": "3",
      "fourth+": "4"
    }
    return ownershipMap[ownership] || ownership
  }

  // Map transmission values to match backend expectations
  const mapTransmission = (transmission: string): string => {
    return transmission.toLowerCase()
  }

  // Updated function to call the advanced demand index API
  const fetchAdvancedDemandIndex = async (carData: CarInput): Promise<AdvancedDemandResponse> => {
    // Multiple backend URLs to try
    const baseUrls = [
        'https://carvalue.onrender.com'
    ]

    let lastError = null

    for (const baseUrl of baseUrls) {
      try {
        console.log(`Trying backend URL: ${baseUrl}`)
        
        // First check if backend is running
        const healthUrl = `${baseUrl}/health`
        console.log("Checking backend health...")
        
        const healthRes = await fetch(healthUrl, {
          method: 'GET',
          mode: 'cors',
          headers: {
            'Accept': 'application/json',
          },
          signal: AbortSignal.timeout(5000) // 5 second timeout
        })
        
        if (!healthRes.ok) {
          throw new Error(`Backend health check failed with status ${healthRes.status}`)
        }
        
        const healthData = await healthRes.json()
        console.log("Backend health:", healthData)
        
        if (!healthData.dataset_loaded) {
          throw new Error("Backend dataset not loaded. Check if cars24.csv exists.")
        }

        // Prepare parameters for advanced API
        const params = new URLSearchParams({
          year: carData.year.toString(),
          fuel_type: carData.fuel.toLowerCase(),
          transmission: mapTransmission(carData.transmission),
          owners: mapOwnership(carData.ownership),
          kms_driven: carData.kmDriven.toString()
        })

        // Construct the advanced demand index URL
        const url = `${baseUrl}/demand-index/${encodeURIComponent(carData.company.toLowerCase())}/${encodeURIComponent(carData.model.toLowerCase())}?${params}`
        
        console.log("Fetching advanced demand URL:", url)
        console.log("Car input:", carData)

        const response = await fetch(url, {
          method: 'GET',
          mode: 'cors',
          headers: {
            'Accept': 'application/json',
          },
          signal: AbortSignal.timeout(10000) // 10 second timeout
        })
        
        console.log("Response status:", response.status)
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }

        const data = await response.json()
        console.log("Advanced demand data:", data)
        
        return {
          demandIndex: data.demand_index || 0,
          breakdown: data.breakdown || {},
          analysis: data.analysis || {},
          message: data.message || 'Demand index calculated successfully'
        }
        
      } catch (e: any) {
        console.error(`Failed with ${baseUrl}:`, e)
        lastError = e
        
        // If this is a timeout or network error, try the next URL
        if (e.name === 'TypeError' || e.name === 'AbortError' || e.message.includes('fetch')) {
          continue
        } else {
          // If it's a different error (like 404, 500), don't try other URLs
          break
        }
      }
    }

    // If we get here, all URLs failed
    console.error("All backend URLs failed. Last error:", lastError)
    
    let errorMessage = "Unable to calculate demand index. Please try again later."
    
    if (lastError) {
      if (lastError.name === 'TypeError' || lastError.name === 'AbortError') {
        errorMessage += " Please ensure FastAPI server is running with: python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
      } else {
        errorMessage += ` ${lastError.message}`
      }
    }
    
    return {
      demandIndex: 0,
      breakdown: {},
      analysis: {},
      message: errorMessage
    }
  }

  async function handleFormSubmit(ci: CarInput) {
    setError(null)
    setInput(ci)
    setScore(null)
    setDemandBreakdown(null)
    setDemandAnalysis(null)
    setDemandMessage(null)
    setLoading(true)
    setStep("result") // Move to result step immediately to show loading

    try {
      // Get advanced demand index
      const demandData = await fetchAdvancedDemandIndex(ci)
      
      if (demandData.demandIndex > 0) {
        // Normalize the score to 0-100 range
        const normalized = Math.max(0, Math.min(100, Math.round(demandData.demandIndex)))
        
        setScore(normalized)
        setDemandBreakdown(demandData.breakdown)
        setDemandAnalysis(demandData.analysis)
        setDemandMessage(demandData.message)
        setError(null)
      } else {
        setError(demandData.message)
        setScore(null)
      }
      
    } catch (e: any) {
      console.error("Error in handleFormSubmit:", e)
      setError("Failed to calculate demand index. Please try again.")
      setScore(null)
    } finally {
      setLoading(false)
    }
  }

  function startOver() {
    setStep("intro")
    setInput(null)
    setScore(null)
    setDemandBreakdown(null)
    setDemandAnalysis(null)
    setDemandMessage(null)
    setLoading(false)
    setError(null)
  }

  return (
    <main className="min-h-[70vh] bg-white">
      {step === "intro" && (
        <section className="mx-auto flex min-h-[70vh] max-w-3xl flex-col items-center justify-center px-4 text-center">
          <h1 className="text-balance text-3xl font-semibold text-slate-900 md:text-4xl">Demand Index</h1>
          <p className="mt-2 max-w-prose text-pretty text-slate-600">
            Estimate market demand for your car configuration in seconds.
          </p>
          <button
            onClick={() => setStep("form")}
            className="mt-6 inline-flex items-center justify-center rounded-md bg-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
          >
            Get started with Demand Index
          </button>
        </section>
      )}

      {step === "form" && (
        <section className="mx-auto max-w-5xl px-4 py-10">
          <div className="mx-auto max-w-3xl rounded-md border bg-white p-5">
            <h2 className="mb-4 text-lg font-semibold text-slate-900">Car Details</h2>
            <p className="mb-4 text-sm text-slate-600">
              Fill in the details below. Then we&apos;ll show your Demand Index.
            </p>
            <CarSearchForm onSubmit={handleFormSubmit} />
            
            {error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}
            
            <div className="mt-6 flex items-center gap-3">
              <button
                onClick={() => setStep("intro")}
                className="inline-flex items-center justify-center rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
                type="button"
              >
                Back
              </button>
            </div>
          </div>
        </section>
      )}

      {step === "result" && (
        <section className="mx-auto max-w-4xl px-4 py-10">
          <div className="rounded-md border bg-white p-5">
            <h2 className="mb-1 text-lg font-semibold text-slate-900">Demand Index</h2>
            <p className="mb-6 text-sm text-slate-600">Based on your car details, transmission, and ownership.</p>
            
            {/* Show input details */}
            {input && (
              <div className="mb-6 p-4 bg-gray-50 rounded-md">
                <h3 className="text-sm font-medium text-gray-900 mb-2">Car Details:</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm text-gray-600">
                  <div><strong>Company:</strong> {input.company}</div>
                  <div><strong>Model:</strong> {input.model}</div>
                  <div><strong>Year:</strong> {input.year}</div>
                  <div><strong>Fuel:</strong> {input.fuel}</div>
                  <div><strong>KMs:</strong> {input.kmDriven.toLocaleString()}</div>
                  <div><strong>Transmission:</strong> {input.transmission}</div>
                  <div><strong>Ownership:</strong> {input.ownership}</div>
                </div>
              </div>
            )}
            
            <div className="flex flex-col items-center">
              {loading ? (
                <div className="flex flex-col items-center space-y-2">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <div className="text-sm text-slate-600">Calculating demand…</div>
                </div>
              ) : error ? (
                <div className="text-center">
                  <div className="text-sm text-red-600 mb-4">{error}</div>
                  <button
                    onClick={() => input && handleFormSubmit(input)}
                    className="inline-flex items-center justify-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
                  >
                    Retry
                  </button>
                </div>
              ) : score == null ? (
                <div className="text-sm text-slate-600">No score available.</div>
              ) : (
                <>
                  <CircularDemandMeter value={score} />
                  
                  {/* Show demand message */}
                  {demandMessage && (
                    <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
                      <p className="text-sm text-blue-800">{demandMessage}</p>
                    </div>
                  )}
                  
                  {/* Show breakdown if available */}
                  {demandBreakdown && Object.keys(demandBreakdown).length > 0 && (
                    <div className="mt-6 w-full max-w-md">
                      <h3 className="text-sm font-medium text-gray-900 mb-3">Demand Breakdown:</h3>
                      <div className="space-y-2">
                        {Object.entries(demandBreakdown).map(([key, value]) => (
                          <div key={key} className="flex justify-between text-sm">
                            <span className="text-gray-600 capitalize">{key.replace(/_/g, ' ')}:</span>
                            <span className="font-medium">{typeof value === 'number' ? value.toFixed(1) : value}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}

              <div className="mt-6 flex items-center gap-3">
                <button
                  onClick={() => setStep("form")}
                  className="inline-flex items-center justify-center rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
                  type="button"
                >
                  Edit Details
                </button>
                <button
                  onClick={startOver}
                  className="inline-flex items-center justify-center rounded-md bg-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2"
                  type="button"
                >
                  Start over
                </button>
              </div>
            </div>
          </div>
        </section>
      )}
    </main>
  )
}