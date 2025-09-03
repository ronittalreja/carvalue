import type { SavedItem } from "./types"

const KEY = "car-valuation:saved"

export function readSaved(): SavedItem[] {
  if (typeof window === "undefined") return []
  try {
    const raw = window.localStorage.getItem(KEY)
    return raw ? (JSON.parse(raw) as SavedItem[]) : []
  } catch {
    return []
  }
}

export function writeSaved(items: SavedItem[]) {
  if (typeof window === "undefined") return
  window.localStorage.setItem(KEY, JSON.stringify(items))
}

export function upsertSaved(item: SavedItem) {
  const list = readSaved()
  const idx = list.findIndex((i) => i.id === item.id)
  if (idx >= 0) list[idx] = item
  else list.unshift(item)
  writeSaved(list)
}

export function removeSaved(id: string) {
  writeSaved(readSaved().filter((i) => i.id !== id))
}
