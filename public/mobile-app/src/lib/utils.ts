export const formatDate = (data: string | Date) => {
  let date: Date
  if (typeof data === 'string') {
    date = new Date(data)
  } else {
    date = data
  }
  const options: Intl.DateTimeFormatOptions = {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }
  return date.toLocaleDateString('fr-FR', options)
}

export const scrollToInput = (event: FocusEvent & { currentTarget: HTMLElement }) => {
  const input = event.currentTarget
  const nav = document.querySelector('nav')
  if (!nav) {
    return
  }
  const inputOffsetTop =
    input.getBoundingClientRect().top -
    nav.getBoundingClientRect().bottom +
    (document.scrollingElement?.scrollTop || 0) -
    5 // Just a small margin to avoid cutting the top of the input
  window.scrollTo({ top: inputOffsetTop, behavior: 'smooth' })
}
