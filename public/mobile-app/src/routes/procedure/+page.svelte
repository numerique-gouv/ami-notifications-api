<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import {
    PUBLIC_API_URL,
    PUBLIC_FEATURE_FLAG_SILENT_FC_OTV,
  } from '$env/static/public';
  import { Address } from '$lib/address';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import PageWrapper from '$lib/components/PageWrapper.svelte';
  import { buildFollowup } from '$lib/followup';
  import { retrieveProcedureUrl } from '$lib/procedure';
  import { User, type UserIdentity, userStore } from '$lib/state/User.svelte';

  let backUrl: string = '/';
  let procedureUrl: string = $state('');
  let itemDate: string = $state('');
  let hasNonArchivedItems: boolean = $state(false);

  const isValidDate = (d: Date | number) =>
    d instanceof Date && !Number.isNaN(d.getTime());

  const getProcedureUrl = async () => {
    let connected: User | null = userStore.connected;
    if (!connected) {
      return;
    }
    let userIdentity: UserIdentity | null = connected.identity;
    if (userIdentity) {
      let preferredUsername: string = userIdentity.preferred_username
        ? userIdentity.preferred_username
        : '';
      let email: string = userIdentity.email ? userIdentity.email : '';
      let addressFromUserStore: Address | undefined = userIdentity.address;
      let addressCity = '';
      let addressPostcode = '';
      let addressName = '';
      if (addressFromUserStore) {
        addressCity = addressFromUserStore.city;
        addressPostcode = addressFromUserStore.postcode;
        addressName = addressFromUserStore.name;
      }
      procedureUrl = await retrieveProcedureUrl(
        preferredUsername,
        email,
        addressCity,
        addressPostcode,
        addressName
      );
    }
  };

  onMount(async () => {
    if (!userStore.connected) {
      goto('/');
    }

    getProcedureUrl();

    const hash = window.location.hash;
    const url = new URL(hash.substring(1), window.location.origin);
    const stringFromUrl = url.searchParams.get('date') || '';
    const dateFormat: Intl.DateTimeFormatOptions = { month: 'long', day: 'numeric' };
    const locale = 'fr-FR';
    itemDate = new Date().toLocaleDateString(locale, dateFormat);

    if (stringFromUrl !== '') {
      const dateFromUrl: Date = new Date(stringFromUrl);
      if (isValidDate(dateFromUrl)) {
        itemDate = dateFromUrl.toLocaleDateString(locale, dateFormat);
      }
    }

    const followup = await buildFollowup();
    hasNonArchivedItems = followup.hasNonArchivedItems(
      'psl',
      'OperationTranquilliteVacances'
    );
  });

  const AMIFILogin = async (procedureUrl: string) => {
    window.location.href = `${PUBLIC_API_URL}/silent-login-ami-fi?redirect_url=${encodeURIComponent(procedureUrl)}`;
  };

  const redirectToLink = (procedureUrl: string) => {
    if (procedureUrl) {
      if (PUBLIC_FEATURE_FLAG_SILENT_FC_OTV === 'true') {
        AMIFILogin(procedureUrl);
      } else {
        window.location.href = procedureUrl;
      }
    }
  };

  const clickOnProcedureButton = async () => {
    await getProcedureUrl();
    redirectToLink(procedureUrl);
  };

  const gotoFollowup = () => {
    goto('/#/followup');
  };
</script>

<PageWrapper>
  {#snippet header({ scrolled })}
    <div class="nav">
      <NavWithBackButton
        title="Opération Tranquillité Vacances"
        logo="/icons/otv-logo.svg"
        logoAlt="Icône du logo du partenaire"
        {backUrl}
        {scrolled}
      />
    </div>
  {/snippet}

  {#snippet content()}
    <div class="procedure">
      <div class="procedure-content">
        <div class="procedure-content-block">
          <p class="title">Quand&nbsp;?</p>
          <p data-testid="item-date">À partir du {itemDate}</p>
        </div>
        <div class="procedure-content-block">
          <p class="title">Comment ça fonctionne&nbsp;?</p>
          <p>
            Pendant toute absence prolongée de votre domicile, vous pouvez vous inscrire
            à l'<b>opération tranquillité vacances</b>.
          </p>
          <p>
            <b
              >Les services de police ou de gendarmerie se chargent alors de surveiller
              votre logement.</b
            >
            Des patrouilles sont organisées pour passer aux abords de votre domicile.
          </p>
          <p>
            <b>Vous serez prévenu</b> en cas d'anomalies (dégradations, cambriolage...).
          </p>
        </div>
      </div>
    </div>
  {/snippet}

  {#snippet footer()}
    <div class="procedure-action-buttons">
      {#if hasNonArchivedItems}
        <button
          class="fr-btn fr-btn--lg"
          type="button"
          onclick={gotoFollowup}
          data-testid="followup-button"
        >
          Accéder à ma démarche
        </button>
        <button
          class="fr-btn fr-btn--lg fr-btn--tertiary"
          type="button"
          onclick={clickOnProcedureButton}
          data-testid="procedure-button"
          disabled="{!procedureUrl}"
        >
          Faire une nouvelle démarche
        </button>
      {:else}
        <button
          class="fr-btn fr-btn--lg"
          type="button"
          onclick={clickOnProcedureButton}
          data-testid="procedure-button"
          disabled="{!procedureUrl}"
        >
          Bénéficier de ce service
        </button>
      {/if}
    </div>
  {/snippet}
</PageWrapper>

<style>
  .nav {
    background-color: var(--green-archipel-975-75);
    border-bottom: 0.25rem solid var(--green-archipel-sun-391-moon-716);
  }

  .procedure {
    .procedure-content {
      .procedure-content-block {
        p {
          margin-bottom: 1rem;
        }
        .title {
          font-weight: 700;
        }
      }
    }
  }

  .procedure-action-buttons {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    button {
      display: flex;
      justify-content: center;
      width: 100%;
    }
  }
</style>
