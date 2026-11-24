<script lang="ts">
  import { buildContentPage, ContentPage, ContentSection } from '$lib/content-page';
  import { renderPageMarkdown } from '$lib/markdown';

  let sectionText: string = $state('');

  const waitForAccordionText = async () => {
    try {
      const page = await buildContentPage('custom-texts');
      const section = page.getSectionBySlug('followup');
      sectionText = section.text;
    } catch (error) {
      // default text
      sectionText = `* S’inscrire à l’opération tranquillité vacances
* Déclaration de changement d’adresse
* Demande de recensement citoyen obligatoire
* Demande d’acte de naissance, de mariage, de décès : copie intégrale ou extrait (survenu à l'étranger)
* Service gratuit
* Déclaration de changement de nom d’usage (nom de l’époux ou de l’épouse)
* Déposer une pré-demande de Pacs
* Toutes les démarches **Démarche numérique**
* Et bientôt : Demande d’acte de naissance, de mariage, de décès : copie intégrale ou extrait (survenu en France) Service gratuit, Demander en ligne
* un certificat de non-Pacs pour le partenaire étranger né à l’étranger,
  * Renouvellement de l’inscription consulaire, Inscription consulaire, Actualisation, Radiation, Demander ses certificats (inscription ou radiation) et sa carte consulaire (Registre des français à l’étranger), Demande de correction d’état civil auprès de l’Insee, Demande de publication au Journal officiel d’annonce préalable de changement de nom pour motif légitime, Renouvellement à distance de passeport en Australie, au Canada, en Espagne et au Portugal, Rendez-vous commissariat`;
    }
  };
</script>
<section class="fr-accordion fr-mt-4v">
  <h3 class="fr-accordion__title">
    <button
      type="button"
      class="fr-accordion__btn"
      aria-expanded="false"
      aria-controls="accordion-1"
    >
      <span class="fr-pr-2v">
        <span class="fr-icon-information-line" aria-hidden="true"></span>
        <span class="fr-sr-only">Information</span>
      </span>
      Quelles sont les démarches que je peux suivre&nbsp;?
    </button>
  </h3>
  <div id="accordion-1" class="fr-collapse fr-p-0">
    {#await waitForAccordionText()}
    {:then accordionTextLoaded}
      <div class="fr-m-4v" data-testid="accordion-text">
        {@html renderPageMarkdown(sectionText)}
      </div>
    {/await}
  </div>
</section>

<style>
  .fr-accordion {
    border: solid 1px var(--border-default-blue-france);
    &:before {
      box-shadow: none;
    }
    .fr-accordion__btn {
      font-size: 14px;
      font-weight: 700;
    }
  }
</style>
