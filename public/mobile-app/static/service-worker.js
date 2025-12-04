// Register event listener for the 'push' event.
self.addEventListener('push', (event) => {
  if (!(self.Notification && self.Notification.permission === 'granted')) {
    console.log('no permission to display notification')
    return
  }

  const json_data = event.data?.json()

  // Keep the service worker alive until the notification is created.
  event.waitUntil(
    self.registration.showNotification(json_data.title, {
      body: `From ${json_data.sender}: ${json_data.message}`,
    })
  )
})

self.addEventListener('notificationclick', (event) => {
  event.notification.close()

  // This looks to see if the current is already open and focuses if it is
  event.waitUntil(
    clients
      .matchAll({
        type: 'window',
      })
      .then((clientList) => {
        for (const client of clientList) {
          if (client.url === '/' && 'focus' in client) {
            return client.focus()
          }
        }
        if (clients.openWindow) {
          return clients.openWindow('/')
        }
      })
  )
})
