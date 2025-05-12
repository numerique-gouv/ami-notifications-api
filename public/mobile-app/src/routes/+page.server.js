import { PUBLIC_NOTIFICATIONS_API_HOST } from '$env/static/public';

export async function load() {
    return { notifications_api_host: PUBLIC_NOTIFICATIONS_API_HOST }
}
