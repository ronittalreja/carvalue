"use client"

import type React from "react"

import { useEffect, useMemo, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Bar } from "react-chartjs-2"
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from "chart.js"

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

type Selector = {
  company: string
  model: string
  year: number
  fuel: string
  km: string
  transmission: string
  ownership: string
}

const years = Array.from({ length: 21 }, (_, i) => 2025 - i)
const fuels = ["Petrol", "Diesel", "CNG", "Electric", "Hybrid"]
const transmissions = ["Manual", "Automatic", "AMT", "CVT", "DCT"]
const ownerships = ["1st", "2nd", "3rd", "4th+"]
const formatINR = (n?: number | null) => (n == null ? "—" : n.toLocaleString("en-IN"))

export default function ComparePage() {
  const [companies, setCompanies] = useState<string[]>([])
  const [modelsA, setModelsA] = useState<string[]>([])
  const [modelsB, setModelsB] = useState<string[]>([])

  const [a, setA] = useState<Selector>({
    company: "",
    model: "",
    year: years[0],
    fuel: fuels[0],
    km: "30000",
    transmission: transmissions[0],
    ownership: ownerships[0],
  })
  const [b, setB] = useState<Selector>({
    company: "",
    model: "",
    year: years[0],
    fuel: fuels[0],
    km: "30000",
    transmission: transmissions[0],
    ownership: ownerships[0],
  })

  const [predA, setPredA] = useState<number | null>(null)
  const [predB, setPredB] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    ;(async () => {
      const res = await fetch("/api/car-data")
      const data = await res.json()
      setCompanies(data.companies || [])
      if (data.companies?.length) {
        setA((p) => ({ ...p, company: data.companies[0] }))
        setB((p) => ({ ...p, company: data.companies[0] }))
      }
    })()
  }, [])

  useEffect(() => {
    if (!a.company) return
    ;(async () => {
      const res = await fetch(`/api/car-models?company=${encodeURIComponent(a.company)}`)
      const data = await res.json()
      setModelsA(data.models || [])
      if (data.models?.length) setA((p) => ({ ...p, model: data.models[0] }))
    })()
  }, [a.company])

  useEffect(() => {
    if (!b.company) return
    ;(async () => {
      const res = await fetch(`/api/car-models?company=${encodeURIComponent(b.company)}`)
      const data = await res.json()
      setModelsB(data.models || [])
      if (data.models?.length) setB((p) => ({ ...p, model: data.models[0] }))
    })()
  }, [b.company])

  const predict = async () => {
    setLoading(true)
    try {
      const ownershipMap: Record<string, number> = {
        "1st": 1,
        "2nd": 2,
        "3rd": 3,
        "4th+": 4,
      }

      const [ra, rb] = await Promise.all([
        fetch("/api/predict", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            company: a.company,
            car_model: a.model,
            year: a.year,
            fuel_type: a.fuel,
            kms_driven: Number(a.km),
            transmission: a.transmission,
            owners: ownershipMap[a.ownership] || 1,
          }),
        }),
        fetch("/api/predict", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            company: b.company,
            car_model: b.model,
            year: b.year,
            fuel_type: b.fuel,
            kms_driven: Number(b.km),
            transmission: b.transmission,
            owners: ownershipMap[b.ownership] || 1,
          }),
        }),
      ])
      const ja = await ra.json()
      const jb = await rb.json()
      setPredA(Number.parseFloat(ja.prediction))
      setPredB(Number.parseFloat(jb.prediction))
    } finally {
      setLoading(false)
    }
  }

  const chartData = useMemo(
    () => ({
      labels: ["Car A", "Car B"],
      datasets: [
        {
          label: "Predicted Price (₹)",
          data: [predA ?? 0, predB ?? 0],
          backgroundColor: ["#3b82f6", "#22c55e"],
          borderRadius: 8,
        },
      ],
    }),
    [predA, predB],
  )

  const [mounted, setMounted] = useState(false)

useEffect(() => {
  setMounted(true)
}, [])

if (!mounted) return null // prevent SSR render mismatch

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <h1 className="text-3xl font-bold mb-6">Compare Cars</h1>

      <div className="grid md:grid-cols-2 gap-6">
        <SelectorCard title="Car A" companies={companies} models={modelsA} selector={a} setSelector={setA} />
        <SelectorCard title="Car B" companies={companies} models={modelsB} selector={b} setSelector={setB} />
      </div>

      <div className="flex items-center gap-3 mt-6">
        <Button onClick={predict} disabled={loading} className="bg-blue-600 hover:bg-blue-700">
          {loading ? "Comparing..." : "Compare"}
        </Button>
      </div>

      {(predA !== null || predB !== null) && (
        <div className="mt-8 grid md:grid-cols-3 gap-6">
          <Card className="md:col-span-1">
            <CardHeader>
              <CardTitle>Prices</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="rounded-lg border p-3">
                <p className="text-sm text-gray-500">Car A</p>
                <p className="text-2xl font-bold text-blue-600">₹ {formatINR(predA)}</p>
              </div>
              <div className="rounded-lg border p-3">
                <p className="text-sm text-gray-500">Car B</p>
                <p className="text-2xl font-bold text-emerald-600">₹ {formatINR(predB)}</p>
              </div>
              {predA !== null && predB !== null && (
                <div className="rounded-lg bg-slate-50 p-3 border">
                  <p className="text-sm text-gray-600">Difference</p>
                  <p className="text-xl font-semibold">₹ {formatINR(Math.abs((predA || 0) - (predB || 0)))}</p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle>Comparison</CardTitle>
            </CardHeader>
            <CardContent>
              <Bar data={chartData} />
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}

function SelectorCard({
  title,
  companies,
  models,
  selector,
  setSelector,
}: {
  title: string
  companies: string[]
  models: string[]
  selector: Selector
  setSelector: React.Dispatch<React.SetStateAction<Selector>>
}) {
  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-3">
        <select
          className="p-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          value={selector.company}
          onChange={(e) => setSelector((p) => ({ ...p, company: e.target.value }))}
        >
          {companies.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
        <select
          className="p-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          value={selector.model}
          onChange={(e) => setSelector((p) => ({ ...p, model: e.target.value }))}
        >
          {models.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
        <select
          className="p-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          value={selector.year}
          onChange={(e) => setSelector((p) => ({ ...p, year: Number(e.target.value) }))}
        >
          {years.map((y) => (
            <option key={y} value={y}>
              {y}
            </option>
          ))}
        </select>
        <select
          className="p-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          value={selector.fuel}
          onChange={(e) => setSelector((p) => ({ ...p, fuel: e.target.value }))}
        >
          {fuels.map((f) => (
            <option key={f} value={f}>
              {f}
            </option>
          ))}
        </select>
        <select
          className="p-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          value={selector.transmission}
          onChange={(e) => setSelector((p) => ({ ...p, transmission: e.target.value }))}
        >
          {transmissions.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>

        <select
          className="p-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          value={selector.ownership}
          onChange={(e) => setSelector((p) => ({ ...p, ownership: e.target.value }))}
        >
          {ownerships.map((o) => (
            <option key={o} value={o}>
              {o}
            </option>
          ))}
        </select>

        <input
          className="p-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          type="tel"
          inputMode="numeric"
          placeholder="Kilometers"
          value={selector.km}
          onChange={(e) => setSelector((p) => ({ ...p, km: e.target.value.replace(/[^\d]/g, "") }))}
        />
      </CardContent>
    </Card>
  )
}
