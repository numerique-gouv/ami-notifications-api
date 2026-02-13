import type { RequestEvent } from '@sveltejs/kit'

export const handleError = async ({
  error,
  event,
}: {
  error: any
  event: RequestEvent
}) => {
  console.error('Error: ', error.stack, event.url.hash)
  console.error(error)
  console.error(event)
}
