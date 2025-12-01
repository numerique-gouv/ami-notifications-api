/* The following was inspired by https://johnresig.com/blog/javascript-pretty-date/ */

// Takes an ISO time and returns a string representing how
// long ago the date represents.
export function prettyDate(data: Date | string) {
  let date
  if (typeof data === 'string') {
    date = new Date(data)
  } else {
    // We hope it's a proper Date object.
    date = data
  }

  const diff = (new Date().getTime() - date.getTime()) / 1000
  const day_diff = Math.floor(diff / 86400)
  if (isNaN(day_diff) || day_diff < 0) return

  return (
    (day_diff == 0 &&
      ((diff < 3600 && '< 1h') || (diff < 86400 && Math.floor(diff / 3600) + 'h'))) ||
    (day_diff < 31 && day_diff + 'j') ||
    (day_diff < 365 && Math.floor(day_diff / 31) + 'm') ||
    Math.floor(day_diff / 365) + 'a'
  )
}
