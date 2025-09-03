"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"

type SavedItem = {
  company: string
  carModel: string
  year: number
  fuelType: string
  kmDriven: string
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
          <div key={i} className="border rounded-lg p-4 flex items-center justify-between">
            <div>
              <p className="font-medium">
                {it.company} {it.carModel}
              </p>
              <p className="text-sm text-gray-600">
                {it.year} • {it.fuelType} • {it.kmDriven} km
              </p>
              <p className="text-blue-600 font-bold mt-1">₹ {it.prediction}</p>
            </div>
            <Button variant="outline" onClick={() => remove(i)}>
              Remove
            </Button>
          </div>
        ))}
      </div>
    </div>
  )
}
