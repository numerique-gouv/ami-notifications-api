import { apiFetch } from '$lib/auth';

export type InventoryItem = {
  partner_id: string;
  external_item_type: string;
  external_item_id: string;
  status_id: string;
  status_label: string;
  milestone_start_date: Date | null;
  milestone_end_date: Date | null;

  title: string;
  description: string;
  icon: string;
  external_url: string | null;
  is_archived: boolean;

  created_at: Date;
  updated_at: Date;
};

export type Inventory = {
  notifications: InventoryItem[];
};

export const retrieveInventory = async (
  date: Date | null = null
): Promise<Inventory> => {
  const now = new Date(date || '');
  const filter_items = [];
  const inventoryData = {
    notifications: localStorage.getItem('notifications_inventory') || '{}',
  };
  type InventoryKey = keyof typeof inventoryData;
  for (const key of Object.keys(inventoryData) as InventoryKey[]) {
    try {
      const data = JSON.parse(inventoryData[key]);
      if (!data || data.status !== 'success') {
        filter_items.push(key);
        continue;
      }
      if (!data.expires_at) {
        filter_items.push(key);
        continue;
      }
      const expires_at = new Date(data.expires_at);
      if (expires_at < now) {
        filter_items.push(key);
      }
    } catch {
      filter_items.push(key);
    }
  }
  if (filter_items.length) {
    const items = (filter_items || []).map((e) => `filter-items=${e}`).join('&');
    const response = await apiFetch(`/api/v1/users/follow-up/inventories?${items}`, {
      credentials: 'include',
    });
    if (response.ok) {
      const inventory = await response.json();
      for (const key of Object.keys(inventoryData) as InventoryKey[]) {
        if (!filter_items.includes(key)) {
          continue;
        }
        // store result if status is 'success'
        if (inventory[key].status === 'success') {
          const new_data = JSON.stringify(inventory[key]);
          inventoryData[key] = new_data;
          localStorage.setItem(`${key}_inventory`, new_data);
        }
      }
    }
  }
  const inventory = {
    notifications:
      JSON.parse(inventoryData.notifications).items || ([] as InventoryItem[]),
  } as Inventory;
  for (const items of Object.values(inventory)) {
    items.forEach((item) => {
      // convert dates
      item.created_at = new Date(item.created_at);
      item.updated_at = new Date(item.updated_at);
      item.milestone_start_date = item.milestone_start_date
        ? new Date(item.milestone_start_date)
        : null;
      item.milestone_end_date = item.milestone_end_date
        ? new Date(item.milestone_end_date)
        : null;
    });
  }
  return inventory;
};

export const archiveInventoryItem = async (
  inventory: string,
  external_id: string
): Promise<boolean> => {
  try {
    const payload = {
      is_archived: true,
    };
    const headers = {
      'Content-Type': 'application/json',
    };
    const response = await apiFetch(
      `/api/v1/users/follow-up/item/${inventory}/${external_id}/archive`,
      {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
        credentials: 'include',
      }
    );
    if (response.status === 200) {
      return true;
    }
  } catch (error) {
    console.error(error);
  }
  return false;
};
