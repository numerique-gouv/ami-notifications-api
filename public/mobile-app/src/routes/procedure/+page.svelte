<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { Address } from '$lib/address';
  import { apiFetch } from '$lib/auth';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import { User, type UserIdentity, userStore } from '$lib/state/User.svelte';

  let backUrl: string = '/';
  let procedureUrl: string = $state('');
  let itemDate: string = $state('');

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
      try {
        const response = await apiFetch(
          `/api/v1/partner/otv/url?preferred_username=${preferredUsername}&email=${email}&address_city=${addressCity}&address_postcode=${addressPostcode}&address_name=${addressName}`,
          {
            credentials: 'include',
          }
        );
        if (response.status === 200) {
          const responseJson = await response.json();
          procedureUrl = responseJson.partner_url;
        }
      } catch (error) {
        console.error(error);
      }
    }
  };

  onMount(() => {
    if (!userStore.connected) {
      goto('/');
    }

    getProcedureUrl();

    const hash = window.location.hash;
    const url = new URL(hash.substring(1), window.location.origin);
    const stringFromUrl = url.searchParams.get('date') || '';
    itemDate = '';

    if (stringFromUrl !== '') {
      const dateFromUrl: Date = new Date(stringFromUrl);
      if (isValidDate(dateFromUrl)) {
        const dayNumber: string = dateFromUrl ? dateFromUrl.getDate().toString() : '';
        const monthName: string = dateFromUrl
          ? dateFromUrl.toLocaleString('fr-FR', { month: 'long' })
          : '';
        itemDate = `${dayNumber} ${monthName}`;
      }
    }
  });

  const redirectToLink = (procedureUrl: string) => {
    if (procedureUrl) {
      window.location.href = procedureUrl;
    }
  };

  const clickOnProcedureButton = async () => {
    const originalProcedureUrl = procedureUrl;
    procedureUrl = '';
    await getProcedureUrl();
    redirectToLink(originalProcedureUrl);
  };

  export const getProcedureUrlForTests = () => procedureUrl;
</script>

<div class="procedure">
  <div class="nav">
    <NavWithBackButton {backUrl}>
      <div class="partner-logo">
        <img src="/icons/otv-logo.svg" alt="Icône du logo du partenaire">
      </div>
      <div class="title">
        <h2>Opération Tranquillité Vacances</h2>
      </div>
    </NavWithBackButton>
  </div>

  <div class="procedure-content">
    <div class="procedure-content-block">
      <p class="title">Quand&nbsp;?</p>
      <p data-testid="item-date">À partir du {itemDate}</p>
    </div>
    <div class="procedure-content-block">
      <p class="title">Comment ça fonctionne&nbsp;?</p>
      <p>
        Pendant toute absence prolongée de votre domicile, vous pouvez vous inscrire à
        l'<b>opération tranquillité vacances</b>.
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

  <div class="procedure-action-buttons">
    <div class="procedure-start">
      <button
        class="fr-btn fr-btn--lg"
        type="button"
        onclick={clickOnProcedureButton}
        data-testid="procedure-button"
        disabled="{!procedureUrl}"
      >
        Bénéficier de ce service
      </button>
    </div>
  </div>
</div>

<style>
  .procedure {
    .nav {
      background-color: var(--green-archipel-975-75);
      border-bottom: 0.25rem solid var(--green-archipel-sun-391-moon-716);

      .partner-logo {
        display: flex;
        justify-content: center;
        margin-bottom: 0.5rem;
      }
      .title {
        display: flex;
        justify-content: center;
        h2 {
          text-align: center;
          margin-bottom: 0;
          font-size: 1.5rem;
          line-height: 2rem;
        }
      }
    }

    .procedure-content {
      padding: 1.5rem 1rem;

      .procedure-content-block {
        padding-bottom: 1rem;
        p {
          margin-bottom: 1rem;
        }
        .title {
          font-weight: 700;
        }
      }
    }

    .procedure-action-buttons {
      position: fixed;
      bottom: 1rem;
      left: 50%;
      transform: translateX(-50%);

      display: block;
      width: 328px;

      .procedure-start {
        button {
          display: flex;
          justify-content: center;
          width: 100%;
        }
      }
    }
  }
</style>
