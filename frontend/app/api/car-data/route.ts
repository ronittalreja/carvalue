import { NextResponse } from "next/server"

// CSV with columns: name,company,year,Price,kms_driven,fuel_type
// const CSV_URL = new URL('../../backend/cars24.csv', import.meta.url)


export async function GET() {
  try {
    const res = await fetch(CSV_URL, { cache: "no-store" })
    const text = await res.text()
    const lines = text.trim().split("\n")
    const header = lines[0].split(",")
    const companyIdx = header.indexOf("company")
    const nameIdx = header.indexOf("name")

    const companiesSet = new Set<string>()
    const modelMap: Record<string, Set<string>> = {}

    for (let i = 1; i < lines.length; i++) {
      const cols = lines[i].split(",")
      const company = cols[companyIdx]?.trim()
      const name = cols[nameIdx]?.trim()
      if (!company || !name) continue
      companiesSet.add(company)
      if (!modelMap[company]) modelMap[company] = new Set()
      modelMap[company].add(name)
    }

    const companies = Array.from(companiesSet).sort()
    return NextResponse.json({
      companies,
      models: Object.fromEntries(Object.entries(modelMap).map(([k, v]) => [k, Array.from(v)])),
    })
  } catch (e) {
    console.error(e)
    return NextResponse.json({ companies: [] })
  }
}
