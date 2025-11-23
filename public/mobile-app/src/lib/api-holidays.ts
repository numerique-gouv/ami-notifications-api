import { PUBLIC_API_URL } from '$env/static/public'

export type Holiday = {
  description: string
  zones: string
  start_date: Date
  end_date: Date
  emoji: string
}

export const dayName = (date) => {
  return date.toLocaleDateString('fr-FR', { weekday: 'short' }).replace('.', '')
}

const capitalizeFirstLetter = (val) => {
  return String(val).charAt(0).toUpperCase() + String(val).slice(1)
}

export const monthName = (date) => {
  return capitalizeFirstLetter(date.toLocaleDateString('fr-FR', { month: 'long' }))
}

export const holidayPeriod = (startDate, endDate) => {
  const locale = 'fr-FR'
  let startFormat = { year: 'numeric', month: 'long', day: 'numeric' }
  let endFormat = startFormat
  if (startDate.getYear() == endDate.getYear()) {
    startFormat = { month: 'long', day: 'numeric' }
    if (startDate.getMonth() == endDate.getMonth()) {
      startFormat = { day: 'numeric' }
    }
  }
  const start = startDate.toLocaleDateString(locale, startFormat)
  const end = endDate.toLocaleDateString(locale, endFormat)
  return `Du ${start} au ${end}`
}

export const retrieveHolidays = async (date) => {
  var today = date || new Date()
  today.setHours(0, 0, 0, 0)
  const current_date = today.toLocaleDateString('sv-SE') // this gives the locale date in ISO format ...
  const oneday_in_ms = 24 * 60 * 60 * 1000
  try {
    const response = await fetch(
      `${PUBLIC_API_URL}/data/holidays?current_date=${current_date}`,
      {
        credentials: 'include',
      }
    )
    const result = {
      now: [] as Holiday[],
      next: [] as Holiday[],
    }
    if (response.status === 200) {
      let holidays = (await response.json()) as Holiday[]
      holidays.forEach((holiday) => {
        // convert dates
        holiday.start_date = new Date(holiday.start_date)
        holiday.end_date = new Date(holiday.end_date)
        // sort holidays
        if (
          holiday.start_date <= today ||
          holiday.start_date < new Date(today.getTime() + 30 * oneday_in_ms)
        ) {
          result.now.push(holiday)
        } else {
          result.next.push(holiday)
        }
      })
    }
    return result
  } catch (error) {
    console.error(error)
  }
}
