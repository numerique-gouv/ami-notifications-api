<div class="skeleton">
  {#each Array(7).keys() as i}
    <div
      class="notification-line fr-tile fr-tile--sm fr-tile--horizontal fr-tile--no-border fr-tile--no-icon fr-enlarge-button fr-p-3v"
    >
      <div class="icon"></div>
      <div class="content">
        <div class="line1"></div>
        <div class="line2"></div>
      </div>
    </div>
  {/each}
</div>

<style>
  .skeleton {
    .notification-line {
      display: flex;
      padding: 0.75rem 0;
      border-bottom: 1px solid #dddddd;
      .icon {
        margin: 0 1rem 0 1rem;
        height: 1.5rem;
        width: 1.5rem;
        border-radius: 100%;
        background: #e3e3fd;
      }
      .content {
        flex: 1;
      }
      .line1 {
        background: #ececfe;
        width: 100%;
        height: 1rem;
        margin-bottom: 0.875rem;
      }
      .line2 {
        background: #ececfe;
        width: 65%;
        height: 1rem;
      }
    }
  }
</style>
