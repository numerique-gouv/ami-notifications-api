import type { Catalog, CatalogItem } from '$lib/api-catalog'
import { retrieveCatalog } from '$lib/api-catalog'
import { createScheduledNotification } from '$lib/scheduled-notifications'
import { userStore } from '$lib/state/User.svelte'

type Kind = 'holiday' | 'otv' | 'election'

const capitalizeFirstLetter = (val: string) => {
  return String(val).charAt(0).toUpperCase() + String(val).slice(1)
}

export const monthName = (date: Date) => {
  return capitalizeFirstLetter(date.toLocaleDateString('fr-FR', { month: 'long' }))
}

const slugify = (str: string): string => {
  return str
    .replace(/\s+/g, '-') // replace spaces with hyphens
    .replace(/-+/g, '-') // remove consecutive hyphens
    .trim() // trim leading or trailing whitespace
    .normalize('NFKD') // split accented characters into their base characters and diacritical marks
    .replace(/[\u0300-\u036f]/g, '') // remove all the accents, which happen to be all in the \u03xx UNICODE block.
    .toLowerCase() // convert to lowercase
    .replace(/[^a-z0-9 -]/g, '') // remove non-alphanumeric characters
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
      ? capitalizeFirstLetter(
          this.date.toLocaleDateString('fr-FR', { weekday: 'short' }).replace('.', '')
        )
      : null
  }

  get fullDayName(): string | null {
    return this.date
      ? capitalizeFirstLetter(
          this.date.toLocaleDateString('fr-FR', { weekday: 'long' })
        )
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
    election: {
      label: 'Élections',
      icon: 'fr-icon-chat-check-fill',
      link: '',
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

  constructor(catalog: Catalog | null = null, date: Date | null = null) {
    const today = date || new Date()
    today.setHours(0, 0, 0, 0)
    const items: Item[] = []

    const school_holidays: CatalogItem[] = catalog?.school_holidays || []
    const public_holidays: CatalogItem[] = catalog?.public_holidays || []
    const elections: CatalogItem[] = catalog?.elections || []

    // build items from school_holidays
    this.createSchoolHolidayItems(items, school_holidays, today)

    // build items from public_holidays
    this.createPublicHolidayItems(items, public_holidays, today)

    // create OTV items
    this.createOTVItems(items, school_holidays, today)

    // build items from elections
    this.createElectionItems(items, elections, today)

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

  private createSchoolHolidayItems(
    items: Item[],
    school_holidays: CatalogItem[],
    date: Date
  ) {
    school_holidays.forEach((holiday) => {
      const item = this.createSchoolHolidayItem(holiday, date)
      if (item !== null) {
        items.push(item)
      }
    })
  }

  private createSchoolHolidayItem(holiday: CatalogItem, date: Date): Item | null {
    const userZone = userStore.connected?.identity.address?.zone
    if (!holiday.start_date || !holiday.end_date) {
      // should not happen for school holiday
      return null
    }
    if (holiday.end_date < date) {
      // exclude past school holiday
      return null
    }
    let title = holiday.title
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

  private createPublicHolidayItems(
    items: Item[],
    public_holidays: CatalogItem[],
    date: Date
  ) {
    public_holidays.forEach((holiday) => {
      const item = this.createPublicHolidayItem(holiday, date)
      if (item !== null) {
        items.push(item)
      }
    })
  }

  private createPublicHolidayItem(holiday: CatalogItem, date: Date): Item | null {
    if (!holiday.date) {
      // should not happen for public holiday
      return null
    }
    if (holiday.date < date) {
      // exclude past public holiday
      return null
    }
    let title = holiday.title
    if (holiday.emoji) {
      title += ` ${holiday.emoji}`
    }
    return new Item('holiday', title, null, holiday.date, null, null, false)
  }

  private createOTVItems(items: Item[], school_holidays: CatalogItem[], date: Date) {
    const seenSchoolHolidays: Set<string> = new Set()
    school_holidays.forEach((holiday) => {
      const item = this.createOTVItem(seenSchoolHolidays, holiday, date)
      if (item !== null) {
        items.push(item)
      }
    })
  }

  private createOTVItem(
    seenSchoolHolidays: Set<string>,
    holiday: CatalogItem,
    date: Date
  ): Item | null {
    if (!holiday.start_date || !holiday.end_date) {
      // should not happen for school holiday
      return null
    }
    const userZone = userStore.connected?.identity.address?.zone
    const scheduledNotificationsCreatedKeys = new Set(
      userStore.connected?.identity.scheduledNotificationsCreatedKeys
    )
    const key = JSON.stringify({
      desc: holiday.title,
      year: holiday.start_date.getFullYear(),
    })
    if (seenSchoolHolidays.has(key)) {
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
    seenSchoolHolidays.add(key)
    if (holiday.end_date < date) {
      // exclude OTV of past school holiday
      return null
    }
    const startDate = new Date(holiday.start_date.getTime() - 3 * 7 * oneday_in_ms)
    const item = new Item(
      'otv',
      'Opération Tranquillité Vacances 🏠',
      'Inscrivez-vous pour protéger votre domicile pendant votre absence',
      null,
      startDate,
      null,
      false
    )
    if (userStore.connected) {
      const scheduledNotificationKey = `ami-otv:d-3w:${holiday.start_date.getFullYear()}:${slugify(holiday.title)}`
      if (!scheduledNotificationsCreatedKeys.has(scheduledNotificationKey)) {
        createScheduledNotification({
          content_title: 'Et si on veillait sur votre logement ? 👮',
          content_body:
            "Demandez l'Opération Tranquillité Vacances afin de partir en vacances l’esprit (plus) tranquille.",
          content_icon: 'fr-icon-megaphone-line',
          reference: scheduledNotificationKey,
          scheduled_at: startDate,
        })
        userStore.connected.addScheduledNotificationCreatedKey(scheduledNotificationKey)
      }
    }
    return item
  }

  private createElectionItems(items: Item[], elections: CatalogItem[], date: Date) {
    elections.forEach((election) => {
      const item = this.createElectionItem(election, date)
      if (item !== null) {
        items.push(item)
      }
    })
  }

  private createElectionItem(election: CatalogItem, date: Date): Item | null {
    if (!election.date) {
      // should not happen for election
      return null
    }
    if (election.date < date) {
      // exclude past election
      return null
    }
    let title = election.title
    if (election.emoji) {
      title += ` ${election.emoji}`
    }
    return new Item(
      'election',
      title,
      election.description,
      election.date,
      null,
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
  const catalog: Catalog = await retrieveCatalog(today)
  return new Agenda(catalog, today)
}
