import { describe, expect, test } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { render } from '@testing-library/svelte';
import { toastStore } from '$lib/state/toast.svelte';
import Toasts from './Toasts.svelte';

describe('/Toasts.svelte', () => {
  test('should display toasts', () => {
    // Given
    toastStore.toasts = [];
    toastStore.addToast("Code d'identification copié !", 'info', 5000, true);
    toastStore.addToast('Information bien enregistrée !', 'success', 5000, false);
    toastStore.addToast('Les notifications ont été activées', 'success', null, false);

    // When
    const { container } = render(Toasts);

    // Then
    const toasts = container.querySelector('.toasts');
    expect(toasts).toHaveTextContent("Code d'identification copié !");
    expect(toasts).toHaveTextContent('Information bien enregistrée !');
    expect(toasts).toHaveTextContent('Les notifications ont été activées');
  });
});
