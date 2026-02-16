import { render, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as navigationMethods from '$app/navigation';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  test('user has to be connected', async () => {
    // Given
    const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith('/');
    });
  });
});
