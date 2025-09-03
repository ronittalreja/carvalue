// app/api/predict/route.ts
import { NextResponse } from "next/server"

export async function POST(request: Request) {
  try {
    const {
      company,
      car_model,
      year,
      fuel_type,
      kms_driven,
      transmission,
      owners,
    } = await request.json()

    // Validation
    if (
      !company ||
      !car_model ||
      !year ||
      !fuel_type ||
      kms_driven === undefined ||
      !transmission ||
      owners === undefined
    ) {
      return NextResponse.json(
        { error: "Missing required fields" },
        { status: 400 }
      )
    }

    // Map ownership string to number
    const ownershipMap: Record<string, number> = {
      "1st": 1,
      "2nd": 2,
      "3rd": 3,
      "4th+": 4,
    }
    const numericOwners = ownershipMap[owners] || 1

    // FastAPI endpoint
    const endpoint = "http://127.0.0.1:8000/predict"

    // Call FastAPI
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        company,
        car_model,
        year,
        fuel_type,
        kms_driven,
        transmission,
        owners: numericOwners,
      }),
    })

    if (!res.ok) {
      throw new Error(`FastAPI error ${res.status}`)
    }

    const data = await res.json()
    return NextResponse.json({ prediction: data.prediction }) // ✅ fixed key
  } catch (e) {
    console.error(e)
    return NextResponse.json(
      { prediction: null, error: "Prediction failed" },
      { status: 500 }
    )
  }
}
