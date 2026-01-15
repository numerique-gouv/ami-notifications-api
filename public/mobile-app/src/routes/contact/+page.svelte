<script lang="ts">
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'
  import { PUBLIC_CONTACT_URL } from '$env/static/public'
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte'
  import { toastStore } from '$lib/state/toast.svelte'
  import { userStore } from '$lib/state/User.svelte'

  let userFcHash: string | null = null
  const contactUrl = PUBLIC_CONTACT_URL

  onMount(async () => {
    if (!userStore.connected) {
      goto('/')
    }
    userFcHash = localStorage.getItem('user_fc_hash')
  })

  const copyIdentificationCode = () => {
    if (userFcHash) {
      navigator.clipboard.writeText(userFcHash)
      toastStore.addToast("Code d'identification copié !", 'neutral')
    }
  }
</script>

<div class="contact-page">
  <NavWithBackButton title="Nous contacter" />

  <div class="contact-page-wrapper">
    <div class="image-wrapper">
      <img
        class="contact-icon"
        src="/icons/community.svg"
        alt="Icône de la page de contact"
      >
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
          title="Copier le code d'identification"
          aria-label="Copier le code d'identification"
          data-testid="copy-button"
        >
          <img
            class="copy-icon"
            src="/remixicons/file-copy-line.svg"
            alt="Icône de copie"
          >
        </button>
      </div>
    </div>

    <div class="contact-link-wrapper">
      <a
        href="{contactUrl}"
        title="Contacter notre équipe"
        aria-label="Contacter notre équipe"
      >
        Contacter notre équipe
      </a>
    </div>
  </div>
</div>

<style>
  .contact-page {
    .contact-page-wrapper {
      padding: 0 1rem;
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
          background-color: #ececfe;
          font-weight: 500;
        }
        .button-wrapper {
          padding-left: 12px;
          .copy-button {
            padding: 0;
          }
        }
      }

      .contact-link-wrapper {
        height: 3rem;
        background-color: var(--text-action-high-blue-france);
        color: var(--text-inverted-blue-france);

        a {
          display: flex;
          justify-content: center;
          align-items: center;
          width: 100%;
          height: 100%;
          text-decoration: none;
          --underline-img: none;
        }
      }
    }
  }
</style>
