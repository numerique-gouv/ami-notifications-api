import { beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { fireEvent, render } from '@testing-library/svelte';
import { createRawSnippet } from 'svelte';
import * as AMINavigationMethods from '$lib/ami-navigation';
import AMILink from './AMILink.svelte';

describe('/AMILink.svelte', () => {
  beforeEach(async () => {
    vi.resetAllMocks();
  });

  test('should render all attributes', () => {
    // Given
    const children = createRawSnippet(() => ({
      render: () => '<span>Voir le lien</span>',
    }));

    // When
    const { container, getByTestId } = render(AMILink, {
      props: {
        children,
        url: '/',
        class: 'fr-link',
        'data-testid': 'link',
        'aria-label': 'Voir',
      },
    });

    // Then
    expect(container).toHaveTextContent('Voir le lien');
    const link = getByTestId('link');
    expect(link).toHaveTextContent('Voir le lien');
    expect(link).toHaveClass('fr-link');
    expect(link).toHaveAttribute('aria-label', 'Voir');
    expect(link.tagName).toBe('A');
  });

  test('should call AMILink', () => {
    // Given
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIUrl')
      .mockReturnValue('another-link');
    const children = createRawSnippet(() => ({
      render: () => '<span>Voir le lien</span>',
    }));

    // When
    const { getByTestId } = render(AMILink, {
      props: {
        children,
        url: 'a-link',
        'data-testid': 'link',
      },
    });

    // Then
    const link = getByTestId('link');
    expect(link).toHaveAttribute('href', 'another-link');
    expect(spy).toHaveBeenCalledTimes(1);
    expect(spy).toHaveBeenCalledWith('a-link', false);
  });

  test('should call AMILink - silentLogin is false', () => {
    // Given
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIUrl')
      .mockReturnValue('another-link');
    const children = createRawSnippet(() => ({
      render: () => '<span>Voir le lien</span>',
    }));

    // When
    const { getByTestId } = render(AMILink, {
      props: {
        children,
        silentLogin: false,
        url: 'a-link',
        'data-testid': 'link',
      },
    });

    // Then
    const link = getByTestId('link');
    expect(link).toHaveAttribute('href', 'another-link');
    expect(spy).toHaveBeenCalledTimes(1);
    expect(spy).toHaveBeenCalledWith('a-link', false);
  });

  test('should call AMILink - silentLogin is true', () => {
    // Given
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIUrl')
      .mockReturnValue('another-link');
    const children = createRawSnippet(() => ({
      render: () => '<span>Voir le lien</span>',
    }));

    // When
    const { getByTestId } = render(AMILink, {
      props: {
        children,
        silentLogin: true,
        url: 'a-link',
        'data-testid': 'link',
      },
    });

    // Then
    const link = getByTestId('link');
    expect(link).toHaveAttribute('href', 'another-link');
    expect(spy).toHaveBeenCalledTimes(1);
    expect(spy).toHaveBeenCalledWith('a-link', true);
  });

  test('should call AMIGoto if internal link', async () => {
    // Given
    const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();
    const children = createRawSnippet(() => ({
      render: () => '<span>Voir le lien</span>',
    }));

    const { getByTestId } = render(AMILink, {
      props: {
        children,
        url: '/internal-link',
        'data-testid': 'link',
      },
    });

    // When
    const link = getByTestId('link');
    await fireEvent.click(link, { button: 0 });

    // Then
    expect(spy).toHaveBeenCalledTimes(1);
    expect(spy).toHaveBeenCalledWith('/internal-link');
  });

  test('should call AMIGoto for external link', async () => {
    // Given
    const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();
    const children = createRawSnippet(() => ({
      render: () => '<span>Voir le lien</span>',
    }));

    const { getByTestId } = render(AMILink, {
      props: {
        children,
        url: 'external-link',
        'data-testid': 'link',
      },
    });

    // When
    const link = getByTestId('link');
    await fireEvent.click(link, { button: 0 });

    // Then
    expect(spy).toHaveBeenCalledTimes(1);
    expect(spy).toHaveBeenCalledWith('external-link');
  });

  test('should not call AMIGoto for empty link', async () => {
    // Given
    const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();
    const children = createRawSnippet(() => ({
      render: () => '<span>Voir le lien</span>',
    }));

    const { getByTestId } = render(AMILink, {
      props: {
        children,
        url: '',
        'data-testid': 'link',
      },
    });

    // When
    const link = getByTestId('link');
    await fireEvent.click(link, { button: 0 });

    // Then
    expect(spy).not.toHaveBeenCalled();
  });

  test.each([
    ['metaKey', { metaKey: true }],
    ['ctrlKey', { ctrlKey: true }],
    ['shiftKey', { shiftKey: true }],
    ['altKey', { altKey: true }],
    ['middle click', { button: 1 }],
  ])('should not call AMIGoto if %s is used', async (_label, eventInit) => {
    // Given
    const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();
    const children = createRawSnippet(() => ({
      render: () => '<span>Voir le lien</span>',
    }));

    const { getByTestId } = render(AMILink, {
      props: {
        children,
        url: 'external-link',
        'data-testid': 'link',
      },
    });

    // When
    const link = getByTestId('link');
    await fireEvent.click(link, { button: 0, ...eventInit });

    // Then
    expect(spy).not.toHaveBeenCalled();
  });

  test('should call custom onclick if provided', async () => {
    // Given
    const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();
    const onClick = vi.fn();
    const children = createRawSnippet(() => ({
      render: () => `<span>Voir le lien</span>`,
    }));

    const { getByTestId } = render(AMILink, {
      props: {
        children,
        url: '/internal-link',
        'data-testid': 'link',
        onclick: onClick,
      },
    });

    // When
    const link = getByTestId('link');
    await fireEvent.click(link, { button: 0 });

    // Then
    expect(onClick).toHaveBeenCalledTimes(1);
    expect(spy).toHaveBeenCalledTimes(1);
    expect(spy).toHaveBeenCalledWith('/internal-link');
  });

  test('should not call AMIGoto if custom onclick calls preventDefault', async () => {
    // Given
    const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();
    const children = createRawSnippet(() => ({
      render: () => `<span>Voir le lien</span>`,
    }));

    const { getByTestId } = render(AMILink, {
      props: {
        children,
        url: '/internal-link',
        'data-testid': 'link',
        onclick: (e) => {
          e.preventDefault();
        },
      },
    });

    // When
    const link = getByTestId('link');
    await fireEvent.click(link, { button: 0 });

    // Then
    expect(spy).not.toHaveBeenCalled();
  });
});
