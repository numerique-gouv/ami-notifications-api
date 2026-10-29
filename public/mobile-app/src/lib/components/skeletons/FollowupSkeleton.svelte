<script lang="ts">
  interface Props {
    archived?: boolean;
  }
  let { archived = false }: Props = $props();
</script>
<div class="skeleton followup">
  {#if !archived}
    <div class="followup--title">
      <h1 class="fr-h2">Mes démarches</h1>
    </div>
  {:else}
    <div class="followup-archived-space"></div>
  {/if}
  <div>
    {#each Array(10).keys() as i}
      <div class="fr-card followup-item">
        <div class="tag"></div>
        <div class="date"></div>
        <div class="line"></div>
        <div class="line"></div>
        <div class="line short"></div>
      </div>
    {/each}
  </div>
</div>

<style>
  .followup {
    padding: 1.5rem 1rem;
    margin-bottom: 4.25rem;
    .followup-archived-space {
      height: 5.5rem;
    }
    .followup--title {
      display: flex;
      position: relative;
    }
  }

  .skeleton {
    .followup {
      padding: 1.5rem 1rem;
    }
    .followup-archived-space {
      padding-top: 5rem;
    }
    .followup-item {
      position: relative;
      padding: 0.875rem 1rem;
      margin-bottom: 1.5rem;
      border-bottom: 0.25rem solid var(--border-active-blue-france);
      .tag {
        background: #ececfe;
        height: 1.2rem;
        width: 50%;
      }
      .date {
        background: #f5f5fe;
        height: 0.8rem;
        width: 30%;
        position: absolute;
        top: 0.875rem;
        right: 1rem;
      }
      .line {
        background: #f5f5fe;
        margin-top: 0.5rem;
        height: 1.2rem;
        &.short {
          width: 70%;
        }
      }
    }
  }
</style>
