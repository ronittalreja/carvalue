import Link from "next/link"
import Image from "next/image"
import { Button } from "@/components/ui/button"

export default function HomePage() {
  return (
    <section className="relative overflow-hidden">
      <div className="mx-auto max-w-6xl px-4 h-[calc(100vh-64px)] grid md:grid-cols-2 gap-10 items-center">
        <div className="space-y-6">
          <p className="inline-flex rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
            Trusted estimates, fast
          </p>
          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-gray-900 leading-[1.05]">
            Find your car’s true resale value
          </h1>
          <p className="text-gray-600 text-lg md:text-xl">
            Fast, data‑backed estimates tailored to your model and year. Compare, track trends, and save predictions.
          </p>
          <div className="flex items-center gap-3">
            <Button asChild className="bg-blue-600 hover:bg-blue-700 text-white px-6">
              <Link href="/predict">Find your car estimate</Link>
            </Button>
          </div>

          <div className="grid grid-cols-3 gap-4 pt-2">
            <Button variant="outline" asChild>
              <Link href="/demand">Demand Index</Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href="/compare">Compare cars</Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href="/about">About Us</Link>
            </Button>
           
          </div>
        </div>

        <div className="w-full">
          <div className="rounded-2xl overflow-hidden shadow-xl ring-1 ring-black/5">
            <Image
              src="/images/hero-car.png"
              alt="Silver sedan studio photo"
              width={1200}
              height={900}
              priority
              className="w-full h-auto"
            />
          </div>
        </div>
      </div>
    </section>
  )
}

function Feature({ title }: { title: string }) {
  return (
    <div className="rounded-xl border bg-white p-4 shadow-sm">
      <p className="text-sm text-gray-800 font-medium">{title}</p>
    </div>
  )
}
