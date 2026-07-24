<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { PUBLIC_CONTACT_EMAIL, PUBLIC_CONTACT_URL } from '$env/static/public';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import { toastStore } from '$lib/state/toast.svelte';
  import { userStore } from '$lib/state/User.svelte';

  let backUrl: string = '/';
  let userFcHash: string | null = null;
  const contactUrl = PUBLIC_CONTACT_URL;
  const contactEmail = PUBLIC_CONTACT_EMAIL;

  onMount(async () => {
    if (!userStore.connected) {
      goto('/');
    }
    userFcHash = localStorage.getItem('user_fc_hash');
  });

  const copyIdentificationCode = () => {
    if (userFcHash) {
      navigator.clipboard.writeText(userFcHash);
      toastStore.addToast("Code d'identification copié !", 'success', 3000, false);
    }
  };
</script>

<div class="fr-container contact-page">
  <NavWithBackButton title="Nous contacter" {backUrl} />

  <div class="contact-page-wrapper">
    <div class="image-wrapper">
      <img class="contact-icon" src="/icons/community.svg" alt="">
    </div>

    <p>
      Une <b>question</b>, une <b>suggestion</b> ou un <b>problème technique</b>&nbsp;?
      Nous sommes là pour vous écouter et pour vous aider.
    </p>
    <p>
      <b>Copiez</b> et transmettez votre <b>code d'identification</b> ci-dessous pour
      <b>échanger avec nous</b> sur notre canal Tchap.
    </p>

    <div class="identification-code-wrapper">
      <p class="identification-code">{userFcHash}</p>

      <div class="button-wrapper">
        <button
          class="copy-button"
          type="button"
          onclick={copyIdentificationCode}
          aria-label="Copier le code d'identification"
          data-testid="copy-button"
        >
          <img class="copy-icon" src="/remixicons/file-copy-line.svg" alt="">
        </button>
      </div>
    </div>

    <p>Contacter notre équipe&nbsp;:</p>
    <ul
      class="fr-btns-group fr-btns-group--center fr-btns-group--equisized fr-btns-group--inline contact-links-wrapper"
    >
      <li>
        <a
          href="{contactUrl}"
          aria-label="Contacter notre équipe par tchap"
          class="fr-btn"
        >
          Par Tchap
        </a>
      </li>
      <li>
        <a
          href="mailto:{contactEmail}?body=Mon code d'identification : {userFcHash}"
          aria-label="Contacter notre équipe par e-mail"
          class="fr-btn"
        >
          Par E-mail
        </a>
      </li>
    </ul>
  </div>
</div>

<style>
  .contact-page {
    .contact-page-wrapper {
      padding-top: 7rem;
      .image-wrapper {
        display: flex;
        justify-content: center;
        margin-bottom: 1.5rem;
      }

      .identification-code-wrapper {
        display: flex;
        align-items: center;
        padding-bottom: 1.5rem;
        .identification-code {
          overflow: hidden;
          padding: 12px;
          margin: 0;
          background-color: var(--background-contrast-blue-france);
          font-weight: 500;
        }
        .button-wrapper {
          padding-left: 12px;
          .copy-button {
            padding: 0;
          }
        }
      }
    }
  }
</style>
