import { fireEvent, render, screen } from '@testing-library/svelte';
import { createRawSnippet } from 'svelte';
import { describe, expect, test, vi } from 'vitest';
import * as AMINavigationMethods from '$lib/ami-navigation';
import { expectBackButtonPresent } from '$tests/utils';
import Page from './NavWithBackButton.svelte';

describe('/NavWithBackButton.svelte', () => {
  test('should render a Back button', async () => {
    // When
    render(Page);

    // Then
    expectBackButtonPresent(screen);
  });

  test('should render the title if provided in the props', async () => {
    // When
    render(Page, { title: 'some title', backUrl: '/foobar' });

    // Then
    expect(screen.getByText('some title')).toBeInTheDocument();
  });
  test('should render the title and the children if any are present', async () => {
    // Given
    const childSnippet = createRawSnippet(() => ({
      render: () => `<span data-testid="child-content">Child content</span>`,
    }));

    // When
    render(Page, { title: 'some title', backUrl: '/foobar', children: childSnippet });

    // Then
    expect(screen.getByText('some title')).toBeInTheDocument();
    expect(screen.getByTestId('child-content')).toBeInTheDocument();
  });
  test('should only render the children if no title and children are present', async () => {
    // Given
    const childSnippet = createRawSnippet(() => ({
      render: () => `<span data-testid="child-content">Child content</span>`,
    }));

    // When
    render(Page, { backUrl: '/foobar', children: childSnippet });

    // Then
    expect(screen.queryByText('some title')).toBeNull();
    expect(screen.getByTestId('child-content')).toBeInTheDocument();
  });
  test('should navigate to previous page when user clicks on Back button', async () => {
    // Given
    const backSpy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());

    // When
    render(Page, { backUrl: '/foobar' });
    const backButton = screen.getByTestId('back-button');
    await fireEvent.click(backButton);

    // Then
    expect(backSpy).toHaveBeenCalledTimes(1);
    expect(backSpy).toHaveBeenCalledWith('/foobar');
    backSpy.mockRestore();
  });
});
