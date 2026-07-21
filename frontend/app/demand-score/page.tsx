"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ArrowUp, ArrowDown, Minus, TrendingUp, Activity, DollarSign, Calendar } from "lucide-react"

export default function DemandScorePage() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const [formData, setFormData] = useState({
    brand: "",
    model: "",
    variant: "",
    city: "",
    year: "",
    fuel: "",
    transmission: ""
  })

  const cities = ["Mumbai", "Delhi", "Bangalore", "Pune", "Hyderabad", "Chennai", "Kolkata", "Ahmedabad"]
  const fuelTypes = ["Petrol", "Diesel", "Electric", "CNG", "Hybrid"]
  const transmissions = ["Manual", "Automatic"]

  const handleCalculate = async () => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const params = new URLSearchParams()
      if (formData.brand) params.append("brand", formData.brand)
      if (formData.model) params.append("model", formData.model)
      if (formData.variant) params.append("variant", formData.variant)
      if (formData.city) params.append("city", formData.city)
      if (formData.year) params.append("year", formData.year)
      if (formData.fuel) params.append("fuel", formData.fuel)
      if (formData.transmission) params.append("transmission", formData.transmission)

      const response = await fetch(`https://carvalue.onrender.com/api/demand-score?${params.toString()}`)
      
      if (!response.ok) {
        throw new Error("Failed to fetch demand score")
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred")
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 81) return "text-green-600"
    if (score >= 61) return "text-blue-600"
    if (score >= 41) return "text-yellow-600"
    if (score >= 21) return "text-orange-600"
    return "text-red-600"
  }

  const getScoreBgColor = (score: number) => {
    if (score >= 81) return "bg-green-100"
    if (score >= 61) return "bg-blue-100"
    if (score >= 41) return "bg-yellow-100"
    if (score >= 21) return "bg-orange-100"
    return "bg-red-100"
  }

  const getTrendIcon = (trend: string) => {
    if (trend === "Increasing") return <ArrowUp className="h-4 w-4 text-green-600" />
    if (trend === "Decreasing") return <ArrowDown className="h-4 w-4 text-red-600" />
    return <Minus className="h-4 w-4 text-gray-600" />
  }

  const getStars = (score: number) => {
    const stars = Math.round(score / 20)
    return "★".repeat(stars) + "☆".repeat(5 - stars)
  }

  return (
    <section className="min-h-screen bg-gradient-to-b from-blue-50 to-white py-12 px-4">
      <div className="mx-auto max-w-6xl">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Demand Score
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Measure real-time market demand for any used car using live marketplace intelligence.
          </p>
        </div>

        {/* Search Form */}
        <Card className="mb-8 shadow-lg">
          <CardHeader>
            <CardTitle>Search Demand Score</CardTitle>
            <CardDescription>Enter car details to get real-time demand analysis</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="brand">Brand *</Label>
                <Input
                  id="brand"
                  placeholder="e.g., Honda, Maruti, BMW"
                  value={formData.brand}
                  onChange={(e) => setFormData({ ...formData, brand: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="model">Model *</Label>
                <Input
                  id="model"
                  placeholder="e.g., City, Swift, X5"
                  value={formData.model}
                  onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="variant">Variant (Optional)</Label>
                <Input
                  id="variant"
                  placeholder="e.g., ZX CVT, VXi"
                  value={formData.variant}
                  onChange={(e) => setFormData({ ...formData, variant: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="city">City (Optional)</Label>
                <Select value={formData.city} onValueChange={(value) => setFormData({ ...formData, city: value })}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select city" />
                  </SelectTrigger>
                  <SelectContent>
                    {cities.map((city) => (
                      <SelectItem key={city} value={city}>{city}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="year">Year (Optional)</Label>
                <Input
                  id="year"
                  type="number"
                  placeholder="e.g., 2020"
                  value={formData.year}
                  onChange={(e) => setFormData({ ...formData, year: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="fuel">Fuel Type (Optional)</Label>
                <Select value={formData.fuel} onValueChange={(value) => setFormData({ ...formData, fuel: value })}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select fuel type" />
                  </SelectTrigger>
                  <SelectContent>
                    {fuelTypes.map((fuel) => (
                      <SelectItem key={fuel} value={fuel}>{fuel}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="transmission">Transmission (Optional)</Label>
                <Select value={formData.transmission} onValueChange={(value) => setFormData({ ...formData, transmission: value })}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select transmission" />
                  </SelectTrigger>
                  <SelectContent>
                    {transmissions.map((trans) => (
                      <SelectItem key={trans} value={trans}>{trans}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="md:col-span-2">
                <Button 
                  onClick={handleCalculate} 
                  disabled={loading || !formData.brand || !formData.model}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                  size="lg"
                >
                  {loading ? "Calculating..." : "Calculate Demand Score"}
                </Button>
              </div>
            </div>

            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Result Card */}
        {result && (
          <Card className="shadow-xl border-2">
            <CardHeader className="text-center">
              <CardTitle className="text-2xl">
                {formData.brand} {formData.model} {formData.variant}
              </CardTitle>
              <CardDescription>Real-time market demand analysis</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-8">
                {/* Score Section */}
                <div className="text-center space-y-4">
                  <div className={`inline-flex items-center justify-center w-32 h-32 rounded-full ${getScoreBgColor(result.score)} border-4 border-white shadow-lg`}>
                    <div>
                      <div className={`text-4xl font-bold ${getScoreColor(result.score)}`}>
                        {result.score}
                      </div>
                      <div className="text-sm text-gray-600">/ 100</div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="text-2xl text-yellow-500">{getStars(result.score)}</div>
                    <div className={`text-xl font-semibold ${getScoreColor(result.score)}`}>
                      {result.level}
                    </div>
                  </div>
                </div>

                {/* Market Activity Section */}
                <div className="space-y-4">
                  <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                    <Activity className="h-5 w-5" />
                    Market Activity
                  </h3>
                  
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <div className="text-sm text-gray-600">Current Listings</div>
                      <div className="text-xl font-bold text-gray-900">{result.listingCount}</div>
                    </div>
                    
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <div className="text-sm text-gray-600">Average Price</div>
                      <div className="text-xl font-bold text-gray-900">{result.averagePrice}</div>
                    </div>
                    
                    <div className="bg-gray-50 p-3 rounded-lg flex items-center justify-between">
                      <div>
                        <div className="text-sm text-gray-600">Supply Trend</div>
                        <div className="text-lg font-bold text-gray-900">{result.marketTrend}</div>
                      </div>
                      {getTrendIcon(result.marketTrend)}
                    </div>
                    
                    <div className="bg-gray-50 p-3 rounded-lg flex items-center justify-between">
                      <div>
                        <div className="text-sm text-gray-600">Price Trend</div>
                        <div className="text-lg font-bold text-gray-900">{result.priceTrend}</div>
                      </div>
                      {getTrendIcon(result.priceTrend.startsWith('+') ? 'Increasing' : result.priceTrend.startsWith('-') ? 'Decreasing' : 'Stable')}
                    </div>
                  </div>
                </div>
              </div>

              {/* Recommendation */}
              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-blue-900 font-medium">{result.recommendation}</p>
              </div>

              {/* Detailed Signals */}
              <div className="mt-6 grid md:grid-cols-3 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="h-4 w-4 text-blue-600" />
                    <span className="text-sm font-medium text-gray-700">Brand Popularity</span>
                  </div>
                  <div className="text-2xl font-bold text-gray-900">{result.signals.brandPopularity}%</div>
                </div>
                
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Activity className="h-4 w-4 text-blue-600" />
                    <span className="text-sm font-medium text-gray-700">Model Popularity</span>
                  </div>
                  <div className="text-2xl font-bold text-gray-900">{result.signals.modelPopularity}%</div>
                </div>
                
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Calendar className="h-4 w-4 text-blue-600" />
                    <span className="text-sm font-medium text-gray-700">Average Age</span>
                  </div>
                  <div className="text-2xl font-bold text-gray-900">{result.signals.averageAge} yrs</div>
                </div>
              </div>

              {/* Data Freshness */}
              <div className="mt-4 text-center text-sm text-gray-500">
                Data updated: {result.metadata.dataFreshness}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </section>
  )
}
