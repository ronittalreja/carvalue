"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"

type SavedItem = {
  company: string
  carModel: string
  year: number
  fuelType: string
  kmDriven: string
  transmission: string
  ownership: string
  serviceHistory: boolean
  previousAccidents: boolean
  insurance: string
  prediction: string
  savedAt: string
}

export default function SavedPage() {
  const [items, setItems] = useState<SavedItem[]>([])

  useEffect(() => {
    const list = JSON.parse(localStorage.getItem("saved-predictions") || "[]")
    setItems(list)
  }, [])

  const remove = (i: number) => {
    const next = items.slice()
    next.splice(i, 1)
    setItems(next)
    localStorage.setItem("saved-predictions", JSON.stringify(next))
  }

  if (!items.length) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-10">
        <h1 className="text-2xl font-bold mb-4">Saved Predictions</h1>
        <p className="text-gray-600">No saved predictions yet. Make a prediction and press Save.</p>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <h1 className="text-2xl font-bold mb-6">Saved Predictions</h1>
      <div className="space-y-4">
        {items.map((it, i) => (
          <div key={i} className="border rounded-lg p-4 flex items-start justify-between">
            <div className="flex-1">
              <p className="font-medium text-lg">
                {it.company} {it.carModel}
              </p>
              <div className="text-sm text-gray-600 mt-2 space-y-1">
                <p>Year: {it.year}</p>
                <p>Fuel Type: {it.fuelType}</p>
                <p>KM Driven: {it.kmDriven}</p>
                <p>Transmission: {it.transmission}</p>
                <p>Ownership: {it.ownership}</p>
                <p>Service history available?: {it.serviceHistory ? "Yes" : "No"}</p>
                <p>Has the car been in an accident?: {it.previousAccidents ? "Yes" : "No"}</p>
                <p>Car's insurance type: {it.insurance}</p>
              </div>
              <p className="text-blue-600 font-bold mt-3 text-lg">₹ {it.prediction}</p>
              <p className="text-xs text-gray-400 mt-1">Saved: {new Date(it.savedAt).toLocaleString()}</p>
            </div>
            <Button variant="outline" onClick={() => remove(i)} className="ml-4">
              Remove
            </Button>
          </div>
        ))}
      </div>
    </div>
  )
}
