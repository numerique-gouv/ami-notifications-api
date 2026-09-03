import { render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test } from 'vitest';
import { buildCheckList } from '$lib/checklist';
import { userStore } from '$lib/state/User.svelte';
import { mockUserInfo } from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  test('load checklist', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const params = { checklist_id: 'F3109' };
    const checklist = await buildCheckList(params.checklist_id);

    // When
    render(Page, { props: { params: params } });

    // Then
    await waitFor(() => {
      expect(screen.getByText('Je crée une association')).toBeInTheDocument();
    });

    const section_id = checklist.sections[0].id;
    expect(
      screen.queryByTestId(`service-steps-checklist-section-${section_id}`)
    ).not.toBeNull();
  });

  test('checklist counter zero', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const params = { checklist_id: 'F3109' };

    // When
    render(Page, { props: { params: params } });

    // Then
    await waitFor(() => {
      expect(screen.getByText('Je crée une association')).toBeInTheDocument();
      expect(screen.queryAllByText('0/7').length).toEqual(2);
    });
  });

  test('checklist counter checked', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const params = { checklist_id: 'F3109' };
    const checklist = await buildCheckList(params.checklist_id);
    const item = checklist.items[0];
    item.markAs(true);

    // When
    render(Page, { props: { params: params } });

    // Then
    await waitFor(() => {
      expect(screen.getByText('Je crée une association')).toBeInTheDocument();
      expect(screen.queryAllByText('0/7').length).toEqual(1);
      expect(screen.queryAllByText('1/7').length).toEqual(1);
    });
  });
});
