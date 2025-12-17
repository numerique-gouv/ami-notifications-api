import type { Holiday } from '$lib/api-holidays'
import { retrieveHolidays } from '$lib/api-holidays'
import { userStore } from '$lib/state/User.svelte'

type Kind = 'holiday' | 'otv'

const capitalizeFirstLetter = (val: string) => {
  return String(val).charAt(0).toUpperCase() + String(val).slice(1)
}

export const monthName = (date: Date) => {
  return capitalizeFirstLetter(date.toLocaleDateString('fr-FR', { month: 'long' }))
}

const oneday_in_ms = 24 * 60 * 60 * 1000

export class Item {
  constructor(
    private _kind: Kind,
    private _title: string,
    private _description: string | null,
    private _date: Date | null = null,
    private _start_date: Date | null = null,
    private _end_date: Date | null = null,
    private _custom: boolean = false
  ) {}

  equals(other: Item): boolean {
    if (!(other instanceof Item)) {
      return false
    }
    return Object.entries(this).every(([key, thisValue]) => {
      const otherValue = other[key as keyof Item]
      // Special handling for Date objects
      if (thisValue instanceof Date || otherValue instanceof Date) {
        return (
          (thisValue as Date | null)?.getTime() ===
          (otherValue as Date | null)?.getTime()
        )
      }
      return thisValue === otherValue
    })
  }

  get title(): string {
    return this._title
  }

  get description(): string | null {
    return this._description
  }

  get date(): Date | null {
    return this._start_date || this._date
  }

  get dayName(): string | null {
    return this.date
      ? this.date.toLocaleDateString('fr-FR', { weekday: 'short' }).replace('.', '')
      : null
  }

  get dayNum(): number | null {
    return this.date ? this.date.getDate() : null
  }

  get monthName(): string | null {
    return this.date ? monthName(this.date) : null
  }

  get period(): string | undefined {
    const locale = 'fr-FR'
    let startFormat: Intl.DateTimeFormatOptions = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    }
    const dateFormat: Intl.DateTimeFormatOptions = startFormat
    if (this._start_date) {
      const start = this._start_date.toLocaleDateString(locale, startFormat)
      if (this._end_date) {
        const endFormat = startFormat
        if (this._start_date.getFullYear() === this._end_date.getFullYear()) {
          startFormat = { month: 'long', day: 'numeric' }
          if (this._start_date.getMonth() === this._end_date.getMonth()) {
            startFormat = { day: 'numeric' }
          }
        }
        const start = this._start_date.toLocaleDateString(locale, startFormat)
        const end = this._end_date.toLocaleDateString(locale, endFormat)
        return `Du ${start} au ${end}`
      }
      return `À partir du ${start}`
    }
    const date = this._date?.toLocaleDateString(locale, dateFormat)
    return date
  }

  private static readonly KindInfo: Record<
    Kind,
    { label: string; icon: string; link: string }
  > = {
    holiday: {
      label: 'Vacances et jours fériés',
      icon: 'fr-icon-calendar-event-fill',
      link: '',
    },
    otv: {
      label: 'Logement',
      icon: 'fr-icon-home-4-fill',
      link: '/#/procedure',
    },
  }

  get kind(): Kind {
    return this._kind
  }

  get custom(): boolean {
    return this._custom
  }

  get label(): string {
    const info = Item.KindInfo[this._kind]
    if (info === undefined) {
      return ''
    }
    return info.label
  }

  get icon(): string {
    const info = Item.KindInfo[this._kind]
    if (info === undefined) {
      return ''
    }
    return info.icon
  }

  get link(): string {
    const info = Item.KindInfo[this._kind]
    if (info === undefined) {
      return ''
    }
    return info.link
  }
}

export class Agenda {
  private _now: Item[] = []
  private _next: Item[] = []

  constructor(holidays: Holiday[], date: Date | null = null) {
    const today = date || new Date()
    today.setHours(0, 0, 0, 0)
    const items: Item[] = []

    // build items from holidays
    this.createHolidayItems(items, holidays, today)

    // create OTV items
    this.createOTVItems(items, holidays, today)

    // sort items by date
    items.sort((a, b) => (a.date?.getTime() || 0) - (b.date?.getTime() || 0))

    // organize items in _now or _next arrays
    items.forEach((item) => {
      if (
        item.date &&
        (item.date <= today ||
          item.date < new Date(today.getTime() + 30 * oneday_in_ms))
      ) {
        this._now.push(item)
      } else {
        this._next.push(item)
      }
    })
  }

  private createHolidayItems(items: Item[], holidays: Holiday[], date: Date) {
    holidays.forEach((holiday) => {
      const item = this.createHolidayItem(holiday, date)
      if (item !== null) {
        items.push(item)
      }
    })
  }

  private createHolidayItem(holiday: Holiday, date: Date): Item | null {
    const userZone = userStore.connected?.identity.address?.zone
    if (holiday.end_date < date) {
      // exclude past holidays
      return null
    }
    let title = holiday.description
    if (holiday.zones) {
      title += ` ${holiday.zones}`
    }
    if (holiday.emoji) {
      title += ` ${holiday.emoji}`
    }
    let custom = false
    let description = null
    if (
      userZone !== undefined &&
      (holiday.zones === `Zone ${userZone}` || holiday.zones === '')
    ) {
      custom = true
      description = `${userStore.connected?.identity.address?.city} 🏠`
    }
    return new Item(
      'holiday',
      title,
      description,
      null,
      holiday.start_date,
      holiday.end_date,
      custom
    )
  }

  private createOTVItems(items: Item[], holidays: Holiday[], date: Date) {
    const seenHolidays: Set<string> = new Set()
    holidays.forEach((holiday) => {
      const item = this.createOTVItem(seenHolidays, holiday, date)
      if (item !== null) {
        items.push(item)
      }
    })
  }

  private createOTVItem(
    seenHolidays: Set<string>,
    holiday: Holiday,
    date: Date
  ): Item | null {
    const userZone = userStore.connected?.identity.address?.zone
    const key = JSON.stringify({
      desc: holiday.description,
      year: holiday.start_date.getFullYear(),
    })
    if (seenHolidays.has(key)) {
      return null
    }
    if (
      userZone !== undefined &&
      holiday.zones !== '' &&
      holiday.zones !== `Zone ${userZone}`
    ) {
      // Only create OTV for the user's zone, if present
      return null
    }
    seenHolidays.add(key)
    if (holiday.end_date < date) {
      // exclude OTV of past holidays
      return null
    }
    return new Item(
      'otv',
      'Opération Tranquillité Vacances 🏠',
      'Inscrivez-vous pour protéger votre domicile pendant votre absence',
      null,
      new Date(holiday.start_date.getTime() - 3 * 7 * oneday_in_ms),
      null,
      false
    )
  }

  get now(): Item[] {
    return this._now
  }

  get next(): Item[] {
    return this._next
  }
}

export const buildAgenda = async (date: Date | null = null): Promise<Agenda> => {
  const today = date || new Date()
  const holidays: Holiday[] = await retrieveHolidays(today)
  return new Agenda(holidays, today)
}
