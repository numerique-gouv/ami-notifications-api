import { render, waitFor } from '@testing-library/svelte';
import { describe, expect, test } from 'vitest';
import { buildCheckList } from '$lib/checklist';
import { userStore } from '$lib/state/User.svelte';
import { mockUserInfo } from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  test('load checklist item', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const checklist = await buildCheckList('F3109');
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
        'Choisir le nom'
      );
    });

    expect(document.querySelectorAll('li').length).toEqual(2);
  });
});
