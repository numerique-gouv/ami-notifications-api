<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import Navigation from '$lib/components/Navigation.svelte';
  import RequestItem from '$lib/components/RequestItem.svelte';
  import type { FollowUp } from '$lib/follow-up';
  import { buildFollowUp } from '$lib/follow-up';
  import { userStore } from '$lib/state/User.svelte';

  let followUp: FollowUp | null = $state(null);

  onMount(async () => {
    if (!userStore.connected) {
      goto('/');
    }

    followUp = await buildFollowUp();
    console.log($state.snapshot(followUp));
  });
</script>

<div class="requests">
  <div class="requests--title">
    <h2>Mes démarches</h2>
    <div class="requests--title--icon">
      <span class="fr-icon-search-line" aria-hidden="true"></span>
    </div>
  </div>

  <div class="requests--container" data-testid="requests">
    {#if followUp && followUp.items.length}
      {#each followUp.items as item}
        <RequestItem item={item} />
      {/each}
    {:else}
      <div class="no-requests">
        <div class="no-requests--icon">
          <img
            class="requests-icon"
            src="/remixicons/tracking.svg"
            alt="Icône de suivi"
          >
        </div>
        <div class="no-requests--title">
          Après avoir effectué vos démarches, vous pouvez les suivre en temps réel
          depuis l’application.
        </div>
      </div>
    {/if}
  </div>
</div>
<Navigation currentItem="requests" />

<style>
  .requests {
    padding: 1.5rem 1rem;
    margin-bottom: 68px;
    .requests--title {
      display: flex;
      h2 {
        flex-grow: 1;
      }
      .requests--title--icon {
        padding-top: 0.25rem;
        color: var(--text-active-blue-france);
      }
    }
    .requests--container {
      display: flex;
      flex-direction: column;
      &:has(div.no-requests) {
        align-items: center;
        justify-content: center;
        height: calc(100vh - 15rem);
        min-height: 10rem;
      }
      .no-requests {
        flex-direction: column;
        text-align: center;
        padding: 1rem;
        display: flex;
        font-size: 16px;
        line-height: 24px;
        color: var(--grey-0-1000);
        img {
          height: 5rem;
          width: 5rem;
        }
        .no-requests--title {
          text-align: left;
        }
      }
    }
  }
</style>
