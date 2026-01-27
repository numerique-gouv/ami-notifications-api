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
