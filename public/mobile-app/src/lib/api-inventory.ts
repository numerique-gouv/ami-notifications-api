import { apiFetch } from '$lib/auth'

export type Status = 'new' | 'wip' | 'closed'

export type InventoryItem = {
  external_id: string
  kind: string
  status_id: Status
  status_label: string
  milestone_start_date: Date | null
  milestone_end_date: Date | null

  title: string
  description: string

  created_at: Date
  updated_at: Date
}

const fetchAndStoreInventory = async () => {
  let items = [] as InventoryItem[]

  try {
    const response = await apiFetch('/data/follow-up/inventories', {
      credentials: 'include',
    })
    if (response.status === 200) {
      const result = await response.json()
      items = result.psl.items
      localStorage.setItem('inventory', JSON.stringify(items))
    }
  } catch (error) {
    console.error(error)
  }

  return items
}

const getInventoryFromStore = async (): Promise<InventoryItem[]> => {
  let items = [] as InventoryItem[]

  const itemsString: string = localStorage.getItem('inventory') || ''
  if (itemsString != null) {
    items = JSON.parse(itemsString)
  }

  items.forEach((item) => {
    // convert dates
    item.created_at = new Date(item.created_at)
    item.updated_at = new Date(item.updated_at)
    item.milestone_start_date = item.milestone_start_date
      ? new Date(item.milestone_start_date)
      : null
    item.milestone_end_date = item.milestone_end_date
      ? new Date(item.milestone_end_date)
      : null
  })

  return items
}

export const retrieveInventory = async (): Promise<InventoryItem[]> => {
  await fetchAndStoreInventory()
  return await getInventoryFromStore()
}
