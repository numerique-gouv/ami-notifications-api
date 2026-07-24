import { render, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import * as AMIGotoMethods from '$lib/ami-goto';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  test('should redirect to new page', async () => {
    // Given
    const spy = vi
      .spyOn(AMIGotoMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('/#/welcome/notifications', false, {
        replaceState: true,
      });
    });
  });
});
