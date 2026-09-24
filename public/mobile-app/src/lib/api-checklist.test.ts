import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { retrieveCheckList } from '$lib/api-checklist';

const checklistData = {
  icon: 'icon',
  definition: {
    title: 'Je deviens parent',
    description:
      'Nous vous présentons par ordre chronologique les démarches à effectuer pendant la grossesse, puis de la naissance jusqu’aux 3 ans de l’enfant.',
    sections: [
      {
        title: 'Pendant la grossesse',
        id: 'pendant-la-grossesse',
      },
    ],
    items: [
      {
        text: '**Avant la fin du 3e mois** de grossesse : passer le **1<sup>er</sup> examen prénatal**, qui permet de faire la **déclaration de grossesse**',
        id: 'e59ab105e3f3',
        section: 'pendant-la-grossesse',
      },
    ],
  },
};

describe('/api-checklist', () => {
  describe('retrieveCheckList', () => {
    test('should get checklist from API', async () => {
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(
          new Response(JSON.stringify(checklistData), { status: 200 })
        );

      // When
      const result = await retrieveCheckList('F16225');

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith(
        '/api/v1/users/data/checklist/F16225'
      );
      expect(result).toEqual(checklistData);
    });
  });
});
