"use client"

import React from "react"
import { cn } from "@/lib/utils"

type CircularDemandMeterProps = {
  value: number // 0 - 100 (can be decimal)
  size?: number // in px
  className?: string
}

export default function CircularDemandMeter({ value, size = 260, className }: CircularDemandMeterProps) {
  // Handle the demand index values properly - ensure we get the right scale
  const normalizedValue = React.useMemo(() => {
    if (value === null || value === undefined || isNaN(value)) {
      return 0
    }
    
    // If value is already in 0-100 range, use it directly
    if (value >= 0 && value <= 100) {
      return Math.round(value * 100) / 100 // Round to 2 decimal places
    }
    
    // If value is in 0-1 range, convert to percentage
    if (value >= 0 && value <= 1) {
      return Math.round(value * 100 * 100) / 100
    }
    
    // Clamp any other values to 0-100 range
    return Math.max(0, Math.min(100, Math.round(value * 100) / 100))
  }, [value])

  const [animated, setAnimated] = React.useState(0)

  React.useEffect(() => {
    const start = animated
    const end = normalizedValue
    const duration = 800
    const startTime = performance.now()
    let raf = 0
    
    const tick = (t: number) => {
      const progress = Math.min(1, (t - startTime) / duration)
      const eased = 1 - Math.pow(1 - progress, 3) // easeOutCubic
      const current = start + (end - start) * eased
      setAnimated(current)
      
      if (progress < 1) {
        raf = requestAnimationFrame(tick)
      }
    }
    
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [normalizedValue])

  const width = size
  const height = Math.round(size * 0.6)
  const cx = width / 2
  const cy = size * 0.55
  const r = size * 0.42
  const arcPath = `M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`

  const angle = (-180 + (animated / 100) * 180) * (Math.PI / 180)
  const nx = cx + r * Math.cos(angle)
  const ny = cy + r * Math.sin(angle)

  const displayValue = Math.round(animated * 10) / 10 // Round to 1 decimal place for display
  const bandColor = animated < 35 ? "stroke-slate-500" : animated < 70 ? "stroke-blue-600" : "stroke-emerald-500"
  const textColor = animated < 35 ? "text-slate-600" : animated < 70 ? "text-blue-600" : "text-emerald-600"
  
  const label = React.useMemo(() => {
    if (animated === 0) return "No Data"
    if (animated < 35) return "Low"
    if (animated < 70) return "Medium"
    return "High"
  }, [animated])

  return (
    <div className={cn("w-full flex flex-col items-center", className)} aria-label="Demand index meter">
      <svg
        width={width}
        height={height + 20}
        viewBox={`0 0 ${width} ${height + 20}`}
        role="img"
        aria-labelledby="demand-meter-title"
      >
        <title id="demand-meter-title">{`Demand Meter: ${displayValue}% (${label})`}</title>

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

        {/* Ticks at 0..100 every 20 for cleaner look */}
        {[0, 20, 40, 60, 80, 100].map((tickValue) => {
          const ang = (-180 + (tickValue / 100) * 180) * (Math.PI / 180)
          const ix1 = cx + (r - 8) * Math.cos(ang)
          const iy1 = cy + (r - 8) * Math.sin(ang)
          const ix2 = cx + (r + 2) * Math.cos(ang)
          const iy2 = cy + (r + 2) * Math.sin(ang)
          return (
            <line
              key={tickValue}
              x1={ix1}
              y1={iy1}
              x2={ix2}
              y2={iy2}
              className="stroke-slate-300"
              strokeWidth={tickValue % 50 === 0 ? 2 : 1}
              strokeLinecap="round"
            />
          )
        })}

        {/* Tick labels */}
        {[0, 50, 100].map((labelValue) => {
          const ang = (-180 + (labelValue / 100) * 180) * (Math.PI / 180)
          const lx = cx + (r + 15) * Math.cos(ang)
          const ly = cy + (r + 15) * Math.sin(ang)
          return (
            <text
              key={labelValue}
              x={lx}
              y={ly}
              textAnchor="middle"
              dominantBaseline="middle"
              className="text-xs fill-slate-400"
              fontSize="10"
            >
              {labelValue}
            </text>
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
          style={{ 
            transition: "x2 0.8s cubic-bezier(0.2, 0.8, 0.2, 1), y2 0.8s cubic-bezier(0.2, 0.8, 0.2, 1)" 
          }}
        />
        <circle cx={cx} cy={cy} r={6} className="fill-slate-900" />
      </svg>

      <div className="mt-2 text-center">
        <div className={cn("text-4xl font-semibold tracking-tight", textColor)}>
          {displayValue}%
        </div>
        <div className="text-sm text-slate-600">{label} Demand</div>
        {animated === 0 && (
          <div className="text-xs text-slate-500 mt-1">
            No matching data found
          </div>
        )}
      </div>
    </div>
  )
}