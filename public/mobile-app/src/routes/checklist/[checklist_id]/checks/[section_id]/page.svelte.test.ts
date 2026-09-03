import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test } from 'vitest';
import { buildCheckList } from '$lib/checklist';
import { userStore } from '$lib/state/User.svelte';
import { mockUserInfo } from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  test('load checklist section', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const checklist = await buildCheckList('F3109');
    const params = { checklist_id: 'F3109', section_id: checklist.sections[0].id };

    // When
    render(Page, { props: { params: params } });

    // Then
    await waitFor(() => {
      expect(document.querySelector('.title')).toHaveTextContent('Cas général');
    });

    expect(document.querySelectorAll('li').length).toEqual(7);
  });

  test('checklist section mark checked', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const checklist = await buildCheckList('F3109');
    const params = { checklist_id: 'F3109', section_id: checklist.sections[0].id };
    const item = checklist.items[0];

    // When
    render(Page, { props: { params: params } });
    await waitFor(() => {
      expect(document.querySelector('.title')).toHaveTextContent('Cas général');
    });

    const checkbox = screen.getByTestId(`checkbox-${item.id}`);
    await fireEvent.click(checkbox);

    // Then
    expect(item.checked).toBe(true);

    await fireEvent.click(checkbox);
    expect(item.checked).toBe(false);
  });
});
