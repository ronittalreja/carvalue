"use client"

import type React from "react"
import { memo, useCallback, useEffect, useMemo, useRef, useState, useTransition } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"

type FormData = {
  company: string
  carModel: string
  year: number
  fuelType: string
  kmDriven: string
  transmission: string
  ownership: string
}

const years = Array.from({ length: 21 }, (_, i) => 2025 - i)
const fuelTypes = ["Petrol", "Diesel", "CNG", "Hybrid", "Electric"]
const transmissions = ["Manual", "Automatic", "AMT", "CVT", "DCT"]
const ownerships = ["1st", "2nd", "3rd", "4th+"]

const formatINR = (n: number | string) => (Number.isFinite(Number(n)) ? Number(n).toLocaleString("en-IN") : String(n))

export default function CarPriceForm() {
  const [step, setStep] = useState(1)
  const [isPending, startTransition] = useTransition()
  const [formData, setFormData] = useState<FormData>({
    company: "",
    carModel: "",
    year: years[0],
    fuelType: fuelTypes[0],
    kmDriven: "",
    transmission: transmissions[0],
    ownership: ownerships[0],
  })
  const [companies, setCompanies] = useState<string[]>([])
  const [models, setModels] = useState<string[]>([])
  const [prediction, setPrediction] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Load companies once
  useEffect(() => {
    let active = true
    ;(async () => {
      try {
        const res = await fetch("/api/car-data")
        const data = await res.json()
        if (!active) return
        setCompanies(data.companies || [])
        if (data.companies?.length) {
          setFormData((p) => ({ ...p, company: data.companies[0] }))
        }
      } catch {
        setCompanies(["Maruti", "Hyundai", "Honda", "Toyota", "Ford"])
      }
    })()
    return () => {
      active = false
    }
  }, [])

  // Load models when company changes
  useEffect(() => {
    if (!formData.company) return
    let active = true
    ;(async () => {
      try {
        const res = await fetch(`/api/car-models?company=${encodeURIComponent(formData.company)}`)
        const data = await res.json()
        if (!active) return
        setModels(data.models || [])
        if (data.models?.length) {
          setFormData((p) => ({ ...p, carModel: data.models[0] }))
        }
      } catch {
        setModels([])
      }
    })()
    return () => {
      active = false
    }
  }, [formData.company])

  const setField = useCallback(
    (name: keyof FormData, value: string | number) => {
      startTransition(() => {
        setFormData((prev) => ({ ...prev, [name]: value as never }))
      })
    },
    [startTransition],
  )

  const nextStep = () => setStep((s) => Math.min(8, s + 1))
  const prevStep = () => setStep((s) => Math.max(1, s - 1))

  const canSave = useMemo(() => !isLoading && prediction && !error, [isLoading, prediction, error])

  const saveToLocal = () => {
    if (!canSave) return
    const list = JSON.parse(localStorage.getItem("saved-predictions") || "[]")
    const item = { ...formData, prediction, savedAt: new Date().toISOString() }
    localStorage.setItem("saved-predictions", JSON.stringify([item, ...list]))
  }

  const predictPrice = async () => {
  setIsLoading(true)
  setError(null)
  setPrediction(null)

  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        company: formData.company,
        car_model: formData.carModel,
        year: Number(formData.year),
        fuel_type: formData.fuelType,
        kms_driven: Number(formData.kmDriven) || 0,
        transmission: formData.transmission,
        owners: Number(formData.ownership.replace(/\D/g, "")) || 1, // Changed from ownership → owners
      }),
    })

    if (!response.ok) throw new Error(`API ${response.status}`)

    const data = await response.json()
    const price = Number.parseFloat(data.prediction)
    setPrediction(Number.isFinite(price) ? formatINR(price) : data.prediction)
  } catch (e) {
    setError("Could not predict price. Please try again.")
  } finally {
    setIsLoading(false)
  }
}


  return (
    <Card className="border-0 shadow-xl ring-1 ring-black/5">
      <CardHeader>
        <CardTitle className="text-2xl">Car Price Predictor</CardTitle>
      </CardHeader>
      <CardContent>
        {/* Fix overflow: wrap in overflow-x-auto and responsive sizing */}
        <Stepper current={step} total={8} />

        <AnimatePresence mode="wait" initial={false}>
          {step === 1 && (
            <Step keyName="step-1">
              <Field label="Select the company">
                <select
                  name="company"
                  value={formData.company}
                  onChange={(e) => setField("company", e.target.value)}
                  className="w-full rounded-lg border px-3 py-2 focus:ring-2 focus:ring-blue-500"
                >
                  {companies.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </Field>
              <Nav next onNext={nextStep} disabled={!formData.company} />
            </Step>
          )}

          {step === 2 && (
            <Step keyName="step-2">
              <Field label="Select the model">
                <select
                  name="carModel"
                  value={formData.carModel}
                  onChange={(e) => setField("carModel", e.target.value)}
                  className="w-full rounded-lg border px-3 py-2 focus:ring-2 focus:ring-blue-500"
                >
                  {models.map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
              </Field>
              <Nav prev onPrev={prevStep} next onNext={nextStep} disabled={!formData.carModel} />
            </Step>
          )}

          {step === 3 && (
            <Step keyName="step-3">
              <Field label="Select year of purchase">
                <select
                  name="year"
                  value={formData.year}
                  onChange={(e) => setField("year", Number(e.target.value))}
                  className="w-full rounded-lg border px-3 py-2 focus:ring-2 focus:ring-blue-500"
                >
                  {years.map((y) => (
                    <option key={y} value={y}>
                      {y}
                    </option>
                  ))}
                </select>
              </Field>
              <Nav prev onPrev={prevStep} next onNext={nextStep} />
            </Step>
          )}

          {step === 4 && (
            <Step keyName="step-4">
              <Field label="Select the fuel type">
                <select
                  name="fuelType"
                  value={formData.fuelType}
                  onChange={(e) => setField("fuelType", e.target.value)}
                  className="w-full rounded-lg border px-3 py-2 focus:ring-2 focus:ring-blue-500"
                >
                  {fuelTypes.map((f) => (
                    <option key={f} value={f}>
                      {f}
                    </option>
                  ))}
                </select>
              </Field>
              <Nav prev onPrev={prevStep} next onNext={nextStep} />
            </Step>
          )}

          {step === 5 && (
            <Step keyName="step-5">
              <Field label="Enter kilometers driven">
                <KiloInput value={formData.kmDriven} onDebouncedChange={(val) => setField("kmDriven", val)} />
              </Field>
              <Nav prev onPrev={prevStep} next onNext={nextStep} disabled={!formData.kmDriven} />
            </Step>
          )}

          {step === 6 && (
            <Step keyName="step-6">
              <Field label="Select transmission">
                <select
                  name="transmission"
                  value={formData.transmission}
                  onChange={(e) => setField("transmission", e.target.value)}
                  className="w-full rounded-lg border px-3 py-2 focus:ring-2 focus:ring-blue-500"
                >
                  {transmissions.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </Field>
              <Nav prev onPrev={prevStep} next onNext={nextStep} />
            </Step>
          )}

          {step === 7 && (
            <Step keyName="step-7">
              <Field label="Ownership">
                <select
                  name="ownership"
                  value={formData.ownership}
                  onChange={(e) => setField("ownership", e.target.value)}
                  className="w-full rounded-lg border px-3 py-2 focus:ring-2 focus:ring-blue-500"
                >
                  {ownerships.map((o) => (
                    <option key={o} value={o}>
                      {o}
                    </option>
                  ))}
                </select>
              </Field>
              <div className="flex items-center justify-between">
                <Button variant="outline" onClick={prevStep}>
                  Back
                </Button>
                <Button
                  onClick={() => {
                    predictPrice()
                    nextStep()
                  }}
                  className="bg-blue-600 hover:bg-blue-700"
                  disabled={!formData.ownership}
                >
                  Predict Price
                </Button>
              </div>
            </Step>
          )}

          {step === 8 && (
            <motion.div
              key="step-8"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ type: "spring", stiffness: 180, damping: 20 }}
              className="space-y-6"
            >
              <Card className="bg-gradient-to-br from-blue-50 to-white border-blue-100">
                <CardContent className="pt-6">
                  <div className="text-sm text-gray-600 mb-2">Estimated Resale Value in 2025</div>
                  <div className="text-4xl font-extrabold text-blue-700">₹ {prediction ?? "—"}</div>
                  <div className="mt-4 rounded-lg bg-white/70 p-4 ring-1 ring-black/5 space-y-1">
                    <p className="font-medium">
                      {formData.company} {formData.carModel}
                    </p>
                    <p className="text-sm text-gray-600">
                      {formData.year} • {formData.fuelType} • {formData.kmDriven} km
                    </p>
                    <p className="text-sm text-gray-600">
                      {formData.transmission} • {formData.ownership} owner
                    </p>
                  </div>
                  {error && (
                    <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-red-700">
                      {error}
                    </div>
                  )}
                </CardContent>
                <CardFooter className="flex items-center justify-between">
                  <Button variant="outline" onClick={() => setStep(1)}>
                    Start Over
                  </Button>
                  <Button onClick={saveToLocal} disabled={!canSave} className="bg-blue-600 hover:bg-blue-700">
                    Save
                  </Button>
                </CardFooter>
              </Card>

              {isLoading && (
                <div className="flex justify-center items-center py-4">
                  <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500" />
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </CardContent>
    </Card>
  )
}

/* ---------- Subcomponents ---------- */

const Step = memo(function Step({ keyName, children }: { keyName: string; children: React.ReactNode }) {
  return (
    <motion.div
      key={keyName}
      initial={{ opacity: 0, x: 24 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -24 }}
      transition={{ type: "spring", stiffness: 220, damping: 22 }}
      className="space-y-5"
    >
      {children}
    </motion.div>
  )
})

const Field = ({ label, children }: { label: string; children: React.ReactNode }) => (
  <div className="space-y-2">
    <Label className="text-gray-800">{label}</Label>
    {children}
  </div>
)

const Nav = ({
  prev,
  next,
  onPrev,
  onNext,
  disabled,
}: {
  prev?: boolean
  next?: boolean
  onPrev?: () => void
  onNext?: () => void
  disabled?: boolean
}) => (
  <div className="flex items-center justify-between">
    <Button variant="outline" onClick={onPrev} disabled={!prev}>
      Back
    </Button>
    <Button onClick={onNext} disabled={!next || disabled} className={cn("bg-blue-600 hover:bg-blue-700")}>
      Next
    </Button>
  </div>
)

// Debounced km input to avoid lag on every keystroke
const KiloInput = memo(function KiloInput({
  value,
  onDebouncedChange,
}: {
  value: string
  onDebouncedChange: (v: string) => void
}) {
  const [local, setLocal] = useState(value ?? "")
  const t = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    setLocal(value ?? "")
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (t.current) clearTimeout(t.current)
    t.current = setTimeout(() => {
      onDebouncedChange(local)
    }, 180)
    return () => {
      if (t.current) clearTimeout(t.current)
    }
  }, [local, onDebouncedChange])

  return (
    <Input
      type="tel"
      inputMode="numeric"
      placeholder="e.g. 30000"
      value={local}
      onChange={(e) => setLocal(e.target.value.replace(/[^\d]/g, ""))}
      className="h-11"
    />
  )
})

const Stepper = memo(function Stepper({ current, total }: { current: number; total: number }) {
  return (
    <div className="mb-6 w-full">
      <div className="flex items-center w-full">
        {Array.from({ length: total }).map((_, i) => {
          const isActive = i + 1 === current
          const isDone = i + 1 < current
          const circleClass = isActive
            ? "bg-blue-600 text-white border-blue-600"
            : isDone
              ? "bg-emerald-500 text-white border-emerald-500"
              : "bg-gray-100 text-gray-600 border-gray-200"

          return (
            <div key={i} className="flex items-center w-full">
              <div
                className={`w-6 h-6 md:w-7 md:h-7 rounded-full flex items-center justify-center text-[10px] md:text-xs border shrink-0 ${circleClass}`}
              >
                {isDone ? "✓" : i + 1}
              </div>
              {i < total - 1 && (
                <div className={`h-0.5 mx-1 md:mx-2 flex-1 rounded ${isDone ? "bg-emerald-500" : "bg-gray-200"}`} />
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
})
