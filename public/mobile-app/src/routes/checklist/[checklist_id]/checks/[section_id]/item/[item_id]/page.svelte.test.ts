import { render, waitFor } from '@testing-library/svelte';
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

  test('load checklist item', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const checklist = new CheckList('F3109', {
      title: 'title',
      sections: [{ id: 'a', title: 'section title' }],
      items: [
        {
          id: 'b',
          text: 'test item content',
          section: 'a',
          links: [
            { text: 'link1', url: 'url1' },
            { text: 'link2', url: 'url2' },
          ],
        },
      ],
    });
    vi.spyOn(CheckListMethods, 'buildCheckList').mockResolvedValue(checklist);
    const params = {
      checklist_id: 'F3109',
      section_id: checklist.sections[0].id,
      item_id: checklist.items[0].id,
    };

    // When
    render(Page, { props: { params: params } });

    // Then
    await waitFor(() => {
      expect(document.querySelector('.item-content')).toHaveTextContent(
        'test item content'
      );
    });

    expect(document.querySelectorAll('li').length).toEqual(2);
  });
});
