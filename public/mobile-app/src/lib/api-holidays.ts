import { apiFetch } from '$lib/auth'

export type Holiday = {
  description: string
  zones: string
  start_date: Date
  end_date: Date
  emoji: string
}

export const retrieveHolidays = async (
  date: Date | null = null
): Promise<Holiday[]> => {
  const today = date || new Date()
  today.setHours(0, 0, 0, 0)
  const current_date = today.toLocaleDateString('sv-SE') // this gives the locale date in ISO format ...
  console.log('current_date', current_date)
  let holidaysData = localStorage.getItem('holidays_data')
  if (!holidaysData) {
    const response = await apiFetch(`/data/holidays?current_date=${current_date}`, {
      credentials: 'include',
    })
    if (response.ok) {
      holidaysData = await response.text()
      localStorage.setItem('holidays_data', holidaysData)
    }
  }
  if (holidaysData) {
    const holidays = JSON.parse(holidaysData) as Holiday[]
    holidays.forEach((holiday) => {
      // convert dates
      holiday.start_date = new Date(holiday.start_date)
      holiday.end_date = new Date(holiday.end_date)
    })
    return holidays
  }
  return []
}
