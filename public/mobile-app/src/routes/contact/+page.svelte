<script lang="ts">
  import { onMount } from 'svelte';
  import { PUBLIC_CONTACT_EMAIL, PUBLIC_CONTACT_URL } from '$env/static/public';
  import { AMIGoto } from '$lib/ami-navigation';
  import BottomModal from '$lib/components/modal/BottomModal.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import { getPlatform, getVersion } from '$lib/nativeInfos';
  import { toastStore } from '$lib/state/toast.svelte';
  import { userStore } from '$lib/state/User.svelte';

  let backUrl: string = '/#/help-center';
  let userFcHash: string | null = null;
  const contactUrl = PUBLIC_CONTACT_URL;
  const contactEmail = PUBLIC_CONTACT_EMAIL;
  let platform = getPlatform();
  let version = getVersion();

  onMount(async () => {
    if (!userStore.connected) {
      userFcHash = '<absent>';
    } else {
      userFcHash = localStorage.getItem('user_fc_hash');
    }
  });

  let contactUsModal = $state(false);
  const openContactUsModal = () => {
    contactUsModal = true;
  };
  const closeContactUsModal = () => {
    contactUsModal = false;
  };
</script>

<div class="fr-container contact-page">
  <NavWithBackButton title="Nous contacter" {backUrl} />

  <div class="contact-page-wrapper fr-pt-14w">
    <div class="image-wrapper">
      <img class="contact-icon" src="/icons/community.svg" alt="">
    </div>

    <p>
      Une <b>question</b>, une <b>suggestion</b> ou un <b>problème technique</b>&nbsp;?
      Nous sommes là pour vous écouter et pour vous aider.
    </p>

    <div class="contact-us-wrapper fr-btns-group">
      <button
        id="contact-us-button"
        class="fr-btn"
        onclick={openContactUsModal}
        data-testid="contact-us-button"
      >
        Contacter notre équipe
      </button>
    </div>

    {#if contactUsModal}
      <BottomModal onClose={closeContactUsModal}>
        {#snippet modalContent()}
          <div class="fr-sidemenu">
            <ul class="fr-sidemenu__list contact-us-links">
              <li>
                <button
                  type="button"
                  class="fr-sidemenu__link fr-text--regular fr-icon-edit-fill"
                  onclick={() => AMIGoto(contactUrl)}
                  data-testid="contact-us-link-url"
                >
                  Faire une demande en ligne
                </button>
              </li>
              <li>
                <button
                  type="button"
                  class="fr-sidemenu__link fr-text--regular fr-icon-mail-fill"
                  onclick={() => window.location.href = "mailto:" + contactEmail}
                  data-testid="contact-us-link-email"
                >
                  Envoyer un mail
                </button>
              </li>
            </ul>
            {#if platform && version}
              <p class="fr-m-4v am-text-mention-grey" data-testid="native-infos">
                {getPlatform()} - {getVersion()}
              </p>
            {/if}
          </div>
        {/snippet}
      </BottomModal>
    {/if}
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
      ul.contact-us-links {
        button {
          color: var(--text-default-grey);
          &:before {
            margin-right: 0.5rem;
            color: var(--text-action-high-blue-france);
          }
        }
      }
    }
    .fr-sidemenu {
      box-shadow: none;
    }
  }
</style>
