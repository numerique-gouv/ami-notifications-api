import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { render, screen } from '@testing-library/svelte';
import { userStore } from '$lib/state/User.svelte';
import LogoutFooter from './LogoutFooter.svelte';

describe('/LogoutFooter.svelte', () => {
  test('should call userStore.logout', async () => {
    // Given
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('', { status: 200 }));
    const spyLogout = vi.spyOn(userStore, 'logout').mockResolvedValue();
    const onClose = vi.fn();

    // When
    render(LogoutFooter, { props: { onClose } });
    const confirmButton = screen.getByTestId('logout-submit-button');
    await confirmButton.click();

    // Then
    expect(spyLogout).toHaveBeenCalled();
  });

  test('should not call userStore.logout if cancel button is clicked', async () => {
    // Given
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('', { status: 200 }));
    const spyLogout = vi.spyOn(userStore, 'logout').mockResolvedValue();
    const onClose = vi.fn();

    // When
    render(LogoutFooter, { props: { onClose } });
    const cancelButton = screen.getByTestId('logout-cancel-button');
    await cancelButton.click();

    // Then
    expect(spyLogout).not.toHaveBeenCalled();
    expect(onClose).toHaveBeenCalled();
  });
});
