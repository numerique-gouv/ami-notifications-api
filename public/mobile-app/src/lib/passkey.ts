import type {
  AuthenticationResponseJSON,
  RegistrationResponseJSON,
} from '@simplewebauthn/browser';
import { startAuthentication, startRegistration } from '@simplewebauthn/browser';
import { apiFetch } from '$lib/auth';
import type { UserIdentity } from '$lib/state/User.svelte';
import { userStore } from '$lib/state/User.svelte';
import * as telemetry from '$lib/telemetry';

export class PasskeyError extends Error {}
export class PasskeyBreakingError extends Error {}
export class PasskeyNetworkError extends Error {}

export const registerPasskey = async () => {
  if (!userStore.connected) {
    return;
  }
  const identity: UserIdentity = userStore.connected.identity;
  const display_name = `${identity.given_name} ${identity.preferred_username || identity.family_name}`;
  let optionsResp: Response;
  telemetry.info('Generating passkey');
  try {
    optionsResp = await apiFetch('/api/v1/fi/passkey/generate-registration-options', {
      method: 'POST',
      body: JSON.stringify({ displayName: display_name }),
      headers: { 'Content-Type': 'application/json' },
    });
    if (!optionsResp.ok) {
      telemetry.error('Error generating passkey', {
        error: '!options resp.ok',
      });
      throw new PasskeyError();
    }
  } catch (error) {
    console.log('ERROR', `${error}`);
    if (error instanceof TypeError) {
      telemetry.error('Error generating passkey', {
        error: 'network error',
      });
      throw new PasskeyNetworkError();
    } else if (error instanceof PasskeyError) {
      throw error;
    } else {
      telemetry.error('Error generating passkey', {
        error: `${error}`,
      });
      throw new PasskeyError();
    }
  }

  let attResp: RegistrationResponseJSON;
  try {
    const opts = await optionsResp.json();

    console.log('Registration Options', JSON.stringify(opts, null, 2));

    attResp = await startRegistration({ optionsJSON: opts });
    console.log('Registration Response', JSON.stringify(attResp, null, 2));
  } catch (error) {
    telemetry.error('Error generating passkey', { error: `${error}` });
    console.log('ERROR', `${error}`);
    throw new PasskeyError();
  }

  let verificationResp: Response;
  try {
    verificationResp = await apiFetch('/api/v1/fi/passkey/verify-registration', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(attResp),
    });
    if (!verificationResp.ok) {
      telemetry.error('Error generating passkey', {
        error: '!verification resp.ok',
      });
      throw new PasskeyError();
    }
  } catch (error) {
    console.log('ERROR', `${error}`);
    if (error instanceof TypeError) {
      telemetry.error('Error generating passkey', {
        error: 'network error',
      });
      throw new PasskeyNetworkError();
    } else if (error instanceof PasskeyError) {
      throw error;
    } else {
      telemetry.error('Error generating passkey', {
        error: `${error}`,
      });
      throw new PasskeyError();
    }
  }

  const verificationJSON = await verificationResp.json();
  console.log('Server Response', JSON.stringify(verificationJSON, null, 2));

  if (verificationJSON?.verified) {
    console.log('Authenticator registered!');
  } else {
    telemetry.error('Error generating passkey', {
      error: '!verified',
    });
    console.log(
      `Oh no, something went wrong! Response: ${JSON.stringify(verificationJSON)}`
    );
    throw new PasskeyError();
  }
};

export const authenticateWithPasskey = async (): Promise<string> => {
  let optionsResp: Response;
  telemetry.info('Authenticating with passkey');
  try {
    optionsResp = await fetch('/api/v1/fi/passkey/generate-authentication-options');
    if (!optionsResp.ok) {
      throw new PasskeyError();
    }
  } catch (error) {
    console.log('ERROR', `${error}`);
    if (error instanceof TypeError) {
      throw new PasskeyNetworkError();
    } else if (error instanceof PasskeyError) {
      throw error;
    } else {
      throw new PasskeyError();
    }
  }

  let attResp: AuthenticationResponseJSON;
  try {
    const opts = await optionsResp.json();

    console.log('Authentication Options', JSON.stringify(opts, null, 2));
    attResp = await startAuthentication({ optionsJSON: opts });
    console.log('Authentication Response', JSON.stringify(attResp, null, 2));
  } catch (error) {
    telemetry.error('Error using passkey authentication', {
      error: `${error}`,
    });
    console.log('ERROR', `${error}`);
    throw new PasskeyError();
  }

  let verificationResp: Response;
  try {
    verificationResp = await apiFetch('/api/v1/fi/passkey/verify-authentication', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(attResp),
    });
    if (!verificationResp.ok) {
      if (verificationResp.status === 400) {
        const verificationJSON = await verificationResp.json();
        if (verificationJSON.retry === true) {
          // 400 errors without retry are FISession errors
          telemetry.warn('Non-fatal error verifiying passkey authentication');
          throw new PasskeyError();
        }
        telemetry.error('Error using passkey authentication', {
          error: 'breakingPasskeyError',
        });
        throw new PasskeyBreakingError();
      }
      telemetry.error('Error using passkey authentication', {
        error: 'passkeyError',
      });
      throw new PasskeyError();
    }
  } catch (error) {
    console.log('ERROR', `${error}`);
    if (error instanceof TypeError) {
      telemetry.error('Error using passkey authentication', {
        error: 'network error',
      });
      throw new PasskeyNetworkError();
    } else if (error instanceof PasskeyError || error instanceof PasskeyBreakingError) {
      throw error;
    } else {
      telemetry.error('Error using passkey authentication', {
        error: `${error}`,
      });
      throw new PasskeyError();
    }
  }

  const verificationJSON = await verificationResp.json();
  console.log('Server Response', JSON.stringify(verificationJSON, null, 2));

  if (verificationJSON?.verified) {
    console.log('User authenticated!');
    return verificationJSON?.redirect_uri;
  } else {
    telemetry.error('Error using passkey authentication', {
      error: '!verified',
    });
    console.log(
      `Oh no, something went wrong! Response: ${JSON.stringify(verificationJSON)}`
    );
    throw new PasskeyError();
  }
};

type PasskeyStatus = {
  has_passkey: boolean;
};

export const getPasskeyStatus = async (): Promise<PasskeyStatus> => {
  const response = await apiFetch('/api/v1/fi/passkey/status');
  if (response.ok) {
    return await response.json();
  } else {
    return { has_passkey: false };
  }
};
