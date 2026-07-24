<script lang="ts">
  import { AMIGoto } from '$lib/ami-goto';
  import ItemModal from '$lib/components/modal/ItemModal.svelte';
  import { type ServicesItem as ServicesItemType } from '$lib/services';

  interface Props {
    item: ServicesItemType | null;
  }
  let { item = $bindable() }: Props = $props();

  const closeModal = () => {
    item = null;
  };

  const goToService = async (item: ServicesItemType | null) => {
    if (item) {
      const url = await item.getServiceUrl();
      AMIGoto(url, item.with_silent_login);
    }
  };

  const goToFollowup = () => {
    AMIGoto('/#/followup');
  };
</script>

<ItemModal onClose={closeModal} centered={true}>
  {#snippet header()}
    <h4 class="services-item-modal-header" data-testid="services-item-modal-header">
      Que voulez-vous faire&nbsp;?
    </h4>
    <p>Vous avez commencé ou réalisé une ou plusieurs {item?.title}</p>
  {/snippet}
  {#snippet footer()}
    <div class="service-action-buttons">
      <button
        class="fr-btn fr-btn--lg"
        type="button"
        onclick={goToFollowup}
        data-testid="followup-button"
      >
        Voir les démarches en cours
      </button>
      <button
        class="fr-btn fr-btn--lg fr-btn--tertiary"
        type="button"
        onclick={() => goToService(item)}
        data-testid="service-button"
      >
        Faire une nouvelle démarche
      </button>
    </div>
  {/snippet}
</ItemModal>

<style>
  .service-action-buttons {
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
