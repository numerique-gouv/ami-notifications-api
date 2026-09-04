import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { beforeEach, describe, expect, test, vi } from 'vitest';
import * as AMIGotoMethods from '$lib/ami-goto';
import * as CheckListMethods from '$lib/checklist';
import { CheckList } from '$lib/checklist';
import { userStore } from '$lib/state/User.svelte';
import { mockUserInfo } from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  test('load checklist section', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const checklist = new CheckList('F3109', {
      title: 'title',
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
    vi.spyOn(CheckListMethods, 'buildCheckList').mockResolvedValue(checklist);
    const params = { checklist_id: 'F3109', section_id: checklist.sections[0].id };

    // When
    render(Page, { props: { params: params } });

    // Then
    await waitFor(() => {
      expect(document.querySelector('.title')).toHaveTextContent('section title');
    });

    expect(document.querySelectorAll('li').length).toEqual(3);
  });

  test('checklist section mark checked', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const checklist = new CheckList('F3109', {
      title: 'title',
      sections: [{ id: 'a', title: 'section title' }],
      items: [
        { id: 'b', text: 'test', section: 'a' },
        { id: 'c', text: 'test2', section: 'a' },
      ],
    });
    vi.spyOn(CheckListMethods, 'buildCheckList').mockResolvedValue(checklist);
    const params = { checklist_id: 'F3109', section_id: checklist.sections[0].id };
    const item = checklist.items[0];

    // When
    render(Page, { props: { params: params } });
    await waitFor(() => {
      expect(document.querySelector('.title')).toHaveTextContent('section title');
    });

    const checkbox = screen.getByTestId(`checkbox-${item.id}`);
    await fireEvent.click(checkbox);

    // Then
    expect(item.checked).toBe(true);

    await fireEvent.click(checkbox);
    expect(item.checked).toBe(false);
  });

  test('checklist section item page link because multiple links', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const checklist = new CheckList('F3109', {
      title: 'title',
      sections: [{ id: 'a', title: 'section title' }],
      items: [
        {
          id: 'b',
          text: 'test',
          section: 'a',
          links: [
            { text: 'link1', url: 'url1' },
            { text: 'link2', url: 'url2' },
          ],
        },
      ],
    });
    vi.spyOn(CheckListMethods, 'buildCheckList').mockResolvedValue(checklist);
    const params = { checklist_id: 'F3109', section_id: checklist.sections[0].id };
    const item = checklist.items[0];
    const spy = vi.spyOn(AMIGotoMethods, 'AMIGoto').mockResolvedValue();

    // When
    render(Page, { props: { params: params } });
    await waitFor(() => {
      expect(document.querySelector('.title')).toHaveTextContent('section title');
    });

    const linkButton = screen.getByTestId(`item-button-page-link-${item.id}`);
    await fireEvent.click(linkButton);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith(item.url);
    });
  });

  test('checklist section item page link because truncated text', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const checklist = new CheckList('F3109', {
      title: 'title',
      sections: [{ id: 'a', title: 'section title' }],
      items: [{ id: 'b', text: 'long test '.repeat(50), section: 'a' }],
    });
    vi.spyOn(CheckListMethods, 'buildCheckList').mockResolvedValue(checklist);
    const params = { checklist_id: 'F3109', section_id: 'a' };
    const spy = vi.spyOn(AMIGotoMethods, 'AMIGoto').mockResolvedValue();

    // When
    render(Page, { props: { params: params } });
    await waitFor(() => {
      expect(document.querySelector('.title')).toHaveTextContent('section title');
    });

    const linkButton = screen.getByTestId(`item-button-page-link-b`);
    await fireEvent.click(linkButton);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith('/#/checklist/F3109/checks/a/item/b/');
    });
  });

  test('checklist section item direct link', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const checklist = new CheckList('F3109', {
      title: 'title',
      sections: [{ id: 'a', title: 'section title' }],
      items: [
        {
          id: 'b',
          text: 'test',
          section: 'a',
          links: [{ text: 'link1', url: 'url1' }],
        },
      ],
    });
    vi.spyOn(CheckListMethods, 'buildCheckList').mockResolvedValue(checklist);

    const item = checklist.items.filter((x) => x.hasLinks() && x.links.length === 1)[0];
    const params = { checklist_id: 'F3109', section_id: item.section_id };
    const spy = vi.spyOn(AMIGotoMethods, 'AMIGoto').mockResolvedValue();

    // When
    render(Page, { props: { params: params } });
    await waitFor(() => {
      expect(document.querySelector('.title')).toHaveTextContent('section title');
    });

    const linkButton = screen.getByTestId(`item-button-direct-link-${item.id}`);
    await fireEvent.click(linkButton);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith(item.links[0].url);
    });
  });
});
