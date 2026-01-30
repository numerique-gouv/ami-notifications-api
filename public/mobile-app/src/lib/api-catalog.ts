import { apiFetch } from '$lib/auth'

export type CatalogItem = {
  kind: string
  title: string
  description: string
  date: Date | null
  start_date: Date | null
  end_date: Date | null
  zones: string
  emoji: string
}

export type Catalog = {
  school_holidays: CatalogItem[]
  public_holidays: CatalogItem[]
  elections: CatalogItem[]
}

export const retrieveCatalog = async (date: Date | null = null): Promise<Catalog> => {
  const today = date || new Date()
  today.setHours(0, 0, 0, 0)
  const current_date = today.toLocaleDateString('sv-SE') // this gives the locale date in ISO format ...
  const catalogData = {
    school_holidays: localStorage.getItem('school_holidays_catalog') || '{}',
    public_holidays: localStorage.getItem('public_holidays_catalog') || '{}',
    elections: localStorage.getItem('elections_catalog') || '{}',
  }
  type CatalogKey = keyof typeof catalogData
  let refresh = false
  for (const value of Object.values(catalogData)) {
    try {
      const data = JSON.parse(value)
      if (!data || data.status !== 'success') {
        refresh = true
        break
      }
    } catch {
      refresh = true
      break
    }
  }
  if (refresh) {
    const response = await apiFetch(`/data/agenda/items?current_date=${current_date}`, {
      credentials: 'include',
    })
    if (response.ok) {
      const catalog = await response.json()
      for (const key of Object.keys(catalogData) as CatalogKey[]) {
        let old_data = null
        try {
          old_data = JSON.parse(catalogData[key])
        } catch {}
        if (old_data && old_data.status === 'success') {
          // already loaded, ignore
          continue
        }
        // store result, even if status is 'failed'
        const new_data = JSON.stringify(catalog[key])
        catalogData[key] = new_data
        localStorage.setItem(`${key}_catalog`, new_data)
      }
    }
  }
  const catalog = {
    school_holidays:
      JSON.parse(catalogData.school_holidays).items || ([] as CatalogItem[]),
    public_holidays:
      JSON.parse(catalogData.public_holidays).items || ([] as CatalogItem[]),
    elections: JSON.parse(catalogData.elections).items || ([] as CatalogItem[]),
  } as Catalog
  for (const items of Object.values(catalog)) {
    items.forEach((item) => {
      // convert dates
      item.date = item.date ? new Date(item.date) : null
      item.start_date = item.start_date ? new Date(item.start_date) : null
      item.end_date = item.end_date ? new Date(item.end_date) : null
    })
  }
  return catalog
}
