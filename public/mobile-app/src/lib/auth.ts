import { userStore } from '$lib/state/User.svelte';

export const logout = async (): Promise<boolean> => {
  // delete auth cookie
  const response = await fetch('/logout', {
    method: 'POST',
    credentials: 'include',
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
  const response = await fetch(input, init);

  if (response.status === 401) {
    console.log(
      `apiFetch error ${response.status} for ${input} (init: ${init}): ${response.statusText}, ${response.body}`
    );
    await userStore.logout();
  }

  return response;
};
