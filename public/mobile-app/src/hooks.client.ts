import * as Sentry from '@sentry/sveltekit';
import { env } from '$env/dynamic/public';

let actualHandleError = null;

if (env.PUBLIC_FRONT_SENTRY_DSN) {
  console.log('init Sentry');
  Sentry.init({
    dsn: env.PUBLIC_FRONT_SENTRY_DSN,
    environment: env.PUBLIC_FRONT_SENTRY_ENV,
    dataCollection: {
      userInfo: false,
      httpBodies: [],
    },
  });
  actualHandleError = Sentry.handleErrorWithSentry();
} else {
  actualHandleError = null;
}

export const handleError = actualHandleError;
