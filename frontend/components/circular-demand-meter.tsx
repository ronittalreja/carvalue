"use client"

import React from "react"
import { cn } from "@/lib/utils"

type CircularDemandMeterProps = {
  value: number // 0 - 100
  size?: number // in px
  className?: string
}

export default function CircularDemandMeter({ value, size = 260, className }: CircularDemandMeterProps) {
  const clamped = Math.max(0, Math.min(100, Math.round(value)))
  const [animated, setAnimated] = React.useState(0)

  React.useEffect(() => {
    const start = animated
    const end = clamped
    const duration = 800
    const startTime = performance.now()
    let raf = 0
    const tick = (t: number) => {
      const p = Math.min(1, (t - startTime) / duration)
      const eased = 1 - Math.pow(1 - p, 3) // easeOutCubic
      const current = Math.round(start + (end - start) * eased)
      setAnimated(current)
      if (p < 1) raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clamped])

  const width = size
  const height = Math.round(size * 0.6)
  const cx = width / 2
  const cy = size * 0.55
  const r = size * 0.42
  const arcPath = `M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`

  const angle = (-180 + (animated / 100) * 180) * (Math.PI / 180)
  const nx = cx + r * Math.cos(angle)
  const ny = cy + r * Math.sin(angle)

  const bandColor = animated < 35 ? "stroke-slate-500" : animated < 70 ? "stroke-blue-600" : "stroke-emerald-500"
  const textColor = animated < 35 ? "text-slate-600" : animated < 70 ? "text-blue-600" : "text-emerald-600"
  const label = animated < 35 ? "Low" : animated < 70 ? "Medium" : "High"

  return (
    <div className={cn("w-full flex flex-col items-center", className)} aria-label="Demand index meter">
      <svg
        width={width}
        height={height + 20}
        viewBox={`0 0 ${width} ${height + 20}`}
        role="img"
        aria-labelledby="demand-meter-title"
      >
        <title id="demand-meter-title">{`Demand Meter: ${animated}% (${label})`}</title>

        {/* Track */}
        <path
          d={arcPath}
          pathLength={100}
          className="stroke-slate-200"
          strokeWidth={12}
          fill="none"
          strokeLinecap="round"
        />

        {/* Progress */}
        <path
          d={arcPath}
          pathLength={100}
          className={cn(bandColor)}
          strokeWidth={12}
          fill="none"
          strokeLinecap="round"
          style={{
            strokeDasharray: `${animated} 100`,
            transition: "stroke-dasharray 0.8s cubic-bezier(0.2, 0.8, 0.2, 1)",
          }}
        />

        {/* Ticks at 0..100 every 10 */}
        {[...Array(11)].map((_, i) => {
          const v = i * 10
          const ang = (-180 + (v / 100) * 180) * (Math.PI / 180)
          const ix1 = cx + (r - 8) * Math.cos(ang)
          const iy1 = cy + (r - 8) * Math.sin(ang)
          const ix2 = cx + (r + 2) * Math.cos(ang)
          const iy2 = cy + (r + 2) * Math.sin(ang)
          return (
            <line
              key={i}
              x1={ix1}
              y1={iy1}
              x2={ix2}
              y2={iy2}
              className="stroke-slate-300"
              strokeWidth={i % 2 === 0 ? 2 : 1}
              strokeLinecap="round"
            />
          )
        })}

        {/* Needle and hub */}
        <line
          x1={cx}
          y1={cy}
          x2={nx}
          y2={ny}
          className="stroke-slate-900"
          strokeWidth={3}
          strokeLinecap="round"
          style={{ transition: "x2 0.8s, y2 0.8s" }}
        />
        <circle cx={cx} cy={cy} r={6} className="fill-slate-900" />
      </svg>

      <div className="mt-2 text-center">
        <div className={cn("text-4xl font-semibold tracking-tight", textColor)}>{animated}%</div>
        <div className="text-sm text-slate-600">{label} Demand</div>
      </div>
    </div>
  )
}
