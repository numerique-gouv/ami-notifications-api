import { beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import * as apiCheckListMethods from '$lib/api-checklist';
import { buildCheckList } from '$lib/checklist';

const checklistData = {
  icon: 'icon',
  definition: {
    title: 'Je crée une association',
    description:
      "J'organise des activités ou je porte des projets qui m'incitent à former une association avec d'autres personnes. Que dois-je faire pour la créer ?",
    sections: [
      {
        title: 'Cas général',
        id: 'cas-general',
      },
      {
        title: 'Alsace-Moselle',
        id: 'alsace-moselle',
      },
    ],
    items: [
      {
        text: "**Choisir le nom** de l'association : vérifier que le nom est disponible, éventuellement protéger le nom",
        id: 'dca85cae1ddb',
        section: 'cas-general',
        links: [
          {
            url: 'https://www.service-public.gouv.fr/particuliers/vosdroits/F31494',
            text: "Peut-on choisir librement le nom d'une association ?",
            type: 'Fiche Question-réponse conditionnée',
          },
          {
            url: 'https://www.service-public.gouv.fr/particuliers/vosdroits/F31493',
            text: "Faut-il protéger le nom d'une association ?",
            type: 'Fiche Question-réponse conditionnée',
          },
        ],
      },
      {
        text: "**Rédiger les statuts** : définir l'objet et les règles de fonctionnement de l'association, prévoir les principales règles de gouvernance (dirigeants, assemblées, cotisations, modification des statuts, dissolution...).",
        id: 'd28f8aa279ad',
        section: 'cas-general',
        links: [
          {
            url: 'https://www.service-public.gouv.fr/particuliers/vosdroits/F1120',
            text: "Rédaction des statuts d'une association",
            type: "Fiche d'information conditionnée",
          },
        ],
      },
    ],
  },
};

describe('/checklist.ts', () => {
  beforeEach(() => {
    const spy = vi
      .spyOn(apiCheckListMethods, 'retrieveCheckList')
      .mockResolvedValue(checklistData);
  });

  test('should build checklist from JSON', async () => {
    const checklist = await buildCheckList('F3109');
    expect(checklist.title).toEqual('Je crée une association');
    expect(checklist.sections.length).toEqual(2);
    expect(checklist.items.length).toEqual(2);
    expect(checklist.items[0].text).toEqual(
      "**Choisir le nom** de l'association : vérifier que le nom est disponible, éventuellement protéger le nom"
    );
    expect(checklist.items[0].links[0].url).toEqual(
      'https://www.service-public.gouv.fr/particuliers/vosdroits/F31494'
    );

    expect(checklist.hasSections()).toBe(true);
    const sectionId = checklist.sections[0].id;
    expect(checklist.getItemsForSection(sectionId).length).toEqual(2);

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
