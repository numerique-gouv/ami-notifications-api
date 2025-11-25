import { PUBLIC_API_URL } from '$env/static/public'

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
  let today = date || new Date()
  today.setHours(0, 0, 0, 0)
  const current_date = today.toLocaleDateString('sv-SE') // this gives the locale date in ISO format ...
  const oneday_in_ms = 24 * 60 * 60 * 1000
  let holidaysData = localStorage.getItem('holidays_data')
  if (!holidaysData) {
    const response = await fetch(
      `${PUBLIC_API_URL}/data/holidays?current_date=${current_date}`,
      {
        credentials: 'include',
      }
    )
    holidaysData = await response.text()
    if (response.ok) {
      localStorage.setItem('holidays_data', holidaysData)
    }
  }
  if (!!holidaysData) {
    let holidays = JSON.parse(holidaysData) as Holiday[]
    holidays.forEach((holiday) => {
      // convert dates
      holiday.start_date = new Date(holiday.start_date)
      holiday.end_date = new Date(holiday.end_date)
    })
    return holidays
  }
}
