import { describe, expect, test } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { render, screen } from '@testing-library/svelte';
import { toastStore } from '$lib/state/toast.svelte';
import Toasts from './Toasts.svelte';

describe('/Toasts.svelte', () => {
  test('should display toasts', () => {
    // Given
    toastStore.toasts = [];
    toastStore.addToast('Code d’identification copié !', 'info', 5000, true);
    toastStore.addToast('Information bien enregistrée !', 'success', 5000, false);
    toastStore.addToast('Les notifications ont été activées', 'success', null, false);

    // When
    const { container } = render(Toasts);

    // Then
    const toasts = container.querySelector('.toasts');
    expect(toasts).toHaveTextContent('Code d’identification copié !');
    expect(toasts).toHaveTextContent('Information bien enregistrée !');
    expect(toasts).toHaveTextContent('Les notifications ont été activées');
  });

  test('should display vocal messages in toasts-container-a11y', async () => {
    // Given
    toastStore.toasts = [];
    toastStore.vocalMessages = [];
    toastStore.addToast('Code d’identification copié !', 'info', 5000, true);
    toastStore.addToast('Information bien enregistrée !', 'success', 5000, false);
    toastStore.addToast('Les notifications ont été activées', 'success', null, false);

    // When
    render(Toasts);

    // Then
    const toastContainerA11y = screen.getByTestId('toasts-container-a11y');
    expect(toastContainerA11y).toHaveTextContent('Code d’identification copié !');
    expect(toastContainerA11y).toHaveTextContent('Information bien enregistrée !');
    expect(toastContainerA11y).toHaveTextContent('Les notifications ont été activées');
  });
});
