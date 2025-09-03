"use client"


import { useState } from "react"
import type { CarInput } from "@/lib/types"
import { CarSearchForm } from "@/components/car-search-form"
import CircularDemandMeter from "@/components/circular-demand-meter"

type Step = "intro" | "form" | "result"

export default function Demand()   {
  const [step, setStep] = useState<Step>("intro")
  const [input, setInput] = useState<CarInput | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [score, setScore] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleFormSubmit(ci: CarInput) {
    setError(null);
    setInput(ci);
    setScore(null);
    setLoading(true);

    // Multiple backend URLs to try
    const baseUrls = [
      'http://localhost:8000',
      'http://127.0.0.1:8000',
      'http://0.0.0.0:8000'
    ];

    let lastError = null;

    for (const baseUrl of baseUrls) {
      try {
        console.log(`Trying backend URL: ${baseUrl}`);
        
        // First check if backend is running
        const healthUrl = `${baseUrl}/health`;
        console.log("Checking backend health...");
        
        const healthRes = await fetch(healthUrl, {
          method: 'GET',
          mode: 'cors',
          headers: {
            'Accept': 'application/json',
          },
          signal: AbortSignal.timeout(5000) // 5 second timeout
        });
        
        if (!healthRes.ok) {
          throw new Error(`Backend health check failed with status ${healthRes.status}`);
        }
        
        const healthData = await healthRes.json();
        console.log("Backend health:", healthData);
        
        if (!healthData.dataset_loaded) {
          throw new Error("Backend dataset not loaded. Check if cars24.csv exists.");
        }

        // Construct the demand index URL
        const url = `${baseUrl}/demand-index/${encodeURIComponent(ci.company.toLowerCase())}/${encodeURIComponent(ci.model.toLowerCase())}`;
        
        console.log("Fetching URL:", url);
        console.log("Car input:", ci);

        const res = await fetch(url, {
          method: 'GET',
          mode: 'cors',
          headers: {
            'Accept': 'application/json',
          },
          signal: AbortSignal.timeout(10000) // 10 second timeout
        });
        
        console.log("Response status:", res.status);
        console.log("Response headers:", Object.fromEntries(res.headers));

        const text = await res.text();
        console.log("Response text:", text);

        if (!res.ok) {
          let errorMessage = `Backend returned status ${res.status}`;
          
          try {
            const errorData = JSON.parse(text);
            if (errorData.detail) {
              errorMessage += `: ${errorData.detail}`;
            }
          } catch (e) {
            errorMessage += `: ${text}`;
          }
          
          throw new Error(errorMessage);
        }

        let data;
        try {
          data = JSON.parse(text);
        } catch (e) {
          throw new Error(`Invalid JSON response: ${text}`);
        }

        console.log("Parsed data:", data);

        // Use the backend's demand_index key
        const raw = typeof data.demand_index === "number" ? data.demand_index : null;
        const normalized = raw !== null ? Math.max(0, Math.min(100, Math.round(raw))) : null;

        console.log("Raw demand index:", raw);
        console.log("Normalized score:", normalized);

        if (normalized === null) {
          setError("Invalid response from server: missing or invalid demand_index");
          setScore(null);
        } else {
          setScore(normalized);
          setStep("result");
        }
        
        // If we get here, the request was successful, so break out of the loop
        setLoading(false); // Ensure loading is cleared
        return;
        
      } catch (e: any) {
        console.error(`Failed with ${baseUrl}:`, e);
        lastError = e;
        
        // If this is a timeout or network error, try the next URL
        if (e.name === 'TypeError' || e.name === 'AbortError' || e.message.includes('fetch')) {
          continue;
        } else {
          // If it's a different error (like 404, 500), don't try other URLs
          break;
        }
      }
    }

    // If we get here, all URLs failed
    console.error("All backend URLs failed. Last error:", lastError);
    
    let errorMessage = "Failed to connect to backend server.";
    
    if (lastError) {
      if (lastError.name === 'TypeError' || lastError.name === 'AbortError') {
        errorMessage += " Please ensure FastAPI server is running with: python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000";
      } else {
        errorMessage += ` ${lastError.message}`;
      }
    }
    
    setError(errorMessage);
    setScore(null);
    setLoading(false);
  }

  function startOver() {
    setStep("intro")
    setInput(null)
    setScore(null)
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
            {/* <div className="mt-6 grid gap-4 sm:grid-cols-2">
              <div className="flex flex-col">
                <label htmlFor="transmission" className="mb-1 text-sm font-medium text-slate-900">
                  Transmission
                </label>
                <select
                  id="transmission"
                  value={transmission}
                  onChange={(e) => setTransmission(e.target.value)}
                  className="rounded-md border px-3 py-2 text-sm text-slate-900"
                >
                  <option value="">Select transmission</option>
                  <option value="Manual">Manual</option>
                  <option value="Automatic">Automatic</option>
                  <option value="AMT">AMT</option>
                  <option value="CVT">CVT</option>
                  <option value="DCT">DCT</option>
                </select>
              </div>
              <div className="flex flex-col">
                <label htmlFor="ownership" className="mb-1 text-sm font-medium text-slate-900">
                  Ownership
                </label>
                <select
                  id="ownership"
                  value={ownership}
                  onChange={(e) => setOwnership(e.target.value)}
                  className="rounded-md border px-3 py-2 text-sm text-slate-900"
                >
                  <option value="">Select ownership</option>
                  <option value="First">1st</option>
                  <option value="Second">2nd</option>
                  <option value="Third+">3rd</option>
                  <option value="Third+">4th+</option>
                </select>
              </div> 
              
            </div> */}
            {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
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
            <div className="flex flex-col items-center">
              {loading ? (
                  <div className="text-sm text-slate-600">Calculating demand…</div>
                ) : score == null ? (
                  <div className="text-sm text-slate-600">No score available.</div>
                ) : (
                  <CircularDemandMeter value={score} />
                )}

              <div className="mt-6 flex items-center gap-3">
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
