import { describe, expect, test } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { buildCheckList } from '$lib/checklist';

describe('/checklist.ts', () => {
  test('should build checklist from JSON', async () => {
    const checklist = await buildCheckList('F3109');
    expect(checklist.title).toEqual('Je crée une association');
    expect(checklist.sections.length).toEqual(2);
    expect(checklist.items.length).toEqual(14);
    expect(checklist.items[0].text).toEqual(
      "**Choisir le nom** de l'association : vérifier que le nom est disponible, éventuellement protéger le nom"
    );
    expect(checklist.items[0].links[0].url).toEqual(
      'https://www.service-public.gouv.fr/particuliers/vosdroits/F31494'
    );

    expect(checklist.hasSections()).toBe(true);
    const sectionId = checklist.sections[0].id;
    expect(checklist.getItemsForSection(sectionId).length).toEqual(7);

    const itemId = checklist.items[0].id;
    const item = checklist.getItemById(itemId);
    expect(item.links.length).toEqual(2);
    expect(item.links[0].url).toEqual(
      'https://www.service-public.gouv.fr/particuliers/vosdroits/F31494'
    );
  });

  test('should mark items as un/checked', async () => {
    const checklist = await buildCheckList('F3109');
    const itemId = checklist.items[0].id;
    const item = checklist.getItemById(itemId);
    expect(item.checked).toBe(false);
    item.markAs(true);
    expect(item.checked).toBe(true);
    item.markAs(false);
    expect(item.checked).toBe(false);
  });

  test('should have url attributes', async () => {
    const checklist = await buildCheckList('F3109');
    const sectionId = checklist.sections[0].id;
    const section = checklist.getSectionById(sectionId);
    const itemId = checklist.items[0].id;
    const item = checklist.getItemById(itemId);
    expect(checklist.url).toEqual('/#/checklist/F3109/');
    expect(section.url).toEqual(`/#/checklist/F3109/checks/${sectionId}/`);
    expect(item.url).toEqual(`/#/checklist/F3109/checks/${sectionId}/item/${itemId}/`);
  });
});
