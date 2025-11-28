# Firebase Cloud Messaging (FCM) Workflow

## Tokens or not tokens?
Several authentication artefacts are used in the workflow.

* `Service Account Key`: Contains private_key, client_email, project_id. Given when registering the app. Used by the backend to request the `Access Token`
* `Access Token` (OAuth 2.0): Short-lived JWT token obtained from Google's auth servers. Lifespan around hour, must be refreshed. Used by the backend to authentify itself when calling FCM notification API.
* Some project specific `API authentications artefects` to authentify the client app when it calls the backend.
* `FCM Registration Token` (Device Token): unique identifier for each app instance, requested by the device to FCM and given back to the backend.
    * Format: Long string like dL8Xg7... (152+ characters). 
    * Generated when app initializes Firebase SDK. A new token is thus generated when user reinstall the app for instance, and must be sent to the back-end.
    * Can be invalidated and must be refreshed.
  
# Workflow

## Mobile registration
1. **Client App** initializes Firebase SDK with config
1. **Firebase SDK** requests registration from FCM
1. **FCM** returns `FCM Registration Token`
1. **Client App** sends `FCM Registration Token` to your backend
1. **Backend** stores `FCM Registration Token` in database linked to user

## Sending Notifications (Back-end Process)
1. Load `Service Account Key`
1. Request `OAuth 2.0 Access Token` from Google
1. POST to FCM API notification payload unsing the stored `FCM Registration Token` linked to the targetted devices

## Token refresh
1. **Firebase SDK** detects `FCM Registration Token` refresh needed
1. **Firebase SDK** requests new `FCM Registration Token` from FCM
1. **FCM** returns new `FCM Registration Token`
1. **Client App** sends new `FCM Registration Token` to your backend
1. **Backend** updates (or adds) stored `FCM Registration Token` linked to the user

# General overview
![](2025-11-28%20notification%20with%20firebase.excalidraw.svg)