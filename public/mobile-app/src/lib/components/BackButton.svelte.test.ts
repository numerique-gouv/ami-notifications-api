import { fireEvent, render, screen } from '@testing-library/svelte';
import { describe, expect, test } from 'vitest';
import Page from './BackButton.svelte';

describe('/BackButton.svelte', () => {
  test('should navigate to previous page when user clicks on Back button', async () => {
    // When
    render(Page, { backUrl: '/foobar' });
    const backButton = screen.getByTestId('back-button');
    await fireEvent.click(backButton);

    // Then
    expect(window.location.href).toEqual('/foobar');
  });
});
