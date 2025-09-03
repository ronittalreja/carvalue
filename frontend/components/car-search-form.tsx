"use client"

import type React from "react"

import { useState,useEffect } from "react"
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

  const [year, setYear] = useState<number>(initial?.year ?? years[5])
  const [fuel, setFuel] = useState<FuelType>(initial?.fuel ?? "Petrol")
  const [kmDriven, setKmDriven] = useState<number>(initial?.kmDriven ?? 0)
  const [transmission, setTransmission] = useState<string>("Manual")
  const [ownership, setOwnership] = useState<string>("First")
  const [companies, setCompanies] = useState<string[]>([])
  const [company, setCompany] = useState<string>("")  // empty at first

  const [model, setModel] = useState(initial?.model ?? "")


useEffect(() => {
  fetch("http://localhost:8000/companies")
    .then(res => res.json())
    .then(data => {
      setCompanies(data.companies)
      if (data.companies.length > 0) {
        setCompany(data.companies[0])  // set first company
        setModel("")                  // clear model, will fetch next
      }
    })
    .catch(err => console.error("Failed to fetch companies:", err))
}, [])


useEffect(() => {
  if (!company) return
  fetch(`http://localhost:8000/models/${company.toLowerCase()}`)
    .then(res => res.json())
    .then(data => {
      setModelsByCompany(prev => ({ ...prev, [company]: data.models }))
      if (data.models.length > 0) setModel(data.models[0])
    })
    .catch(err => console.error(`Failed to fetch models for ${company}:`, err))
}, [company])

  function handleSubmit(e: React.FormEvent) {
  e.preventDefault()

  if (!transmission || !ownership) {
    alert("Please select Transmission and Ownership before submitting.")
    return
  }

  onSubmit?.({ company, model, year, fuel, kmDriven, transmission, ownership })
}


  return (
    <form onSubmit={handleSubmit} className="grid gap-4">
      <div className={`grid ${compact ? "grid-cols-2" : "grid-cols-2 md:grid-cols-3"} gap-4`}>
          <div className="grid gap-2">
  <Label>Company</Label>
<Select value={company} onValueChange={(v) => setCompany(v)}>
        <SelectTrigger>
      <SelectValue placeholder="Select model" />
    </SelectTrigger>
  <SelectContent>
    {companies.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
  </SelectContent>
</Select>

<Select value={model} onValueChange={(v) => setModel(v)}>

  <SelectContent>
    {(modelsByCompany[company] || []).map(m => (
      <SelectItem key={m} value={m}>{m}</SelectItem>
    ))}
  </SelectContent>
</Select>
</div>
<div className="grid gap-2">
  <Label>Model</Label>
  <Select value={model} onValueChange={(v) => setModel(v)}>
    <SelectTrigger>
      <SelectValue placeholder="Select model" />
    </SelectTrigger>
    <SelectContent>
      {(modelsByCompany[company] || []).map((m) => (
        <SelectItem key={m} value={m}>
          {m}
        </SelectItem>
      ))}
    </SelectContent>
  </Select>
</div>



        {!compact && (
          <div className="grid gap-2">
            <Label>Year</Label>
            <Select value={String(year)} onValueChange={(v) => setYear(Number(v))}>
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
          </div>
        )}

        {!compact && (
          <div className="grid gap-2">
            <Label>Fuel</Label>
            <Select value={fuel} onValueChange={(v) => setFuel(v as FuelType)}>
              <SelectTrigger>
                <SelectValue placeholder="Fuel type" />
              </SelectTrigger>
              <SelectContent>
                {fuels.map((f) => (
                  <SelectItem key={f} value={f}>
                    {f}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}
        {!compact && (
          <div className="grid gap-2">
            <Label htmlFor="km">Kilometers</Label>
            <Input
              id="km"
              type="number"
              min={0}
              step={1000}
              value={kmDriven}
              onChange={(e) => setKmDriven(Number(e.target.value))}
            />
          </div>
        )}
                
            <div className="grid gap-2">
              <Label>Transmission</Label>
              <Select value={transmission} onValueChange={(v) => setTransmission(v)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select transmission" />
                </SelectTrigger>
                <SelectContent>
                  {["Manual","Automatic","AMT","CVT","DCT"].map(t => (
                    <SelectItem key={t} value={t}>{t}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
              <div className="grid gap-2">
                    <Label>Ownership</Label>
                    <Select value={ownership} onValueChange={(v) => setOwnership(v)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select ownership" />
                      </SelectTrigger>
                      <SelectContent>
                        {["First","Second","Third+","fourth+"].map(o => (
                          <SelectItem key={o} value={o}>{o}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
              </div>

      </div>
      <div>
        <Button className="bg-blue-600 text-white hover:bg-blue-700">Get Estimate</Button>
      </div>
    </form>
  )
}
