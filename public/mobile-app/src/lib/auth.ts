import { userStore } from '$lib/state/User.svelte';

export const logout = async (): Promise<boolean> => {
  // delete auth cookie
  const response = await fetch('/logout', {
    method: 'POST',
  });
  if (response.status >= 400) {
    console.log(
      `logout error ${response.status}: ${response.statusText}, ${response.body}`
    );
    return false;
  }
  return true;
};

export const apiFetch = async (
  input: string,
  init?: RequestInit
): Promise<Response> => {
  let response: Response;
  if (typeof init !== 'undefined') {
    response = await fetch(input, init);
  } else {
    response = await fetch(input);
  }

  if (response.status === 401) {
    console.log(
      `apiFetch error ${response.status} for ${input} (init: ${init}): ${response.statusText}, ${response.body}`
    );
    await userStore.logout();
  }

  return response;
};
