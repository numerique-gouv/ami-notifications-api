import * as Sentry from '@sentry/sveltekit';
import { env } from '$env/dynamic/public';
import { checkAccessKey } from '$lib/access-key';

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
    integrations: [
      Sentry.browserTracingIntegration(),
      Sentry.elementTimingIntegration(),
    ],
    tracesSampleRate: parseFloat(env.PUBLIC_FRONT_SENTRY_TRACES_SAMPLE_RATE),
  });
  actualHandleError = Sentry.handleErrorWithSentry();
} else {
  actualHandleError = null;
}

export const handleError = actualHandleError;

export const init = async () => {
  await checkAccessKey();
};
