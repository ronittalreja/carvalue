"use client"

import type React from "react"

import { useState, useEffect } from "react"
import type { CarInput, FuelType } from "@/lib/types"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"

const fuels: FuelType[] = ["Petrol", "Diesel", "CNG", "EV"]
const years = Array.from({ length: 20 }, (_, i) => new Date().getFullYear() - i)

export function CarSearchForm({
  initial,
  compact,
  onSubmit,
}: {
  initial?: Partial<CarInput>
  compact?: boolean
  onSubmit?: (val: CarInput) => void
}) {

  const [modelsByCompany, setModelsByCompany] = useState<Record<string, string[]>>({})

  // Initialize with empty values and proper placeholders
  const [year, setYear] = useState<string>("")
  const [fuel, setFuel] = useState<string>("")
  const [kmDriven, setKmDriven] = useState<string>("") // Changed to string for text input
  const [transmission, setTransmission] = useState<string>("")
  const [ownership, setOwnership] = useState<string>("")
  
  // Initialize arrays to prevent undefined errors
  const [companies, setCompanies] = useState<string[]>([])
  const [transmissions, setTransmissions] = useState<string[]>([])
  const [owners, setOwners] = useState<string[]>([])
  
  const [company, setCompany] = useState<string>("")
  const [model, setModel] = useState<string>("")

  // Loading states
  const [loading, setLoading] = useState({
    companies: false,
    models: false,
    transmissions: false,
    owners: false
  })

  // Error states
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [submitError, setSubmitError] = useState<string>("")

  const API_BASE = "https://carvalue.onrender.com"

  // Set initial values if provided (only for edit mode)
  useEffect(() => {
    if (initial) {
      if (initial.year) setYear(String(initial.year))
      if (initial.fuel) setFuel(initial.fuel)
      if (initial.kmDriven) setKmDriven(String(initial.kmDriven))
      if (initial.model) setModel(initial.model)
    }
  }, [initial])

  // Fetch companies on mount
  useEffect(() => {
    setLoading(prev => ({ ...prev, companies: true }))
    fetch(`${API_BASE}/companies`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then(data => {
        const companiesArray = Array.isArray(data.companies) ? data.companies : []
        setCompanies(companiesArray)
        
        // Only set initial company if provided in initial prop
        if (initial?.company && companiesArray.includes(initial.company.toLowerCase())) {
          setCompany(initial.company.toLowerCase())
        }
      })
      .catch(err => {
        console.error("Failed to fetch companies:", err)
        setErrors(prev => ({ ...prev, companies: "Failed to load companies. Please try again later." }))
        setCompanies([])
      })
      .finally(() => {
        setLoading(prev => ({ ...prev, companies: false }))
      })
  }, [initial?.company])

  // Fetch transmissions on mount
  useEffect(() => {
    setLoading(prev => ({ ...prev, transmissions: true }))
    fetch(`${API_BASE}/transmissions`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then(data => {
        const transmissionsArray = Array.isArray(data.transmissions) ? data.transmissions : []
        setTransmissions(transmissionsArray)
        
        // Only set initial transmission if provided
        if (initial?.transmission && transmissionsArray.includes(initial.transmission.toLowerCase())) {
          setTransmission(initial.transmission.toLowerCase())
        }
      })
      .catch(err => {
        console.error("Failed to fetch transmissions:", err)
        setTransmissions(["manual", "automatic", "amt", "cvt", "dct"])
        setErrors(prev => ({ ...prev, transmissions: "Using default transmission options" }))
      })
      .finally(() => {
        setLoading(prev => ({ ...prev, transmissions: false }))
      })
  }, [initial?.transmission])

  // Fetch owners on mount
  useEffect(() => {
    setLoading(prev => ({ ...prev, owners: true }))
    fetch(`${API_BASE}/owners`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then(data => {
        const ownersArray = Array.isArray(data.owners) 
          ? data.owners.map(o => String(o)) 
          : []
        setOwners(ownersArray)
        
        // Only set initial ownership if provided
        if (initial?.ownership && ownersArray.includes(String(initial.ownership))) {
          setOwnership(String(initial.ownership))
        }
      })
      .catch(err => {
        console.error("Failed to fetch owners:", err)
        setOwners(["1", "2", "3", "4"])
        setErrors(prev => ({ ...prev, owners: "Using default owner options" }))
      })
      .finally(() => {
        setLoading(prev => ({ ...prev, owners: false }))
      })
  }, [initial?.ownership])

  // Fetch models when company changes
  useEffect(() => {
    if (!company) return
    
    setLoading(prev => ({ ...prev, models: true }))
    fetch(`${API_BASE}/models/${encodeURIComponent(company.toLowerCase())}`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then(data => {
        const modelsArray = Array.isArray(data.models) ? data.models : []
        setModelsByCompany(prev => ({ ...prev, [company]: modelsArray }))
        
        // Only set model if it exists in the fetched models or if it's initial value
        if (initial?.model && modelsArray.includes(initial.model.toLowerCase())) {
          setModel(initial.model.toLowerCase())
        } else if (!initial?.model) {
          setModel("") // Reset model for new company selection
        }
      })
      .catch(err => {
        console.error(`Failed to fetch models for ${company}:`, err)
        setModelsByCompany(prev => ({ ...prev, [company]: [] }))
        setModel("")
        setErrors(prev => ({ ...prev, models: `Failed to load models for ${company}. Please try again later.` }))
      })
      .finally(() => {
        setLoading(prev => ({ ...prev, models: false }))
      })
  }, [company, initial?.model])

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()

    // Clear previous errors
    setErrors({})
    setSubmitError("")

    // Validate required fields
    const newErrors: Record<string, string> = {}
    
    if (!company) newErrors.company = "Please select a company"
    if (!model) newErrors.model = "Please select a model"
    if (!year) newErrors.year = "Please select a year"
    if (!fuel) newErrors.fuel = "Please select fuel type"
    if (!transmission) newErrors.transmission = "Please select transmission type"
    if (!ownership) newErrors.ownership = "Please select ownership"
    if (!kmDriven || kmDriven.trim() === "") {
      newErrors.kmDriven = "Please enter kilometers driven"
    } else if (isNaN(Number(kmDriven)) || Number(kmDriven) < 0) {
      newErrors.kmDriven = "Please enter a valid number for kilometers"
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    try {
      // Submit the form
      onSubmit?.({ 
        company, 
        model, 
        year: Number(year), 
        fuel: fuel as FuelType, 
        kmDriven: Number(kmDriven), 
        transmission, 
        ownership 
      })
    } catch (error) {
      setSubmitError("Please try again later")
    }
  }

  // Helper function to capitalize first letter
  const capitalize = (str: string) => str.charAt(0).toUpperCase() + str.slice(1)

  return (
    <div className="grid gap-4">
      {submitError && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-600">{submitError}</p>
        </div>
      )}
      
      <div className={`grid ${compact ? "grid-cols-2" : "grid-cols-2 md:grid-cols-3"} gap-4`}>
        
        {/* Company Selection */}
        <div className="grid gap-2">
          <Label>Company</Label>
          {loading.companies ? (
            <div className="text-sm text-gray-500">Loading companies...</div>
          ) : (
            <Select value={company} onValueChange={(v) => {
              setCompany(v)
              setModel("") // Reset model when company changes
            }}>
              <SelectTrigger>
                <SelectValue placeholder="Select company" />
              </SelectTrigger>
              <SelectContent>
                {companies.map(c => (
                  <SelectItem key={c} value={c}>{capitalize(c)}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
          {errors.company && <p className="text-sm text-red-600">{errors.company}</p>}
          {errors.companies && <p className="text-sm text-red-600">{errors.companies}</p>}
        </div>

        {/* Model Selection */}
        <div className="grid gap-2">
          <Label>Model</Label>
          {loading.models ? (
            <div className="text-sm text-gray-500">Loading models...</div>
          ) : (
            <Select value={model} onValueChange={(v) => setModel(v)} disabled={!company}>
              <SelectTrigger>
                <SelectValue placeholder="Select model" />
              </SelectTrigger>
              <SelectContent>
                {(modelsByCompany[company] || []).map((m) => (
                  <SelectItem key={m} value={m}>
                    {capitalize(m)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
          {errors.model && <p className="text-sm text-red-600">{errors.model}</p>}
          {errors.models && <p className="text-sm text-red-600">{errors.models}</p>}
        </div>

        {/* Year Selection */}
        {!compact && (
          <div className="grid gap-2">
            <Label>Year</Label>
            <Select value={year} onValueChange={(v) => setYear(v)}>
              <SelectTrigger>
                <SelectValue placeholder="Select year" />
              </SelectTrigger>
              <SelectContent>
                {years.map((y) => (
                  <SelectItem key={y} value={String(y)}>
                    {y}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.year && <p className="text-sm text-red-600">{errors.year}</p>}
          </div>
        )}

        {/* Fuel Selection */}
        {!compact && (
          <div className="grid gap-2">
            <Label>Fuel Type</Label>
            <Select value={fuel} onValueChange={(v) => setFuel(v)}>
              <SelectTrigger>
                <SelectValue placeholder="Select fuel type" />
              </SelectTrigger>
              <SelectContent>
                {fuels.map((f) => (
                  <SelectItem key={f} value={f}>
                    {f}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.fuel && <p className="text-sm text-red-600">{errors.fuel}</p>}
          </div>
        )}

        {/* Kilometers Input - Changed to text input */}
        {!compact && (
          <div className="grid gap-2">
            <Label htmlFor="km">Kilometers Driven</Label>
            <Input
              id="km"
              type="text"
              placeholder="Enter kilometers driven"
              value={kmDriven}
              onChange={(e) => {
                // Only allow numbers and remove any non-numeric characters except for temporary input
                const value = e.target.value
                if (value === "" || /^\d+$/.test(value)) {
                  setKmDriven(value)
                }
              }}
            />
            {errors.kmDriven && <p className="text-sm text-red-600">{errors.kmDriven}</p>}
          </div>
        )}
                
        {/* Transmission Selection */}
        <div className="grid gap-2">
          <Label>Transmission</Label>
          {loading.transmissions ? (
            <div className="text-sm text-gray-500">Loading...</div>
          ) : (
            <Select value={transmission} onValueChange={(v) => setTransmission(v)}>
              <SelectTrigger>
                <SelectValue placeholder="Select transmission type" />
              </SelectTrigger>
              <SelectContent>
                {transmissions.map(t => (
                  <SelectItem key={t} value={t}>{capitalize(t)}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
          {errors.transmission && <p className="text-sm text-red-600">{errors.transmission}</p>}
          {errors.transmissions && <p className="text-sm text-red-600">{errors.transmissions}</p>}
        </div>

        {/* Ownership Selection */}
        <div className="grid gap-2">
          <Label>Ownership</Label>
          {loading.owners ? (
            <div className="text-sm text-gray-500">Loading...</div>
          ) : (
            <Select value={ownership} onValueChange={(v) => setOwnership(v)}>
              <SelectTrigger>
                <SelectValue placeholder="Select ownership" />
              </SelectTrigger>
              <SelectContent>
                {owners.map(o => (
                  <SelectItem key={o} value={o}>
                    {o} {o === '1' ? 'Owner' : 'Owners'}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
          {errors.ownership && <p className="text-sm text-red-600">{errors.ownership}</p>}
          {errors.owners && <p className="text-sm text-red-600">{errors.owners}</p>}
        </div>

      </div>
      
      <div>
        <Button 
          onClick={handleSubmit}
          className="bg-blue-600 text-white hover:bg-blue-700"
          disabled={loading.companies || loading.models || loading.transmissions || loading.owners}
        >
          {loading.companies || loading.models || loading.transmissions || loading.owners 
            ? "Loading..." 
            : "Get Estimate"}
        </Button>
      </div>
    </div>
  )
}