import { render, screen, waitFor } from '@testing-library/svelte';
import { beforeEach, describe, expect, test, vi } from 'vitest';
import * as CheckListMethods from '$lib/checklist';
import { CheckList } from '$lib/checklist';
import { userStore } from '$lib/state/User.svelte';
import { mockUserInfo } from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  test('load checklist', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const checklist = new CheckList('F3109', {
      title: 'checklist title',
      sections: [
        { id: 'a', title: 'section title' },
        { id: 'b', title: 'other title' },
      ],
      items: [
        { id: 'b', text: 'test', section: 'a' },
        { id: 'c', text: 'test2', section: 'a' },
        { id: 'd', text: 'test3', section: 'a' },
        { id: 'e', text: 'test4', section: 'b' },
      ],
    });
    const params = { checklist_id: checklist.id };
    vi.spyOn(CheckListMethods, 'buildCheckList').mockResolvedValue(checklist);

    // When
    render(Page, { props: { params: params } });

    // Then
    await waitFor(() => {
      expect(screen.getByText('checklist title')).toBeInTheDocument();
    });

    const sectionId = checklist.sections[0].id;
    expect(
      screen.queryByTestId(`sidemenu-button-checklist-section-${sectionId}`)
    ).not.toBeNull();
  });

  test('checklist counter zero', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const checklist = new CheckList('F3109', {
      title: 'checklist title',
      sections: [
        { id: 'a', title: 'section title' },
        { id: 'b', title: 'other title' },
      ],
      items: [
        { id: 'b', text: 'test', section: 'a' },
        { id: 'c', text: 'test2', section: 'a' },
        { id: 'd', text: 'test3', section: 'a' },
        { id: 'e', text: 'test4', section: 'b' },
      ],
    });
    const params = { checklist_id: 'F3109' };
    vi.spyOn(CheckListMethods, 'buildCheckList').mockResolvedValue(checklist);

    // When
    render(Page, { props: { params: params } });

    // Then
    await waitFor(() => {
      expect(screen.getByText('checklist title')).toBeInTheDocument();
      expect(screen.queryAllByText('0/3').length).toEqual(1);
      expect(screen.queryAllByText('0/1').length).toEqual(1);
    });
  });

  test('checklist counter checked', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const checklist = new CheckList('F3109', {
      title: 'checklist title',
      sections: [
        { id: 'a', title: 'section title' },
        { id: 'b', title: 'other title' },
      ],
      items: [
        { id: 'b', text: 'test', section: 'a' },
        { id: 'c', text: 'test2', section: 'a' },
        { id: 'd', text: 'test3', section: 'a' },
        { id: 'e', text: 'test4', section: 'b' },
      ],
    });
    const params = { checklist_id: 'F3109' };
    const item = checklist.items[0];
    vi.spyOn(CheckListMethods, 'buildCheckList').mockResolvedValue(checklist);

    // When
    item.markAs(true);
    render(Page, { props: { params: params } });

    // Then
    await waitFor(() => {
      expect(screen.getByText('checklist title')).toBeInTheDocument();
      expect(screen.queryAllByText('1/3').length).toEqual(1);
      expect(screen.queryAllByText('0/1').length).toEqual(1);
    });
  });
});
