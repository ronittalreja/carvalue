export type FuelType = "Petrol" | "Diesel" | "CNG" | "EV"

export interface CarInput {
  company: string
  model: string
  year: number
  fuel: FuelType
  kmDriven: number
  transmission?: string   // optional
  ownership?: string      
}

export interface DepreciationPoint {
  year: number
  valueINR: number
}

export interface FuelComparisonPoint {
  fuel: FuelType
  value: number
}

export interface PredictionResult {
  priceINR: number
  year: number
  confidence?: number
  insights?: string[]
  depreciation?: DepreciationPoint[]
  fuelComparison?: FuelComparisonPoint[]
}

export interface SavedItem {
  id: string
  input: CarInput
  result: PredictionResult
  createdAt: string
}
