<script lang="ts">
  import { onMount } from 'svelte';
  import { PUBLIC_CURRENT_COMMIT_ID } from '$env/static/public';
  import { AMIGoto } from '$lib/ami-navigation';
  import { getPlatform, getVersion } from '$lib/bridges/nativeInfos';
  import BottomModal from '$lib/components/modal/BottomModal.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import { getContactMailToUri, getContactUrl } from '$lib/contact';
  import { toastStore } from '$lib/state/toast.svelte';
  import { userStore } from '$lib/state/User.svelte';

  let backUrl: string = '/#/help-center';
  let userFcHash: string = '';
  let userDebugFcHash: string = '';
  let platform = getPlatform();
  let version = getVersion();

  onMount(async () => {
    if (!userStore.connected) {
      userFcHash = '<non connecté>';
      userDebugFcHash = userFcHash;
    } else {
      userFcHash = localStorage.getItem('user_fc_hash') || '<error>';
      userDebugFcHash = userFcHash.substring(0, 9);
    }
  });
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
        data-fr-opened="false"
        aria-controls="contact-us-modal"
        id="contact-us-button"
        class="fr-btn"
        data-testid="contact-us-button"
      >
        Contacter notre équipe
      </button>
    </div>

    <BottomModal modalId="contact-us-modal">
      {#snippet modalContent()}
        <h2 id="contact-us-modal-title" class="fr-sr-only">Contact</h2>
        <div class="fr-sidemenu">
          <ul class="fr-sidemenu__list contact-us-links">
            <li>
              <button
                type="button"
                class="fr-sidemenu__link fr-text--regular fr-icon-edit-fill"
                onclick={() => AMIGoto(getContactUrl(userFcHash))}
                data-testid="contact-us-link-url"
              >
                Faire une demande en ligne
              </button>
            </li>
            <li>
              <button
                type="button"
                class="fr-sidemenu__link fr-text--regular fr-icon-mail-fill"
                onclick={() => window.location.href = getContactMailToUri(userFcHash)}
                data-testid="contact-us-link-email"
              >
                Envoyer un mail
              </button>
            </li>
          </ul>
        </div>
      {/snippet}
    </BottomModal>
  </div>

  <p class="fr-m-4v am-text-mention-grey debug-infos" data-testid="debug-infos">
    version :
    {#if platform && version}
      {platform} {version} ·
    {/if}
    {PUBLIC_CURRENT_COMMIT_ID}
    <br>
    {userDebugFcHash}
  </p>
</div>

<style>
  .contact-page {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    .contact-page-wrapper {
      flex: 1;
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
    .debug-infos {
      text-align: center;
    }
  }
</style>
