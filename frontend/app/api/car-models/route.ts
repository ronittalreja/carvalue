import { NextResponse } from "next/server"

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const company = searchParams.get("company")
    if (!company) return NextResponse.json({ models: [] })

    const base = new URL(request.url)
    base.pathname = "https://carvalue.onrender.com/companies"
    base.search = ""
    const res = await fetch(base.toString(), { cache: "no-store" })
    const data = await res.json()
    const allModels = data.models || {}
    const models = (allModels[company] as string[] | undefined) || []
    return NextResponse.json({ models })
  } catch (e) {
    console.error(e)
    return NextResponse.json({ models: [] })
  }
}
