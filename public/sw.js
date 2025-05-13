// Register event listener for the 'push' event.
self.addEventListener('push', (event) => {
    console.log('received push event:', event)
    if (!(self.Notification && self.Notification.permission === 'granted')) {
        console.log('no permission to display notification')
        return
    }

    console.log('data:', event.data)
    const title = 'Remote notification'
    const message = event.data?.text() ?? 'Default notification message'

    // Keep the service worker alive until the notification is created.
    event.waitUntil(
        self.registration.showNotification(title, {
            body: message,
        })
    )
})

self.addEventListener('notificationclick', (event) => {
    console.log('On notification click: ', event.notification.tag)
    event.notification.close()

    // This looks to see if the current is already open and focuses if it is
    event.waitUntil(
        clients
            .matchAll({
                type: 'window',
            })
            .then((clientList) => {
                for (const client of clientList) {
                    if (client.url === '/' && 'focus' in client) return client.focus()
                }
                if (clients.openWindow) return clients.openWindow('/')
            })
    )
})
